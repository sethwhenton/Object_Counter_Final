#!/usr/bin/python3
"""CI/CD Database Setup Script
Sets up MySQL database for GitLab CI/CD pipeline testing
"""
import os
import sys
import time
import pymysql
from datetime import datetime

def wait_for_mysql(max_retries=30, delay=2):
    """Wait for MySQL to be ready"""
    print("🔄 Waiting for MySQL to be ready...")
    
    for attempt in range(max_retries):
        try:
            connection = pymysql.connect(
                host=os.environ.get('OBJ_DETECT_MYSQL_HOST', 'mysql'),
                user=os.environ.get('OBJ_DETECT_MYSQL_USER', 'root'),
                password=os.environ.get('OBJ_DETECT_MYSQL_PWD', 'root'),
                database=os.environ.get('OBJ_DETECT_MYSQL_DB', 'obj_detect_test_db'),
                connect_timeout=5
            )
            connection.close()
            print("✅ MySQL is ready!")
            return True
        except Exception as e:
            print(f"⏳ Attempt {attempt + 1}/{max_retries}: MySQL not ready yet ({e})")
            time.sleep(delay)
    
    print("❌ MySQL failed to become ready within timeout")
    return False

def setup_test_database():
    """Set up test database and initialize with required data"""
    print("🔧 Setting up test database...")
    
    try:
        # Set up environment variables for CI
        os.environ['OBJ_DETECT_ENV'] = 'test'
        os.environ['OBJ_DETECT_MYSQL_USER'] = os.environ.get('OBJ_DETECT_MYSQL_USER', 'root')
        os.environ['OBJ_DETECT_MYSQL_PWD'] = os.environ.get('OBJ_DETECT_MYSQL_PWD', 'root')
        os.environ['OBJ_DETECT_MYSQL_HOST'] = os.environ.get('OBJ_DETECT_MYSQL_HOST', 'mysql')
        os.environ['OBJ_DETECT_MYSQL_DB'] = os.environ.get('OBJ_DETECT_MYSQL_DB', 'obj_detect_test_db')
        
        # Import and initialize database
        from storage.database_functions import init_database
        init_database()
        
        print("✅ Test database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to set up test database: {e}")
        return False

def verify_database_setup():
    """Verify that database is properly set up"""
    print("🔍 Verifying database setup...")
    
    try:
        from storage.database_functions import get_all_object_types, count_outputs
        
        # Check object types
        object_types = get_all_object_types()
        print(f"✅ Found {len(object_types)} object types")
        
        # Check outputs count
        output_count = count_outputs()
        print(f"✅ Database has {output_count} outputs")
        
        # Verify required object types exist
        required_types = ['car', 'person', 'dog', 'cat', 'tree']
        existing_types = [ot.name for ot in object_types]
        
        for required_type in required_types:
            if required_type in existing_types:
                print(f"✅ Object type '{required_type}' exists")
            else:
                print(f"⚠️  Object type '{required_type}' missing")
        
        print("✅ Database verification completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting CI/CD Database Setup")
    print(f"📅 Started at: {datetime.now().isoformat()}")
    print("=" * 50)
    
    # Step 1: Wait for MySQL
    if not wait_for_mysql():
        sys.exit(1)
    
    # Step 2: Set up test database
    if not setup_test_database():
        sys.exit(1)
    
    # Step 3: Verify setup
    if not verify_database_setup():
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 CI/CD Database Setup Completed Successfully!")
    print(f"📅 Completed at: {datetime.now().isoformat()}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())


