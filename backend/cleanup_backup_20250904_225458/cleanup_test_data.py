#!/usr/bin/python3
"""Cleanup Test Data Script"""

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

def cleanup_test_data():
    """Clean up test data from previous runs"""
    print("Cleaning up test data...")
    print("=" * 40)
    
    try:
        from storage.engine.engine import Engine
        from storage.object_types import ObjectType
        
        engine = Engine()
        engine.reload()  # Ensure fresh session
        
        # Find and delete test objects by pattern
        all_types = engine.get_all(ObjectType)
        deleted_count = 0
        
        for obj_type in all_types:
            # Check if it's a test object (starts with "test_")
            if obj_type.name.startswith("test_"):
                print(f"Deleting test object: {obj_type.name}")
                try:
                    engine.delete(obj_type)
                    deleted_count += 1
                except Exception as e:
                    print(f"WARNING: Failed to delete {obj_type.name}: {e}")
                    # Try rollback and continue
                    engine.rollback()
        
        if deleted_count > 0:
            print(f"SUCCESS: Deleted {deleted_count} test objects")
        else:
            print("INFO: No test objects found to delete")
        
        # Show remaining object types
        all_types = engine.get_all(ObjectType)
        print(f"\nRemaining object types: {len(all_types)}")
        for obj_type in all_types:
            print(f"  - {obj_type.name}: {obj_type.id}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main cleanup function"""
    print("Test Data Cleanup Utility")
    print("=" * 50)
    
    if cleanup_test_data():
        print("\nSUCCESS: Test data cleanup completed!")
        print("You can now run the migration tests safely")
        return True
    else:
        print("\nERROR: Test data cleanup failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
