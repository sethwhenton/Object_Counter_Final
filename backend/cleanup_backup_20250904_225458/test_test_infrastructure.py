#!/usr/bin/python3
"""Test the Test Infrastructure
Verify that the testing infrastructure is working correctly
"""
import os
import sys
from datetime import datetime

# Set environment variables
os.environ['OBJ_DETECT_MYSQL_USER'] = 'obj_detect_dev'
os.environ['OBJ_DETECT_MYSQL_PWD'] = 'obj_detect_dev_pwd'
os.environ['OBJ_DETECT_MYSQL_HOST'] = 'localhost'
os.environ['OBJ_DETECT_MYSQL_DB'] = 'obj_detect_test_db'
os.environ['OBJ_DETECT_ENV'] = 'test'

def test_test_runner_import():
    """Test that test runner can be imported"""
    print("Testing Test Runner Import")
    print("=" * 30)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
        import test_runner
        print("SUCCESS: test_runner imported successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to import test_runner: {e}")
        return False

def test_test_environment_check():
    """Test environment checking functionality"""
    print("\nTesting Environment Check")
    print("=" * 30)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
        from test_runner import check_test_environment
        
        success = check_test_environment()
        if success:
            print("SUCCESS: Environment check passed")
        else:
            print("ERROR: Environment check failed")
        return success
    except Exception as e:
        print(f"ERROR: Environment check failed: {e}")
        return False

def test_test_database_setup():
    """Test test database setup"""
    print("\nTesting Database Setup")
    print("=" * 30)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
        from test_runner import setup_test_database
        
        success = setup_test_database()
        if success:
            print("SUCCESS: Test database setup completed")
        else:
            print("ERROR: Test database setup failed")
        return success
    except Exception as e:
        print(f"ERROR: Database setup failed: {e}")
        return False

def test_test_modules_import():
    """Test that test modules can be imported"""
    print("\nTesting Test Modules Import")
    print("=" * 30)
    
    try:
        # Test API test modules
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
        
        # Import test modules
        from test_api import test_inputs
        print("SUCCESS: test_inputs imported")
        
        from test_api import test_outputs
        print("SUCCESS: test_outputs imported")
        
        from test_api import test_object_types
        print("SUCCESS: test_object_types imported")
        
        from test_storage import test_database
        print("SUCCESS: test_database imported")
        
        return True
    except Exception as e:
        print(f"ERROR: Failed to import test modules: {e}")
        return False

def test_basic_api_test():
    """Test a basic API test"""
    print("\nTesting Basic API Test")
    print("=" * 30)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
        from test_api.test_inputs import TestInputAPI
        
        # Create test instance
        test_instance = TestInputAPI()
        test_instance.setUpClass()
        
        # Test health endpoint
        response = test_instance.client.get('/health')
        
        if response.status_code == 200:
            print("SUCCESS: Basic API test passed")
            return True
        else:
            print(f"ERROR: API test failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Basic API test failed: {e}")
        return False

def test_basic_storage_test():
    """Test a basic storage test"""
    print("\nTesting Basic Storage Test")
    print("=" * 30)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
        from test_storage.test_database import TestDatabaseOperations
        
        # Create test instance
        test_instance = TestDatabaseOperations()
        test_instance.setUpClass()
        
        # Test database connection
        from storage import database
        from storage.object_types import ObjectType
        
        count = database.count(ObjectType)
        if isinstance(count, int) and count >= 0:
            print("SUCCESS: Basic storage test passed")
            return True
        else:
            print("ERROR: Storage test failed")
            return False
    except Exception as e:
        print(f"ERROR: Basic storage test failed: {e}")
        return False

def main():
    """Run all infrastructure tests"""
    print("Test Infrastructure Verification")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Test Runner Import", test_test_runner_import),
        ("Environment Check", test_test_environment_check),
        ("Database Setup", test_test_database_setup),
        ("Test Modules Import", test_test_modules_import),
        ("Basic API Test", test_basic_api_test),
        ("Basic Storage Test", test_basic_storage_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL INFRASTRUCTURE TESTS PASSED!")
        print("The testing infrastructure is working correctly!")
        print("\nNext steps:")
        print("1. Run full test suite: python tests/test_runner.py --test all")
        print("2. Run specific tests: python tests/test_runner.py --test api")
        print("3. Check environment: python tests/test_runner.py --check-env")
        return True
    else:
        print("❌ Some infrastructure tests failed.")
        print("Please check the errors above and fix any issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
