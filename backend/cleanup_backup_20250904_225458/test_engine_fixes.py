#!/usr/bin/python3
"""Test Engine Fixes"""

import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variables for testing
os.environ['OBJ_DETECT_MYSQL_USER'] = os.getenv('OBJ_DETECT_MYSQL_USER', 'obj_detect_dev')
os.environ['OBJ_DETECT_MYSQL_PWD'] = os.getenv('OBJ_DETECT_MYSQL_PWD', 'obj_detect_dev_pwd')
os.environ['OBJ_DETECT_MYSQL_HOST'] = os.getenv('OBJ_DETECT_MYSQL_HOST', 'localhost')
os.environ['OBJ_DETECT_MYSQL_DB'] = os.getenv('OBJ_DETECT_MYSQL_DB', 'obj_detect_dev_db')
os.environ['OBJ_DETECT_ENV'] = os.getenv('OBJ_DETECT_ENV', 'development')

def test_engine_methods():
    """Test that all Engine methods work"""
    print("Testing Engine Methods...")
    print("=" * 40)
    
    try:
        from storage.engine.engine import Engine
        from storage.object_types import ObjectType
        
        # Create engine instance
        engine = Engine()
        engine.reload()
        print("SUCCESS: Engine created and database connected")
        
        # Test get_all method
        print("\nTesting get_all method...")
        all_types = engine.get_all(ObjectType)
        print(f"SUCCESS: get_all returned {len(all_types)} object types")
        
        # Test get_by_name method
        print("\nTesting get_by_name method...")
        # First create a test object
        test_obj = ObjectType()
        test_obj.name = "test_method"
        test_obj.description = "Test method object"
        engine.new(test_obj)
        engine.save()
        
        # Now test get_by_name
        found_obj = engine.get_by_name(ObjectType, name="test_method")
        if found_obj:
            print(f"SUCCESS: get_by_name found object: {found_obj.name}")
        else:
            print("ERROR: get_by_name failed to find object")
            return False
        
        # Test count method
        print("\nTesting count method...")
        count = engine.count(ObjectType)
        print(f"SUCCESS: count returned {count} object types")
        
        # Clean up
        engine.delete(test_obj)
        print("SUCCESS: Test object cleaned up")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Engine method test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_storage_import():
    """Test that storage import works correctly"""
    print("\nTesting Storage Import...")
    print("=" * 40)
    
    try:
        from storage import database
        from storage.object_types import ObjectType
        
        print("SUCCESS: Storage import working")
        
        # Test database object
        all_types = database.get_all(ObjectType)
        print(f"SUCCESS: Database object working - found {len(all_types)} object types")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Storage import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Engine Fixes Test Suite")
    print("=" * 50)
    
    # Test engine methods
    if not test_engine_methods():
        print("ERROR: Engine methods test failed")
        return False
    
    # Test storage import
    if not test_storage_import():
        print("ERROR: Storage import test failed")
        return False
    
    print("\n" + "=" * 50)
    print("SUCCESS: All engine fixes working!")
    print("Ready to run the full ObjectType migration test")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
