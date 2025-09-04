#!/usr/bin/python3
"""Test Relationship Fixes"""

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

def test_relationships():
    """Test model relationships"""
    print("Testing Model Relationships...")
    print("=" * 40)
    
    try:
        from storage.engine.engine import Engine
        from storage.outputs import Output
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        engine = Engine()
        engine.reload()
        print("SUCCESS: Engine created and database connected")
        
        # Create test data
        import time
        unique_name = f"relationship_test_{int(time.time())}"
        
        # Create ObjectType
        print("\nCreating ObjectType...")
        obj_type = ObjectType()
        obj_type.name = unique_name
        obj_type.description = "Test object type for relationships"
        engine.new(obj_type)
        engine.save()
        print(f"SUCCESS: Created ObjectType: {obj_type.name}")
        
        # Create Input
        print("\nCreating Input...")
        test_input = Input()
        test_input.image_path = f"/test/relationship_{int(time.time())}.jpg"
        test_input.description = "Test input for relationships"
        engine.new(test_input)
        engine.save()
        print(f"SUCCESS: Created Input: {test_input.image_path}")
        
        # Create Output
        print("\nCreating Output...")
        output = Output()
        output.predicted_count = 3
        output.pred_confidence = 0.92
        output.object_type_id = obj_type.id
        output.input_id = test_input.id
        engine.new(output)
        engine.save()
        print(f"SUCCESS: Created Output: {output.id}")
        
        # Test relationships
        print("\nTesting relationships...")
        
        # Test ObjectType -> Outputs relationship
        print("Testing ObjectType -> Outputs relationship...")
        if hasattr(obj_type, 'outputs'):
            print(f"SUCCESS: ObjectType has outputs relationship: {len(obj_type.outputs)} outputs")
            for out in obj_type.outputs:
                print(f"  - Output {out.id}: {out.predicted_count} objects")
        else:
            print("ERROR: ObjectType missing outputs relationship")
            return False
        
        # Test Input -> Outputs relationship
        print("Testing Input -> Outputs relationship...")
        if hasattr(test_input, 'outputs'):
            print(f"SUCCESS: Input has outputs relationship: {len(test_input.outputs)} outputs")
            for out in test_input.outputs:
                print(f"  - Output {out.id}: {out.predicted_count} objects")
        else:
            print("ERROR: Input missing outputs relationship")
            return False
        
        # Test Output -> ObjectType relationship
        print("Testing Output -> ObjectType relationship...")
        if hasattr(output, 'object_type'):
            print(f"SUCCESS: Output has object_type relationship: {output.object_type.name}")
        else:
            print("ERROR: Output missing object_type relationship")
            return False
        
        # Test Output -> Input relationship
        print("Testing Output -> Input relationship...")
        if hasattr(output, 'input'):
            print(f"SUCCESS: Output has input relationship: {output.input.image_path}")
        else:
            print("ERROR: Output missing input relationship")
            return False
        
        # Clean up
        print("\nCleaning up test data...")
        engine.delete(output)
        engine.delete(obj_type)
        engine.delete(test_input)
        print("SUCCESS: Test data cleaned up")
        
        print("\n" + "=" * 40)
        print("SUCCESS: All relationship tests passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: Relationship test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Relationship Fix Test")
    print("=" * 50)
    
    if test_relationships():
        print("\nSUCCESS: Relationships are working correctly!")
        print("Ready to run the full Output migration test")
        return True
    else:
        print("\nERROR: Relationship tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
