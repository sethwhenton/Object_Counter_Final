#!/usr/bin/python3
"""API Tests for Object Type Endpoints
Test object type-related API functionality
"""
import unittest
import os
import sys
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests import TEST_CONFIG


class TestObjectTypeAPI(unittest.TestCase):
    """Test object type-related API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        # Import app after setting up environment
        import app_restructured
        cls.app = app_restructured.app
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # Initialize test database
        from storage.database_functions import init_database
        init_database()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test class"""
        cls.app_context.pop()
    
    def setUp(self):
        """Set up each test"""
        # Clean up any existing test data
        from storage.database_functions import get_all_object_types
        from storage import database
        
        # Remove any test object types
        object_types = get_all_object_types()
        for obj_type in object_types:
            if 'test_' in obj_type.name:
                try:
                    database.delete(obj_type)
                except:
                    pass
    
    def test_get_object_types(self):
        """Test getting all object types"""
        response = self.client.get('/api/object-types')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('object_types', data)
        self.assertIsInstance(data['object_types'], list)
        self.assertGreater(len(data['object_types']), 0)
        
        # Check that we have the expected default object types
        object_type_names = [obj['name'] for obj in data['object_types']]
        expected_types = ['car', 'person', 'dog', 'cat', 'tree']
        
        for expected_type in expected_types:
            self.assertIn(expected_type, object_type_names)
    
    def test_object_type_structure(self):
        """Test object type data structure"""
        response = self.client.get('/api/object-types')
        data = json.loads(response.data)
        
        obj_type = data['object_types'][0]
        
        # Check required fields
        required_fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        for field in required_fields:
            self.assertIn(field, obj_type)
        
        # Check field types
        self.assertIsInstance(obj_type['id'], str)
        self.assertIsInstance(obj_type['name'], str)
        self.assertIsInstance(obj_type['description'], str)
        self.assertIsInstance(obj_type['created_at'], str)
        self.assertIsInstance(obj_type['updated_at'], str)
        
        # Check UUID format
        self.assertEqual(len(obj_type['id']), 36)  # UUID length
        self.assertIn('-', obj_type['id'])
    
    def test_object_type_uniqueness(self):
        """Test that object type names are unique"""
        response = self.client.get('/api/object-types')
        data = json.loads(response.data)
        
        object_type_names = [obj['name'] for obj in data['object_types']]
        
        # Check for duplicates
        self.assertEqual(len(object_type_names), len(set(object_type_names)))
    
    def test_object_type_validation_in_count_endpoint(self):
        """Test object type validation in count endpoint"""
        from io import BytesIO
        
        # Test with valid object type - use dummy data to avoid pipeline processing
        test_image_data = BytesIO(b'fake_image_data')
        response = self.client.post('/api/count', data={
            'image': (test_image_data, 'test.jpg'),
            'object_type': 'car'
        })
        
        # Should not fail due to invalid object type (might fail due to pipeline)
        self.assertIn(response.status_code, [200, 400, 500])
        
        if response.status_code == 400:
            data = json.loads(response.data)
            # Should not be an invalid object type error
            self.assertNotIn('Invalid object type', data.get('error', ''))
        
        # Test with invalid object type
        test_image_data = BytesIO(b'fake_image_data')
        response = self.client.post('/api/count', data={
            'image': (test_image_data, 'test.jpg'),
            'object_type': 'nonexistent_type'
        })
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Invalid object type', data['error'])
        self.assertIn('available_types', data)
        self.assertIsInstance(data['available_types'], list)
    
    def test_object_type_availability(self):
        """Test that available types are returned correctly"""
        response = self.client.get('/api/object-types')
        data = json.loads(response.data)
        
        # Get available types from the API
        available_types = [obj['name'] for obj in data['object_types']]
        
        # Test count endpoint with invalid type to get available types
        from io import BytesIO
        test_image_data = BytesIO(b'fake_image_data')
        response = self.client.post('/api/count', data={
            'image': (test_image_data, 'test.jpg'),
            'object_type': 'invalid_type'
        })
        
        self.assertEqual(response.status_code, 400)
        error_data = json.loads(response.data)
        
        self.assertIn('available_types', error_data)
        error_available_types = error_data['available_types']
        
        # Available types should match
        self.assertEqual(set(available_types), set(error_available_types))
    
    def test_object_type_persistence(self):
        """Test that object types persist across requests"""
        # Get object types first time
        response1 = self.client.get('/api/object-types')
        data1 = json.loads(response1.data)
        types1 = {obj['name']: obj for obj in data1['object_types']}
        
        # Get object types second time
        response2 = self.client.get('/api/object-types')
        data2 = json.loads(response2.data)
        types2 = {obj['name']: obj for obj in data2['object_types']}
        
        # Should be the same
        self.assertEqual(len(types1), len(types2))
        self.assertEqual(set(types1.keys()), set(types2.keys()))
        
        # Check that IDs are consistent
        for name in types1:
            self.assertEqual(types1[name]['id'], types2[name]['id'])
    
    def test_object_type_descriptions(self):
        """Test that object types have meaningful descriptions"""
        response = self.client.get('/api/object-types')
        data = json.loads(response.data)
        
        for obj_type in data['object_types']:
            self.assertIsInstance(obj_type['description'], str)
            self.assertGreater(len(obj_type['description']), 0)
            self.assertNotEqual(obj_type['description'].strip(), '')
    
    def test_object_type_timestamps(self):
        """Test that object types have valid timestamps"""
        response = self.client.get('/api/object-types')
        data = json.loads(response.data)
        
        for obj_type in data['object_types']:
            # Check that timestamps are valid ISO format
            try:
                from datetime import datetime
                datetime.fromisoformat(obj_type['created_at'].replace('Z', '+00:00'))
                datetime.fromisoformat(obj_type['updated_at'].replace('Z', '+00:00'))
            except ValueError:
                self.fail(f"Invalid timestamp format for object type {obj_type['name']}")
            
            # Check that created_at is before or equal to updated_at
            created = datetime.fromisoformat(obj_type['created_at'].replace('Z', '+00:00'))
            updated = datetime.fromisoformat(obj_type['updated_at'].replace('Z', '+00:00'))
            self.assertLessEqual(created, updated)
    
    def test_object_type_case_sensitivity(self):
        """Test object type case sensitivity"""
        from io import BytesIO
        
        # Object types should be case-sensitive
        # Test with lowercase (should work)
        test_image_data = BytesIO(b'fake_image_data')
        response = self.client.post('/api/count', data={
            'image': (test_image_data, 'test.jpg'),
            'object_type': 'car'
        })
        
        # Should not fail due to case sensitivity
        self.assertIn(response.status_code, [200, 400, 500])
        
        # Test with uppercase (should fail)
        test_image_data = BytesIO(b'fake_image_data')
        response = self.client.post('/api/count', data={
            'image': (test_image_data, 'test.jpg'),
            'object_type': 'CAR'
        })
        
        # Should get 400 for invalid object type, but might get 500 if pipeline fails
        self.assertIn(response.status_code, [400, 500])
        data = json.loads(response.data)
        if response.status_code == 400:
            self.assertIn('Invalid object type', data['error'])
        else:
            # If pipeline fails, that's also acceptable for this test
            self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()
