#!/usr/bin/python3
"""Complete Setup Test Script - Windows Compatible"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test basic imports
        import flask
        print("SUCCESS: Flask imported")
        
        import pymysql
        print("SUCCESS: PyMySQL imported")
        
        import sqlalchemy
        print("SUCCESS: SQLAlchemy imported")
        
        import cryptography
        print("SUCCESS: Cryptography imported")
        
        return True
    except ImportError as e:
        print(f"ERROR: Import failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        # Set environment variables
        os.environ['OBJ_DETECT_MYSQL_USER'] = 'obj_detect_dev'
        os.environ['OBJ_DETECT_MYSQL_PWD'] = 'obj_detect_dev_pwd'
        os.environ['OBJ_DETECT_MYSQL_HOST'] = 'localhost'
        os.environ['OBJ_DETECT_MYSQL_DB'] = 'obj_detect_dev_db'
        os.environ['OBJ_DETECT_ENV'] = 'development'
        
        # Import and test
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from storage.engine.engine import Engine
        
        engine = Engine()
        engine.reload()
        print("SUCCESS: Database connection established")
        
        return True
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        return False

def main():
    """Main test function"""
    print("AI Object Counting System - Setup Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\nERROR: Import test failed")
        print("TIP: Run: pip install -r requirements.txt")
        return False
    
    # Test database
    if not test_database_connection():
        print("\nERROR: Database test failed")
        print("TIP: Run: python backend/setup_mysql.py")
        return False
    
    print("\nSUCCESS: All tests passed!")
    print("Your development environment is ready!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


