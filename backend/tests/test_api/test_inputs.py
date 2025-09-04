#!/usr/bin/python3
"""API Tests for Input Endpoints
Test input-related API functionality
"""
import unittest
import os
import sys
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests import TEST_CONFIG


class TestInputAPI(unittest.TestCase):
    """Test input-related API endpoints"""
    
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
        from storage.database_functions import get_all_inputs, delete_output
        from storage.database_functions import get_all_outputs
        
        # Clean up test outputs and inputs
        outputs = get_all_outputs()
        for output in outputs:
            if 'test_' in str(output.id):
                try:
                    delete_output(output.id)
                except:
                    pass
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('status', data)
        self.assertIn('database', data)
        self.assertIn('object_types', data)
        self.assertIn('pipeline_available', data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['database'], 'connected')
    
    def test_object_types_endpoint(self):
        """Test object types endpoint"""
        response = self.client.get('/api/object-types')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('object_types', data)
        self.assertIsInstance(data['object_types'], list)
        self.assertGreater(len(data['object_types']), 0)
        
        # Check structure of object type
        obj_type = data['object_types'][0]
        self.assertIn('id', obj_type)
        self.assertIn('name', obj_type)
        self.assertIn('description', obj_type)
        self.assertIn('created_at', obj_type)
        self.assertIn('updated_at', obj_type)
    
    def test_count_objects_missing_image(self):
        """Test count objects endpoint with missing image"""
        response = self.client.post('/api/count', data={
            'object_type': 'car'
        })
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('No image file provided', data['error'])
    
    def test_count_objects_missing_object_type(self):
        """Test count objects endpoint with missing object type"""
        # Use a small dummy image to avoid pipeline processing
        from io import BytesIO
        test_image_data = BytesIO(b'fake_image_data')
        
        response = self.client.post('/api/count', data={
            'image': (test_image_data, 'test.jpg')
        })
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('No object_type specified', data['error'])
    
    def test_count_objects_invalid_object_type(self):
        """Test count objects endpoint with invalid object type"""
        # Use a small dummy image to avoid pipeline processing
        from io import BytesIO
        test_image_data = BytesIO(b'fake_image_data')
        
        response = self.client.post('/api/count', data={
            'image': (test_image_data, 'test.jpg'),
            'object_type': 'invalid_type'
        })
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Invalid object type', data['error'])
        self.assertIn('available_types', data)
    
    def test_correct_prediction_missing_data(self):
        """Test correct prediction endpoint with missing data"""
        response = self.client.put('/api/correct', 
                                 data=json.dumps({}),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('JSON data required', data['error'])
    
    def test_correct_prediction_missing_result_id(self):
        """Test correct prediction endpoint with missing result_id"""
        response = self.client.put('/api/correct', 
                                 data=json.dumps({'corrected_count': 5}),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('result_id is required', data['error'])
    
    def test_correct_prediction_missing_corrected_count(self):
        """Test correct prediction endpoint with missing corrected_count"""
        response = self.client.put('/api/correct', 
                                 data=json.dumps({'result_id': 'test-id'}),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('corrected_count is required', data['error'])
    
    def test_correct_prediction_invalid_count(self):
        """Test correct prediction endpoint with invalid corrected_count"""
        response = self.client.put('/api/correct', 
                                 data=json.dumps({
                                     'result_id': 'test-id',
                                     'corrected_count': -1
                                 }),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('corrected_count must be a non-negative integer', data['error'])
    
    def test_correct_prediction_nonexistent_result(self):
        """Test correct prediction endpoint with nonexistent result"""
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        response = self.client.put('/api/correct', 
                                 data=json.dumps({
                                     'result_id': fake_uuid,
                                     'corrected_count': 5
                                 }),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_get_result_details_nonexistent(self):
        """Test get result details endpoint with nonexistent result"""
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        response = self.client.get(f'/api/results/{fake_uuid}')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_delete_result_nonexistent(self):
        """Test delete result endpoint with nonexistent result"""
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        response = self.client.delete(f'/api/results/{fake_uuid}/delete')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_swagger_documentation(self):
        """Test Swagger documentation endpoints"""
        # Test Swagger UI
        response = self.client.get('/docs')
        self.assertEqual(response.status_code, 200)
        
        # Test API spec
        response = self.client.get('/apispec.json')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('swagger', data)
        self.assertIn('info', data)
        self.assertIn('paths', data)
        self.assertEqual(data['info']['title'], 'Object Counting API')


if __name__ == '__main__':
    unittest.main()
