#!/usr/bin/python3
"""Simple Output Test - No Session Issues"""

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

def test_output_basic():
    """Test basic Output functionality"""
    print("Simple Output Test")
    print("=" * 40)
    
    try:
        from storage.engine.engine import Engine
        from storage.outputs import Output
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        # Create engine instance
        engine = Engine()
        engine.reload()
        print("SUCCESS: Engine created and database connected")
        
        # Get existing data or create test data
        print("\nGetting existing data...")
        object_types = engine.get_all(ObjectType)
        inputs = engine.get_all(Input)
        
        if not object_types:
            print("ERROR: No object types found. Please create object types first.")
            return False
        
        if not inputs:
            print("Creating test input...")
            import time
            test_input = Input()
            test_input.image_path = f"/test/simple_{int(time.time())}.jpg"
            test_input.description = "Test input for simple output test"
            engine.new(test_input)
            engine.save()
            inputs = [test_input]
            print(f"SUCCESS: Created test input: {test_input.image_path}")
        else:
            print(f"SUCCESS: Found {len(inputs)} existing inputs")
        
        # Test 1: Create a new Output
        print("\nTest 1: Creating new Output...")
        import time
        output = Output()
        output.predicted_count = 5
        output.corrected_count = None
        output.pred_confidence = 0.85
        output.object_type_id = object_types[0].id
        output.input_id = inputs[0].id
        
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
        else:
            print("ERROR: Failed to retrieve Output")
            return False
        
        # Test 3: Update the Output
        print("\nTest 3: Updating Output...")
        retrieved_output.corrected_count = 7
        retrieved_output.updated_at = datetime.now()
        engine.save()
        print("SUCCESS: Output updated")
        
        # Test 4: Get all Outputs
        print("\nTest 4: Getting all Outputs...")
        all_outputs = engine.get_all(Output)
        print(f"SUCCESS: Found {len(all_outputs)} Outputs in database")
        
        # Test 5: Count Outputs
        print("\nTest 5: Counting Outputs...")
        count = engine.count(Output)
        print(f"SUCCESS: Count returned {count} Outputs")
        
        # Test 6: Test relationships
        print("\nTest 6: Testing relationships...")
        obj_type = engine.get(ObjectType, id=output.object_type_id)
        if obj_type:
            print(f"SUCCESS: Found related ObjectType: {obj_type.name}")
        else:
            print("ERROR: Failed to find related ObjectType")
            return False
        
        input_obj = engine.get(Input, id=output.input_id)
        if input_obj:
            print(f"SUCCESS: Found related Input: {input_obj.image_path}")
        else:
            print("ERROR: Failed to find related Input")
            return False
        
        # Clean up test data
        print("\nCleanup: Removing test Output...")
        engine.delete(output)
        print("SUCCESS: Test Output cleaned up")
        
        print("\n" + "=" * 40)
        print("SUCCESS: All basic Output tests passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: Output test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Simple Output Test Suite")
    print("=" * 50)
    
    if test_output_basic():
        print("\nSUCCESS: Output model is working correctly!")
        print("Ready to proceed with database functions migration")
        return True
    else:
        print("\nERROR: Output tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
