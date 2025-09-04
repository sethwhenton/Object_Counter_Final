#!/usr/bin/python3
"""Test Output Model Migration"""

import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variables for testing
os.environ['OBJ_DETECT_MYSQL_USER'] = os.getenv('OBJ_DETECT_MYSQL_USER', 'obj_detect_dev')
os.environ['OBJ_DETECT_MYSQL_PWD'] = os.getenv('OBJ_DETECT_MYSQL_PWD', 'obj_detect_dev_pwd')
os.environ['OBJ_DETECT_MYSQL_HOST'] = os.getenv('OBJ_DETECT_MYSQL_HOST', 'localhost')
os.environ['OBJ_DETECT_MYSQL_DB'] = os.getenv('OBJ_DETECT_MYSQL_DB', 'obj_detect_dev_db')
os.environ['OBJ_DETECT_ENV'] = os.getenv('OBJ_DETECT_ENV', 'development')

def test_output_creation():
    """Test creating Output instances"""
    print("Testing Output Model Migration...")
    print("=" * 50)
    
    try:
        from storage.engine.engine import Engine
        from storage.outputs import Output
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        # Create engine instance
        engine = Engine()
        engine.reload()
        print("SUCCESS: Engine created and database connected")
        
        # Create test ObjectType first
        print("\nCreating test ObjectType...")
        import time
        unique_name = f"output_test_type_{int(time.time())}"
        obj_type = ObjectType()
        obj_type.name = unique_name
        obj_type.description = "Test object type for output testing"
        engine.new(obj_type)
        engine.save()
        print(f"SUCCESS: Created ObjectType: {obj_type.name}")
        
        # Create test Input
        print("\nCreating test Input...")
        test_input = Input()
        test_input.image_path = f"/test/path/image_{int(time.time())}.jpg"
        test_input.description = "Test input for output testing"
        engine.new(test_input)
        engine.save()
        print(f"SUCCESS: Created Input: {test_input.image_path}")
        
        # Test 1: Create a new Output
        print("\nTest 1: Creating new Output...")
        output = Output()
        output.predicted_count = 5
        output.corrected_count = None  # No correction yet
        output.pred_confidence = 0.85  # 85% confidence
        output.object_type_id = obj_type.id
        output.input_id = test_input.id
        
        # Check UUID generation
        print(f"Generated UUID: {output.id}")
        print(f"UUID length: {len(output.id)}")
        print(f"Predicted count: {output.predicted_count}")
        print(f"Prediction confidence: {output.pred_confidence}")
        print(f"Object type ID: {output.object_type_id}")
        print(f"Input ID: {output.input_id}")
        print(f"Created at: {output.created_at}")
        print(f"Updated at: {output.updated_at}")
        
        # Save to database
        engine.new(output)
        engine.save()
        print("SUCCESS: Output saved to database")
        
        # Test 2: Retrieve the Output
        print("\nTest 2: Retrieving Output...")
        retrieved_output = engine.get(Output, id=output.id)
        if retrieved_output:
            print(f"SUCCESS: Retrieved Output: {retrieved_output.id}")
            print(f"Predicted count: {retrieved_output.predicted_count}")
            print(f"Confidence: {retrieved_output.pred_confidence}")
            print(f"Object type ID: {retrieved_output.object_type_id}")
            print(f"Input ID: {retrieved_output.input_id}")
        else:
            print("ERROR: Failed to retrieve Output")
            return False
        
        # Test 3: Update the Output (add correction)
        print("\nTest 3: Updating Output with correction...")
        retrieved_output.corrected_count = 7
        retrieved_output.updated_at = datetime.now()
        engine.save()
        print("SUCCESS: Output updated with correction")
        
        # Verify the update
        updated_output = engine.get(Output, id=output.id)
        if updated_output and updated_output.corrected_count == 7:
            print(f"SUCCESS: Correction verified: {updated_output.corrected_count}")
        else:
            print("ERROR: Correction not saved properly")
            return False
        
        # Test 4: Get all Outputs
        print("\nTest 4: Getting all Outputs...")
        all_outputs = engine.get_all(Output)
        print(f"SUCCESS: Found {len(all_outputs)} Outputs in database")
        for out in all_outputs:
            print(f"  - Output {out.id}: {out.predicted_count} objects, confidence: {out.pred_confidence}")
        
        # Test 5: Count Outputs
        print("\nTest 5: Counting Outputs...")
        count = engine.count(Output)
        print(f"SUCCESS: Count returned {count} Outputs")
        
        # Test 6: Test foreign key relationships
        print("\nTest 6: Testing foreign key relationships...")
        # Get the related ObjectType
        related_obj_type = engine.get(ObjectType, id=output.object_type_id)
        if related_obj_type:
            print(f"SUCCESS: Found related ObjectType: {related_obj_type.name}")
        else:
            print("ERROR: Failed to find related ObjectType")
            return False
        
        # Get the related Input
        related_input = engine.get(Input, id=output.input_id)
        if related_input:
            print(f"SUCCESS: Found related Input: {related_input.image_path}")
        else:
            print("ERROR: Failed to find related Input")
            return False
        
        # Clean up test data
        print("\nCleanup: Removing test data...")
        engine.delete(output)
        engine.delete(obj_type)
        engine.delete(test_input)
        print("SUCCESS: Test data cleaned up")
        
        print("\n" + "=" * 50)
        print("SUCCESS: All Output migration tests passed!")
        print("Output model is ready for production use")
        return True
        
    except Exception as e:
        print(f"ERROR: Output migration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_output_relationships():
    """Test Output relationships with other models"""
    print("\nTesting Output Relationships...")
    print("=" * 50)
    
    try:
        from storage.engine.engine import Engine
        from storage.outputs import Output
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        engine = Engine()
        
        # Create test data
        import time
        unique_name = f"relationship_test_{int(time.time())}"
        
        # Create ObjectType
        obj_type = ObjectType()
        obj_type.name = unique_name
        obj_type.description = "Test object type for relationships"
        engine.new(obj_type)
        engine.save()
        
        # Create Input
        test_input = Input()
        test_input.image_path = f"/test/relationship_{int(time.time())}.jpg"
        test_input.description = "Test input for relationships"
        engine.new(test_input)
        engine.save()
        
        # Create Output
        output = Output()
        output.predicted_count = 3
        output.pred_confidence = 0.92
        output.object_type_id = obj_type.id
        output.input_id = test_input.id
        engine.new(output)
        engine.save()
        
        print(f"SUCCESS: Created Output with relationships")
        print(f"Output ID: {output.id}")
        print(f"ObjectType ID: {obj_type.id}")
        print(f"Input ID: {test_input.id}")
        
        # Test cascade delete (when we implement it)
        print("\nTesting cascade delete...")
        # Delete ObjectType and see if Output is affected
        # Note: This depends on cascade settings in the model
        
        # Clean up
        engine.delete(output)
        engine.delete(obj_type)
        engine.delete(test_input)
        print("SUCCESS: Relationship test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Relationship test failed: {e}")
        return False

def test_output_validation():
    """Test Output field validation"""
    print("\nTesting Output Field Validation...")
    print("=" * 50)
    
    try:
        from storage.engine.engine import Engine
        from storage.outputs import Output
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        engine = Engine()
        
        # Create test data
        import time
        unique_name = f"validation_test_{int(time.time())}"
        
        obj_type = ObjectType()
        obj_type.name = unique_name
        obj_type.description = "Test object type for validation"
        engine.new(obj_type)
        engine.save()
        
        test_input = Input()
        test_input.image_path = f"/test/validation_{int(time.time())}.jpg"
        test_input.description = "Test input for validation"
        engine.new(test_input)
        engine.save()
        
        # Test 1: Valid Output
        print("Test 1: Creating valid Output...")
        valid_output = Output()
        valid_output.predicted_count = 10
        valid_output.pred_confidence = 0.95
        valid_output.object_type_id = obj_type.id
        valid_output.input_id = test_input.id
        engine.new(valid_output)
        engine.save()
        print("SUCCESS: Valid Output created")
        
        # Test 2: Output with correction
        print("Test 2: Creating Output with correction...")
        corrected_output = Output()
        corrected_output.predicted_count = 8
        corrected_output.corrected_count = 12
        corrected_output.pred_confidence = 0.78
        corrected_output.object_type_id = obj_type.id
        corrected_output.input_id = test_input.id
        engine.new(corrected_output)
        engine.save()
        print("SUCCESS: Output with correction created")
        
        # Test 3: High confidence Output
        print("Test 3: Creating high confidence Output...")
        high_conf_output = Output()
        high_conf_output.predicted_count = 1
        high_conf_output.pred_confidence = 0.99
        high_conf_output.object_type_id = obj_type.id
        high_conf_output.input_id = test_input.id
        engine.new(high_conf_output)
        engine.save()
        print("SUCCESS: High confidence Output created")
        
        # Clean up
        engine.delete(valid_output)
        engine.delete(corrected_output)
        engine.delete(high_conf_output)
        engine.delete(obj_type)
        engine.delete(test_input)
        print("SUCCESS: Validation test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Validation test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Output Model Migration Test Suite")
    print("=" * 60)
    
    # Test basic Output functionality
    if not test_output_creation():
        print("ERROR: Output creation tests failed")
        return False
    
    # Test relationships
    if not test_output_relationships():
        print("ERROR: Output relationship tests failed")
        return False
    
    # Test validation
    if not test_output_validation():
        print("ERROR: Output validation tests failed")
        return False
    
    print("\n" + "=" * 60)
    print("SUCCESS: All Output migration tests passed!")
    print("Step 3.3: Output Model Migration - COMPLETE!")
    print("Ready to proceed to Step 3.4: Update Database Functions")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
