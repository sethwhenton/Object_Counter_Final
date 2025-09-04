#!/usr/bin/python3
"""Test MySQL connection and basic database operations - Fixed Version"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set environment variables for testing
os.environ['OBJ_DETECT_MYSQL_USER'] = 'obj_detect_dev'
os.environ['OBJ_DETECT_MYSQL_PWD'] = 'obj_detect_dev_pwd'
os.environ['OBJ_DETECT_MYSQL_HOST'] = 'localhost'
os.environ['OBJ_DETECT_MYSQL_DB'] = 'obj_detect_dev_db'
os.environ['OBJ_DETECT_ENV'] = 'development'

try:
    # Import our storage modules
    from storage.engine.engine import Engine
    from storage.base_model import Base
    from storage.object_types import ObjectType
    from storage.inputs import Input
    from storage.outputs import Output
    
    print("Testing MySQL Connection...")
    
    # Create engine instance
    engine = Engine()
    print("SUCCESS: Engine created successfully")
    
    # Test database connection
    engine.reload()
    print("SUCCESS: Database connection established")
    
    # Test creating a simple object type
    print("Testing object creation...")
    
    # Create a test object type
    test_object = ObjectType()
    test_object.name = "test_object"
    test_object.description = "Test object for connection verification"
    
    # Save to database using engine directly
    engine.new(test_object)
    engine.save()
    print("SUCCESS: Test object created and saved successfully")
    
    # Retrieve the object
    retrieved_object = engine.get(ObjectType, id=test_object.id)
    if retrieved_object:
        print(f"SUCCESS: Object retrieved successfully: {retrieved_object.name}")
    else:
        print("ERROR: Failed to retrieve object")
    
    # Clean up test object
    engine.delete(retrieved_object)
    print("SUCCESS: Test object cleaned up")
    
    print("\nSUCCESS: MySQL connection test completed successfully!")
    print("SUCCESS: Database is ready for the application")
    
except ImportError as e:
    print(f"ERROR: Import error: {e}")
    print("TIP: Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"ERROR: Database connection failed: {e}")
    print("TIP: Make sure MySQL is running and the database is created")
    print("TIP: Run: python backend/setup_mysql.py")
    sys.exit(1)
