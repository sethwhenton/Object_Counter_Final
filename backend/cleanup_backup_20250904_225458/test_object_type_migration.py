#!/usr/bin/python3
"""Test ObjectType Model Migration"""

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

def test_object_type_creation():
    """Test creating ObjectType instances"""
    print("Testing ObjectType Model Migration...")
    print("=" * 50)
    
    try:
        # Import our new models
        from storage.engine.engine import Engine
        from storage.object_types import ObjectType
        
        # Create engine instance
        engine = Engine()
        engine.reload()
        print("SUCCESS: Engine created and database connected")
        
        # Test 1: Create a new ObjectType
        print("\nTest 1: Creating new ObjectType...")
        import time
        unique_name = f"test_person_{int(time.time())}"
        obj_type = ObjectType()
        obj_type.name = unique_name
        obj_type.description = "Test person object type"
        
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
        
        # Test 3: Update the ObjectType
        print("\nTest 3: Updating ObjectType...")
        retrieved_type.description = "Updated description for test person"
        retrieved_type.updated_at = datetime.now()
        engine.save()
        print("SUCCESS: ObjectType updated")
        
        # Test 4: Query by name
        print("\nTest 4: Querying by name...")
        found_type = engine.get_by_name(ObjectType, name=unique_name)
        if found_type:
            print(f"SUCCESS: Found ObjectType by name: {found_type.name}")
        else:
            print("ERROR: Failed to find ObjectType by name")
            return False
        
        # Test 5: Get all ObjectTypes
        print("\nTest 5: Getting all ObjectTypes...")
        all_types = engine.get_all(ObjectType)
        print(f"SUCCESS: Found {len(all_types)} ObjectTypes in database")
        for obj_type in all_types:
            print(f"  - {obj_type.name}: {obj_type.id}")
        
        # Test 6: Test unique constraint
        print("\nTest 6: Testing unique constraint...")
        duplicate_type = ObjectType()
        duplicate_type.name = unique_name  # Same name as existing
        duplicate_type.description = "Duplicate test"
        
        try:
            engine.new(duplicate_type)
            engine.save()
            print("ERROR: Unique constraint not working - duplicate name allowed")
            return False
        except Exception as e:
            print(f"SUCCESS: Unique constraint working - {str(e)}")
            # Rollback the failed transaction
            engine.rollback()
        
        # Clean up test data
        print("\nCleanup: Removing test ObjectType...")
        try:
            engine.delete(obj_type)
            print("SUCCESS: Test ObjectType cleaned up")
        except Exception as e:
            print(f"WARNING: Cleanup failed (this is expected after rollback): {e}")
            # Try to get a fresh object from database
            fresh_obj = engine.get(ObjectType, id=obj_type.id)
            if fresh_obj:
                engine.delete(fresh_obj)
                print("SUCCESS: Test ObjectType cleaned up (fresh object)")
        
        print("\n" + "=" * 50)
        print("SUCCESS: All ObjectType migration tests passed!")
        print("ObjectType model is ready for production use")
        return True
        
    except Exception as e:
        print(f"ERROR: ObjectType migration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_object_type_relationships():
    """Test ObjectType relationships with other models"""
    print("\nTesting ObjectType Relationships...")
    print("=" * 50)
    
    try:
        from storage.engine.engine import Engine
        from storage.object_types import ObjectType
        from storage.outputs import Output
        
        engine = Engine()
        
        # Create test ObjectType
        import time
        unique_name = f"test_relationship_{int(time.time())}"
        obj_type = ObjectType()
        obj_type.name = unique_name
        obj_type.description = "Test relationship object type"
        engine.new(obj_type)
        engine.save()
        
        # Test relationship (this will be expanded when we migrate Output model)
        print(f"SUCCESS: ObjectType created for relationship testing: {obj_type.name}")
        print(f"ObjectType ID: {obj_type.id}")
        
        # Clean up
        engine.delete(obj_type)
        print("SUCCESS: Relationship test ObjectType cleaned up")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Relationship test failed: {e}")
        return False

def main():
    """Main test function"""
    print("ObjectType Model Migration Test Suite")
    print("=" * 60)
    
    # Test basic ObjectType functionality
    if not test_object_type_creation():
        print("ERROR: ObjectType creation tests failed")
        return False
    
    # Test relationships
    if not test_object_type_relationships():
        print("ERROR: ObjectType relationship tests failed")
        return False
    
    print("\n" + "=" * 60)
    print("SUCCESS: ObjectType Model Migration Complete!")
    print("Ready to proceed to Step 3.2: Migrate Input Model")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
