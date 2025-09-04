#!/usr/bin/python3
"""Storage Tests for Database Operations
Test MySQL database operations, model creation, relationships, and constraints
"""
import unittest
import os
import sys
import uuid
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests import TEST_CONFIG


class TestDatabaseOperations(unittest.TestCase):
    """Test database operations and engine functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        # Import after setting up environment
        from storage import database
        from storage.database_functions import init_database
        
        cls.database = database
        cls.database.reload()
        init_database()
    
    def setUp(self):
        """Set up each test"""
        # Clean up any existing test data
        from storage.database_functions import get_all_outputs, delete_output
        from storage import database
        
        # Clean up test outputs
        outputs = get_all_outputs()
        for output in outputs:
            if 'test_' in str(output.id):
                try:
                    delete_output(output.id)
                except:
                    pass
        
        # Clean up test object types and inputs
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        object_types = database.get_all(ObjectType)
        for obj_type in object_types:
            if 'test_' in obj_type.name:
                try:
                    database.delete(obj_type)
                except:
                    pass
        
        inputs = database.get_all(Input)
        for input_record in inputs:
            if 'test_' in input_record.image_path:
                try:
                    database.delete(input_record)
                except:
                    pass
    
    def test_database_connection(self):
        """Test database connection"""
        from storage import database
        
        # Test that database is connected
        self.assertIsNotNone(database)
        self.assertIsNotNone(database._Engine__session)
        
        # Test basic query
        from storage.object_types import ObjectType
        count = database.count(ObjectType)
        self.assertGreaterEqual(count, 0)
    
    def test_database_engine_methods(self):
        """Test database engine methods"""
        from storage import database
        from storage.object_types import ObjectType
        
        # Test get method
        object_types = database.get_all(ObjectType)
        if object_types:
            obj_type = database.get(ObjectType, object_types[0].id)
            self.assertIsNotNone(obj_type)
            self.assertEqual(obj_type.id, object_types[0].id)
        
        # Test get_by_name method
        car_type = database.get_by_name(ObjectType, 'car')
        if car_type:
            self.assertEqual(car_type.name, 'car')
        
        # Test count method
        count = database.count(ObjectType)
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 0)
    
    def test_database_transactions(self):
        """Test database transactions and rollback"""
        from storage import database
        from storage.object_types import ObjectType
        
        # Test successful transaction
        initial_count = database.count(ObjectType)
        
        obj_type = ObjectType()
        obj_type.name = f"test_transaction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        obj_type.description = "Test transaction"
        
        database.new(obj_type)
        database.save()
        
        new_count = database.count(ObjectType)
        self.assertEqual(new_count, initial_count + 1)
        
        # Test rollback
        try:
            # Try to create duplicate (should fail)
            duplicate_type = ObjectType()
            duplicate_type.name = obj_type.name  # Same name
            duplicate_type.description = "Duplicate"
            
            database.new(duplicate_type)
            database.save()
            self.fail("Should have raised an exception")
        except Exception:
            # Should rollback automatically
            database.rollback()
            final_count = database.count(ObjectType)
            self.assertEqual(final_count, new_count)  # Should be same as before rollback
        
        # Clean up
        database.delete(obj_type)
    
    def test_database_session_management(self):
        """Test database session management"""
        from storage import database
        
        # Test session is available
        self.assertIsNotNone(database._Engine__session)
        
        # Test session operations
        from storage.object_types import ObjectType
        object_types = database.get_all(ObjectType)
        self.assertIsInstance(object_types, list)
    
    def test_database_error_handling(self):
        """Test database error handling"""
        from storage import database
        from storage.object_types import ObjectType
        
        # Test getting nonexistent object
        fake_id = str(uuid.uuid4())
        result = database.get(ObjectType, fake_id)
        self.assertIsNone(result)
        
        # Test getting by nonexistent name
        result = database.get_by_name(ObjectType, 'nonexistent_type')
        self.assertIsNone(result)


class TestModelCreation(unittest.TestCase):
    """Test model creation and validation"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        from storage import database
        from storage.database_functions import init_database
        
        cls.database = database
        cls.database.reload()
        init_database()
    
    def setUp(self):
        """Set up each test"""
        # Clean up test data
        from storage.database_functions import get_all_outputs, delete_output
        from storage import database
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        # Clean up test outputs
        outputs = get_all_outputs()
        for output in outputs:
            if 'test_' in str(output.id):
                try:
                    delete_output(output.id)
                except:
                    pass
        
        # Clean up test object types and inputs
        object_types = database.get_all(ObjectType)
        for obj_type in object_types:
            if 'test_' in obj_type.name:
                try:
                    database.delete(obj_type)
                except:
                    pass
        
        inputs = database.get_all(Input)
        for input_record in inputs:
            if 'test_' in input_record.image_path:
                try:
                    database.delete(input_record)
                except:
                    pass
    
    def test_object_type_creation(self):
        """Test ObjectType model creation"""
        from storage import database
        from storage.object_types import ObjectType
        
        # Create object type
        obj_type = ObjectType()
        obj_type.name = f"test_type_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        obj_type.description = "Test object type"
        
        # Check UUID generation
        self.assertIsNotNone(obj_type.id)
        self.assertEqual(len(obj_type.id), 36)  # UUID length
        self.assertIn('-', obj_type.id)
        
        # Save to database
        database.new(obj_type)
        database.save()
        
        # Verify it was saved
        retrieved = database.get(ObjectType, obj_type.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, obj_type.name)
        self.assertEqual(retrieved.description, obj_type.description)
        
        # Clean up
        database.delete(obj_type)
    
    def test_input_creation(self):
        """Test Input model creation"""
        from storage import database
        from storage.inputs import Input
        
        # Create input
        input_record = Input()
        input_record.image_path = f"test_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        input_record.description = "Test input"
        
        # Check UUID generation
        self.assertIsNotNone(input_record.id)
        self.assertEqual(len(input_record.id), 36)
        
        # Save to database
        database.new(input_record)
        database.save()
        
        # Verify it was saved
        retrieved = database.get(Input, input_record.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.image_path, input_record.image_path)
        self.assertEqual(retrieved.description, input_record.description)
        
        # Clean up
        database.delete(input_record)
    
    def test_output_creation(self):
        """Test Output model creation"""
        from storage import database
        from storage.outputs import Output
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        # Create required objects first
        obj_type = ObjectType()
        obj_type.name = f"test_type_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        obj_type.description = "Test object type"
        database.new(obj_type)
        database.save()
        
        input_record = Input()
        input_record.image_path = f"test_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        input_record.description = "Test input"
        database.new(input_record)
        database.save()
        
        # Create output
        output = Output()
        output.predicted_count = 5
        output.pred_confidence = 0.85
        output.object_type_id = obj_type.id
        output.input_id = input_record.id
        
        # Check UUID generation
        self.assertIsNotNone(output.id)
        self.assertEqual(len(output.id), 36)
        
        # Save to database
        database.new(output)
        database.save()
        
        # Verify it was saved
        retrieved = database.get(Output, output.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.predicted_count, 5)
        self.assertEqual(retrieved.pred_confidence, 0.85)
        self.assertEqual(retrieved.object_type_id, obj_type.id)
        self.assertEqual(retrieved.input_id, input_record.id)
        
        # Clean up
        database.delete(output)
        database.delete(input_record)
        database.delete(obj_type)
    
    def test_model_validation(self):
        """Test model validation and constraints"""
        from storage import database
        from storage.object_types import ObjectType
        
        # Test unique constraint on object type name
        obj_type1 = ObjectType()
        obj_type1.name = f"test_unique_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        obj_type1.description = "Test unique"
        database.new(obj_type1)
        database.save()
        
        # Try to create another with same name
        obj_type2 = ObjectType()
        obj_type2.name = obj_type1.name  # Same name
        obj_type2.description = "Test unique duplicate"
        database.new(obj_type2)
        
        with self.assertRaises(Exception):
            database.save()  # Should fail due to unique constraint
        
        # Clean up
        database.rollback()
        database.delete(obj_type1)
    
    def test_model_timestamps(self):
        """Test model timestamp handling"""
        from storage import database
        from storage.object_types import ObjectType
        
        # Create object type
        obj_type = ObjectType()
        obj_type.name = f"test_timestamp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        obj_type.description = "Test timestamp"
        
        # Check initial timestamps
        self.assertIsNotNone(obj_type.created_at)
        self.assertIsNotNone(obj_type.updated_at)
        
        # Save to database
        database.new(obj_type)
        database.save()
        
        # Check timestamps after save
        retrieved = database.get(ObjectType, obj_type.id)
        self.assertIsNotNone(retrieved.created_at)
        self.assertIsNotNone(retrieved.updated_at)
        
        # Clean up
        database.delete(obj_type)


class TestModelRelationships(unittest.TestCase):
    """Test model relationships and foreign keys"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        from storage import database
        from storage.database_functions import init_database
        
        cls.database = database
        cls.database.reload()
        init_database()
    
    def setUp(self):
        """Set up each test"""
        # Clean up test data
        from storage.database_functions import get_all_outputs, delete_output
        from storage import database
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        # Clean up test outputs
        outputs = get_all_outputs()
        for output in outputs:
            if 'test_' in str(output.id):
                try:
                    delete_output(output.id)
                except:
                    pass
        
        # Clean up test object types and inputs
        object_types = database.get_all(ObjectType)
        for obj_type in object_types:
            if 'test_' in obj_type.name:
                try:
                    database.delete(obj_type)
                except:
                    pass
        
        inputs = database.get_all(Input)
        for input_record in inputs:
            if 'test_' in input_record.image_path:
                try:
                    database.delete(input_record)
                except:
                    pass
    
    def test_output_object_type_relationship(self):
        """Test Output-ObjectType relationship"""
        from storage import database
        from storage.outputs import Output
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        # Create object type
        obj_type = ObjectType()
        obj_type.name = f"test_relationship_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        obj_type.description = "Test relationship"
        database.new(obj_type)
        database.save()
        
        # Create input
        input_record = Input()
        input_record.image_path = f"test_relationship_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        input_record.description = "Test relationship input"
        database.new(input_record)
        database.save()
        
        # Create output
        output = Output()
        output.predicted_count = 3
        output.pred_confidence = 0.90
        output.object_type_id = obj_type.id
        output.input_id = input_record.id
        database.new(output)
        database.save()
        
        # Test relationship
        retrieved_output = database.get(Output, output.id)
        self.assertIsNotNone(retrieved_output.object_type)
        self.assertEqual(retrieved_output.object_type.id, obj_type.id)
        self.assertEqual(retrieved_output.object_type.name, obj_type.name)
        
        # Clean up
        database.delete(output)
        database.delete(input_record)
        database.delete(obj_type)
    
    def test_output_input_relationship(self):
        """Test Output-Input relationship"""
        from storage import database
        from storage.outputs import Output
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        # Create object type
        obj_type = ObjectType()
        obj_type.name = f"test_input_rel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        obj_type.description = "Test input relationship"
        database.new(obj_type)
        database.save()
        
        # Create input
        input_record = Input()
        input_record.image_path = f"test_input_rel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        input_record.description = "Test input relationship"
        database.new(input_record)
        database.save()
        
        # Create output
        output = Output()
        output.predicted_count = 2
        output.pred_confidence = 0.75
        output.object_type_id = obj_type.id
        output.input_id = input_record.id
        database.new(output)
        database.save()
        
        # Test relationship
        retrieved_output = database.get(Output, output.id)
        self.assertIsNotNone(retrieved_output.input)
        self.assertEqual(retrieved_output.input.id, input_record.id)
        self.assertEqual(retrieved_output.input.image_path, input_record.image_path)
        
        # Clean up
        database.delete(output)
        database.delete(input_record)
        database.delete(obj_type)
    
    def test_foreign_key_constraints(self):
        """Test foreign key constraints"""
        from storage import database
        from storage.outputs import Output
        
        # Try to create output with invalid foreign keys
        output = Output()
        output.predicted_count = 1
        output.pred_confidence = 0.50
        output.object_type_id = str(uuid.uuid4())  # Invalid object type ID
        output.input_id = str(uuid.uuid4())  # Invalid input ID
        
        database.new(output)
        
        with self.assertRaises(Exception):
            database.save()  # Should fail due to foreign key constraint
        
        database.rollback()
    
    def test_cascade_relationships(self):
        """Test cascade relationships - input deletion should cascade to outputs"""
        from storage import database
        from storage.outputs import Output
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        # Create object type
        obj_type = ObjectType()
        obj_type.name = f"test_cascade_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        obj_type.description = "Test cascade"
        database.new(obj_type)
        database.save()
        
        # Create input
        input_record = Input()
        input_record.image_path = f"test_cascade_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        input_record.description = "Test cascade input"
        database.new(input_record)
        database.save()
        
        # Create output
        output = Output()
        output.predicted_count = 4
        output.pred_confidence = 0.95
        output.object_type_id = obj_type.id
        output.input_id = input_record.id
        database.new(output)
        database.save()
        
        # Test that output exists
        retrieved_output = database.get(Output, output.id)
        self.assertIsNotNone(retrieved_output)
        
        # Delete input (should cascade to output)
        database.delete(input_record)
        
        # Output should be deleted due to cascade delete configured
        retrieved_output = database.get(Output, output.id)
        self.assertIsNone(retrieved_output)
        
        # Clean up
        database.delete(output)
        database.delete(obj_type)


if __name__ == '__main__':
    unittest.main()
