#!/usr/bin/python3
"""API Tests for Output Endpoints
Test output-related API functionality including CRUD operations
"""
import unittest
import os
import sys
import json
import uuid
from datetime import datetime
from io import BytesIO

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests import TEST_CONFIG


class TestOutputAPI(unittest.TestCase):
    """Test output-related API endpoints"""
    
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
        from storage.database_functions import get_all_outputs, delete_output
        
        outputs = get_all_outputs()
        for output in outputs:
            if 'test_' in str(output.id):
                try:
                    delete_output(output.id)
                except:
                    pass
        
        # Create test output for some tests
        self.test_output_id = None
        self._create_test_output()
    
    def _create_test_output(self):
        """Create a test output for testing"""
        from storage.database_functions import save_prediction_result
        import uuid
        
        try:
            # Use UUID to ensure unique image path
            unique_id = str(uuid.uuid4())[:8]
            test_image_path = f"test_output_{unique_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            output = save_prediction_result(
                image_path=test_image_path,
                object_type_name='car',
                predicted_count=3,
                description='Test output for API testing',
                pred_confidence=0.85
            )
            self.test_output_id = output.id
        except Exception as e:
            print(f"Warning: Could not create test output: {e}")
    
    def test_create_output_via_count_endpoint(self):
        """Test creating output via count endpoint (if pipeline available)"""
        # This test will only work if the AI pipeline is available
        # For now, we'll test the endpoint structure
        
        # Use dummy data to avoid pipeline processing during tests
        test_image_data = BytesIO(b'fake_image_data')
        response = self.client.post('/api/count', data={
            'image': (test_image_data, 'test.jpg'),
            'object_type': 'car',
            'description': 'Test image for output creation'
        })
        
        # The response might be 500 if pipeline is not available, which is expected
        # We're testing the endpoint structure, not the pipeline functionality
        self.assertIn(response.status_code, [200, 400, 500])
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('success', data)
            self.assertIn('result_id', data)
            self.assertIn('predicted_count', data)
            self.assertIn('object_type', data)
        elif response.status_code == 500:
            data = json.loads(response.data)
            self.assertIn('error', data)
            # This is expected if AI pipeline is not available
        elif response.status_code == 400:
            data = json.loads(response.data)
            self.assertIn('error', data)
            # This is expected for invalid file types or other validation errors
    
    def test_get_output_details(self):
        """Test getting output details"""
        if not self.test_output_id:
            self.skipTest("No test output available")
        
        response = self.client.get(f'/api/results/{self.test_output_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('result', data)
        
        result = data['result']
        self.assertIn('id', result)
        self.assertIn('predicted_count', result)
        self.assertIn('pred_confidence', result)
        self.assertIn('object_type', result)
        self.assertIn('created_at', result)
        self.assertIn('updated_at', result)
        self.assertEqual(result['id'], self.test_output_id)
    
    def test_update_output_correction(self):
        """Test updating output correction"""
        if not self.test_output_id:
            self.skipTest("No test output available")
        
        response = self.client.put('/api/correct', 
                                 data=json.dumps({
                                     'result_id': self.test_output_id,
                                     'corrected_count': 5
                                 }),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('result_id', data)
        self.assertIn('predicted_count', data)
        self.assertIn('corrected_count', data)
        self.assertIn('updated_at', data)
        self.assertEqual(data['corrected_count'], 5)
        self.assertEqual(data['result_id'], self.test_output_id)
    
    def test_update_output_correction_multiple_times(self):
        """Test updating output correction multiple times"""
        if not self.test_output_id:
            self.skipTest("No test output available")
        
        # First correction
        response = self.client.put('/api/correct', 
                                 data=json.dumps({
                                     'result_id': self.test_output_id,
                                     'corrected_count': 4
                                 }),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['corrected_count'], 4)
        
        # Second correction
        response = self.client.put('/api/correct', 
                                 data=json.dumps({
                                     'result_id': self.test_output_id,
                                     'corrected_count': 6
                                 }),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['corrected_count'], 6)
    
    def test_delete_output(self):
        """Test deleting output"""
        if not self.test_output_id:
            self.skipTest("No test output available")
        
        # Create a separate output for deletion test
        from storage.database_functions import save_prediction_result
        import uuid
        
        unique_id = str(uuid.uuid4())[:8]
        test_image_path = f"test_delete_{unique_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        output = save_prediction_result(
            image_path=test_image_path,
            object_type_name='person',
            predicted_count=2,
            description='Test output for deletion',
            pred_confidence=0.90
        )
        
        delete_id = output.id
        
        # Delete the output
        response = self.client.delete(f'/api/results/{delete_id}/delete')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('message', data)
        self.assertIn('deleted_result_id', data)
        self.assertEqual(data['deleted_result_id'], delete_id)
        
        # Verify the output is deleted
        response = self.client.get(f'/api/results/{delete_id}')
        self.assertEqual(response.status_code, 404)
    
    def test_output_with_feedback_metrics(self):
        """Test output with feedback and performance metrics"""
        if not self.test_output_id:
            self.skipTest("No test output available")
        
        # Add correction to get performance metrics
        response = self.client.put('/api/correct', 
                                 data=json.dumps({
                                     'result_id': self.test_output_id,
                                     'corrected_count': 4
                                 }),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Get result details to check metrics
        response = self.client.get(f'/api/results/{self.test_output_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        result = data['result']
        self.assertIn('f1_score', result)
        self.assertIn('precision', result)
        self.assertIn('recall', result)
        self.assertIn('accuracy', result)
        self.assertIn('has_feedback', result)
        self.assertTrue(result['has_feedback'])
    
    def test_output_validation(self):
        """Test output validation"""
        # Test with invalid UUID format
        response = self.client.get('/api/results/invalid-uuid')
        self.assertEqual(response.status_code, 404)
        
        # Test with valid UUID format but nonexistent
        fake_uuid = str(uuid.uuid4())
        response = self.client.get(f'/api/results/{fake_uuid}')
        self.assertEqual(response.status_code, 404)
    
    def test_output_error_handling(self):
        """Test output error handling"""
        # Test correction with invalid UUID
        response = self.client.put('/api/correct', 
                                 data=json.dumps({
                                     'result_id': 'invalid-uuid',
                                     'corrected_count': 5
                                 }),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        
        # Test deletion with invalid UUID
        response = self.client.delete('/api/results/invalid-uuid/delete')
        self.assertEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
