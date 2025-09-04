#!/usr/bin/python3
"""Simple ObjectType Test - No Session Issues"""

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

def test_object_type_basic():
    """Test basic ObjectType functionality without complex scenarios"""
    print("Simple ObjectType Test")
    print("=" * 40)
    
    try:
        from storage.engine.engine import Engine
        from storage.object_types import ObjectType
        
        # Create engine instance
        engine = Engine()
        engine.reload()
        print("SUCCESS: Engine created and database connected")
        
        # Test 1: Create a new ObjectType
        print("\nTest 1: Creating new ObjectType...")
        import time
        unique_name = f"simple_test_{int(time.time())}"
        obj_type = ObjectType()
        obj_type.name = unique_name
        obj_type.description = "Simple test object type"
        
        # Check UUID generation
        print(f"Generated UUID: {obj_type.id}")
        print(f"UUID length: {len(obj_type.id)}")
        print(f"Created at: {obj_type.created_at}")
        print(f"Updated at: {obj_type.updated_at}")
        
        # Save to database
        engine.new(obj_type)
        engine.save()
        print("SUCCESS: ObjectType saved to database")
        
        # Test 2: Retrieve the ObjectType
        print("\nTest 2: Retrieving ObjectType...")
        retrieved_type = engine.get(ObjectType, id=obj_type.id)
        if retrieved_type:
            print(f"SUCCESS: Retrieved ObjectType: {retrieved_type.name}")
            print(f"ID: {retrieved_type.id}")
            print(f"Description: {retrieved_type.description}")
        else:
            print("ERROR: Failed to retrieve ObjectType")
            return False
        
        # Test 3: Query by name
        print("\nTest 3: Querying by name...")
        found_type = engine.get_by_name(ObjectType, name=unique_name)
        if found_type:
            print(f"SUCCESS: Found ObjectType by name: {found_type.name}")
        else:
            print("ERROR: Failed to find ObjectType by name")
            return False
        
        # Test 4: Get all ObjectTypes
        print("\nTest 4: Getting all ObjectTypes...")
        all_types = engine.get_all(ObjectType)
        print(f"SUCCESS: Found {len(all_types)} ObjectTypes in database")
        
        # Test 5: Count ObjectTypes
        print("\nTest 5: Counting ObjectTypes...")
        count = engine.count(ObjectType)
        print(f"SUCCESS: Count returned {count} ObjectTypes")
        
        # Clean up test data
        print("\nCleanup: Removing test ObjectType...")
        engine.delete(obj_type)
        print("SUCCESS: Test ObjectType cleaned up")
        
        print("\n" + "=" * 40)
        print("SUCCESS: All basic ObjectType tests passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: ObjectType test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_unique_constraint():
    """Test unique constraint separately"""
    print("\nTesting Unique Constraint...")
    print("=" * 40)
    
    try:
        from storage.engine.engine import Engine
        from storage.object_types import ObjectType
        
        engine = Engine()
        engine.reload()  # Fresh session
        
        # Create first object
        import time
        unique_name = f"unique_test_{int(time.time())}"
        obj_type1 = ObjectType()
        obj_type1.name = unique_name
        obj_type1.description = "First object"
        engine.new(obj_type1)
        engine.save()
        print(f"SUCCESS: Created first object: {unique_name}")
        
        # Try to create second object with same name
        obj_type2 = ObjectType()
        obj_type2.name = unique_name  # Same name
        obj_type2.description = "Second object"
        engine.new(obj_type2)
        
        try:
            engine.save()
            print("ERROR: Unique constraint not working - duplicate name allowed")
            # Clean up both objects
            engine.delete(obj_type1)
            engine.delete(obj_type2)
            return False
        except Exception as e:
            print(f"SUCCESS: Unique constraint working - {str(e)}")
            # Clean up first object
            engine.delete(obj_type1)
            return True
        
    except Exception as e:
        print(f"ERROR: Unique constraint test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Simple ObjectType Test Suite")
    print("=" * 50)
    
    # Test basic functionality
    if not test_object_type_basic():
        print("ERROR: Basic ObjectType tests failed")
        return False
    
    # Test unique constraint
    if not test_unique_constraint():
        print("ERROR: Unique constraint test failed")
        return False
    
    print("\n" + "=" * 50)
    print("SUCCESS: All simple ObjectType tests passed!")
    print("ObjectType model is working correctly")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
