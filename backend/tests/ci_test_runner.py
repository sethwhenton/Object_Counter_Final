#!/usr/bin/python3
"""CI/CD Test Runner
Specialized test runner for GitLab CI/CD pipeline with JUnit XML output
"""
import os
import sys
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime
from io import StringIO

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_ci_environment():
    """Set up CI environment variables"""
    print("🔧 Setting up CI environment...")
    
    # Set CI-specific environment variables
    os.environ['OBJ_DETECT_ENV'] = 'test'
    os.environ['OBJ_DETECT_MYSQL_USER'] = os.environ.get('OBJ_DETECT_MYSQL_USER', 'root')
    os.environ['OBJ_DETECT_MYSQL_PWD'] = os.environ.get('OBJ_DETECT_MYSQL_PWD', 'root')
    os.environ['OBJ_DETECT_MYSQL_HOST'] = os.environ.get('OBJ_DETECT_MYSQL_HOST', 'mysql')
    os.environ['OBJ_DETECT_MYSQL_DB'] = os.environ.get('OBJ_DETECT_MYSQL_DB', 'obj_detect_test_db')
    
    print("✅ CI environment configured")

def generate_junit_xml(test_result, output_file='test-results.xml'):
    """Generate JUnit XML report from test results"""
    print(f"📊 Generating JUnit XML report: {output_file}")
    
    # Create root element
    root = ET.Element('testsuite')
    root.set('name', 'Object Counting API Tests')
    root.set('tests', str(test_result.testsRun))
    root.set('failures', str(len(test_result.failures)))
    root.set('errors', str(len(test_result.errors)))
    root.set('skipped', str(len(test_result.skipped)))
    root.set('time', str(test_result.testsRun * 0.1))  # Estimated time
    
    # Add test cases
    for test_case, traceback in test_result.failures + test_result.errors:
        test_elem = ET.SubElement(root, 'testcase')
        test_elem.set('name', test_case._testMethodName)
        test_elem.set('classname', test_case.__class__.__module__ + '.' + test_case.__class__.__name__)
        test_elem.set('time', '0.1')
        
        if (test_case, traceback) in test_result.failures:
            failure = ET.SubElement(test_elem, 'failure')
            failure.set('message', 'Test failed')
            failure.text = traceback
        else:
            error = ET.SubElement(test_elem, 'error')
            error.set('message', 'Test error')
            error.text = traceback
    
    # Add successful test cases
    for test_case in test_result.testsRun:
        if not any(test_case == failed[0] for failed in test_result.failures + test_result.errors):
            test_elem = ET.SubElement(root, 'testcase')
            test_elem.set('name', test_case._testMethodName)
            test_elem.set('classname', test_case.__class__.__module__ + '.' + test_case.__class__.__name__)
            test_elem.set('time', '0.1')
    
    # Write XML file
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    
    print(f"✅ JUnit XML report generated: {output_file}")

def run_ci_tests():
    """Run tests for CI/CD pipeline"""
    print("🧪 Running CI/CD Test Suite")
    print("=" * 50)
    
    # Set up environment
    setup_ci_environment()
    
    # Import test modules
    try:
        from tests.test_api import test_inputs, test_outputs, test_object_types
        from tests.test_storage import test_database
        print("✅ Test modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import test modules: {e}")
        return False
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add API tests
    suite.addTests(loader.loadTestsFromModule(test_inputs))
    suite.addTests(loader.loadTestsFromModule(test_outputs))
    suite.addTests(loader.loadTestsFromModule(test_object_types))
    
    # Add storage tests
    suite.addTests(loader.loadTestsFromModule(test_database))
    
    print(f"📋 Test suite created with {suite.countTestCases()} tests")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Generate JUnit XML report
    generate_junit_xml(result)
    
    # Print summary
    print("=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\n❌ Test Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print("\n💥 Test Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\\n')[-2]}")
    
    # Return success status
    success = len(result.failures) == 0 and len(result.errors) == 0
    if success:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n💥 {len(result.failures) + len(result.errors)} tests failed!")
    
    return success

def main():
    """Main CI test runner function"""
    print("🚀 CI/CD Test Runner")
    print(f"📅 Started at: {datetime.now().isoformat()}")
    print("=" * 50)
    
    try:
        success = run_ci_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"💥 CI test runner failed: {e}")
        return 1
    finally:
        print("=" * 50)
        print(f"📅 Completed at: {datetime.now().isoformat()}")

if __name__ == '__main__':
    sys.exit(main())


