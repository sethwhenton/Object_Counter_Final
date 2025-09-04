#!/usr/bin/python3
"""Test Runner for Object Counting API
Comprehensive test runner for the restructured MySQL application
"""
import os
import sys
import unittest
import argparse
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests import TEST_CONFIG


def run_api_tests():
    """Run API tests"""
    print("Running API Tests")
    print("=" * 50)
    
    # Discover and run API tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'test_api')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_storage_tests():
    """Run storage tests"""
    print("\nRunning Storage Tests")
    print("=" * 50)
    
    # Discover and run storage tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'test_storage')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_all_tests():
    """Run all tests"""
    print("Running All Tests")
    print("=" * 50)
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_specific_test(test_name):
    """Run a specific test"""
    print(f"Running Specific Test: {test_name}")
    print("=" * 50)
    
    # Import and run specific test
    if test_name == 'api':
        return run_api_tests()
    elif test_name == 'storage':
        return run_storage_tests()
    else:
        print(f"Unknown test: {test_name}")
        return False


def check_test_environment():
    """Check if test environment is properly set up"""
    print("Checking Test Environment")
    print("=" * 30)
    
    issues = []
    
    # Check environment variables
    required_env_vars = [
        'OBJ_DETECT_MYSQL_USER',
        'OBJ_DETECT_MYSQL_PWD',
        'OBJ_DETECT_MYSQL_HOST',
        'OBJ_DETECT_MYSQL_DB',
        'OBJ_DETECT_ENV'
    ]
    
    for var in required_env_vars:
        if not os.environ.get(var):
            issues.append(f"Missing environment variable: {var}")
        else:
            print(f"✅ {var}: {os.environ[var]}")
    
    # Check if test database is configured
    if os.environ.get('OBJ_DETECT_ENV') != 'test':
        issues.append("OBJ_DETECT_ENV should be set to 'test' for testing")
    
    # Check if test database name is correct
    if os.environ.get('OBJ_DETECT_MYSQL_DB') != 'obj_detect_test_db':
        issues.append("Test database should be 'obj_detect_test_db'")
    
    # Check if required modules can be imported
    try:
        import app_restructured
        print("✅ app_restructured imported successfully")
    except ImportError as e:
        issues.append(f"Cannot import app_restructured: {e}")
    
    try:
        from storage import database
        print("✅ storage.database imported successfully")
    except ImportError as e:
        issues.append(f"Cannot import storage.database: {e}")
    
    try:
        from storage.database_functions import init_database
        print("✅ storage.database_functions imported successfully")
    except ImportError as e:
        issues.append(f"Cannot import storage.database_functions: {e}")
    
    if issues:
        print("\n❌ Environment Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("\n✅ Test environment is properly configured")
        return True


def setup_test_database():
    """Set up test database"""
    print("Setting up Test Database")
    print("=" * 30)
    
    try:
        from storage.database_functions import init_database
        init_database()
        print("✅ Test database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize test database: {e}")
        return False


def cleanup_test_database():
    """Clean up test database"""
    print("Cleaning up Test Database")
    print("=" * 30)
    
    try:
        from storage.database_functions import get_all_outputs, delete_output
        from storage import database
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        # Clean up test outputs
        outputs = get_all_outputs()
        test_outputs = [output for output in outputs if 'test_' in str(output.id)]
        
        for output in test_outputs:
            try:
                delete_output(output.id)
            except:
                pass
        
        # Clean up test object types
        object_types = database.get_all(ObjectType)
        test_types = [obj_type for obj_type in object_types if 'test_' in obj_type.name]
        
        for obj_type in test_types:
            try:
                database.delete(obj_type)
            except:
                pass
        
        # Clean up test inputs
        inputs = database.get_all(Input)
        test_inputs = [input_record for input_record in inputs if 'test_' in input_record.image_path]
        
        for input_record in test_inputs:
            try:
                database.delete(input_record)
            except:
                pass
        
        print(f"✅ Cleaned up {len(test_outputs)} test outputs, {len(test_types)} test object types, {len(test_inputs)} test inputs")
        return True
        
    except Exception as e:
        print(f"❌ Failed to cleanup test database: {e}")
        return False


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Run tests for Object Counting API')
    parser.add_argument('--test', choices=['api', 'storage', 'all'], default='all',
                       help='Type of tests to run')
    parser.add_argument('--check-env', action='store_true',
                       help='Check test environment setup')
    parser.add_argument('--setup-db', action='store_true',
                       help='Set up test database')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up test database')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    print("Object Counting API Test Runner")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test type: {args.test}")
    print()
    
    # Check environment if requested
    if args.check_env:
        if not check_test_environment():
            print("\n❌ Environment check failed. Please fix the issues above.")
            return 1
        return 0
    
    # Set up test database if requested
    if args.setup_db:
        if not setup_test_database():
            print("\n❌ Database setup failed.")
            return 1
        return 0
    
    # Clean up test database if requested
    if args.cleanup:
        if not cleanup_test_database():
            print("\n❌ Database cleanup failed.")
            return 1
        return 0
    
    # Check environment before running tests
    if not check_test_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        return 1
    
    # Set up test database
    if not setup_test_database():
        print("\n❌ Database setup failed.")
        return 1
    
    # Run tests
    success = False
    
    try:
        if args.test == 'api':
            success = run_api_tests()
        elif args.test == 'storage':
            success = run_storage_tests()
        elif args.test == 'all':
            success = run_all_tests()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 All tests passed!")
        else:
            print("❌ Some tests failed!")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ Test runner error: {e}")
        return 1
    
    finally:
        # Clean up test database
        cleanup_test_database()


if __name__ == '__main__':
    sys.exit(main())


