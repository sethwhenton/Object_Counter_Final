#!/usr/bin/python3
"""Simple MySQL Connection Test"""
import os

# Set environment variables
os.environ['OBJ_DETECT_MYSQL_USER'] = 'obj_detect_dev'
os.environ['OBJ_DETECT_MYSQL_PWD'] = 'obj_detect_dev_pwd'
os.environ['OBJ_DETECT_MYSQL_HOST'] = 'localhost'
os.environ['OBJ_DETECT_MYSQL_DB'] = 'obj_detect_dev_db'
os.environ['OBJ_DETECT_ENV'] = 'development'

def test_connection():
    """Test MySQL connection"""
    print("Testing MySQL Connection...")
    print("=" * 30)
    
    try:
        # Test basic connection
        from storage import database
        print("SUCCESS: Database module imported")
        
        # Test database reload
        database.reload()
        print("SUCCESS: Database connected and tables created")
        
        # Test basic query
        from storage.object_types import ObjectType
        count = database.count(ObjectType)
        print(f"SUCCESS: Found {count} object types in database")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    if success:
        print("\n🎉 MySQL connection test PASSED!")
    else:
        print("\n❌ MySQL connection test FAILED!")
        print("\nTroubleshooting steps:")
        print("1. Make sure MySQL service is running")
        print("2. Check if databases exist")
        print("3. Verify credentials")
