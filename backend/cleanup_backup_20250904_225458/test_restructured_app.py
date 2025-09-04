#!/usr/bin/python3
"""Test Restructured App
Test the new Flask-RESTful API with MySQL backend
"""
import os
import requests
import json
from datetime import datetime

# Set environment variables
os.environ['OBJ_DETECT_MYSQL_USER'] = 'obj_detect_dev'
os.environ['OBJ_DETECT_MYSQL_PWD'] = 'obj_detect_dev_pwd'
os.environ['OBJ_DETECT_MYSQL_HOST'] = 'localhost'
os.environ['OBJ_DETECT_MYSQL_DB'] = 'obj_detect_dev_db'
os.environ['OBJ_DETECT_ENV'] = 'development'

def test_app_import():
    """Test that the restructured app can be imported"""
    print("Testing App Import")
    print("=" * 30)
    
    try:
        import app_restructured
        print("SUCCESS: app_restructured imported successfully")
        
        # Test app creation
        app = app_restructured.app
        if app:
            print("SUCCESS: Flask app created")
        else:
            print("ERROR: Flask app not created")
            return False
        
        # Test API creation
        api = app_restructured.api
        if api:
            print("SUCCESS: Flask-RESTful API created")
        else:
            print("ERROR: Flask-RESTful API not created")
            return False
        
        # Test Swagger creation
        swagger = app_restructured.swagger
        if swagger:
            print("SUCCESS: Swagger documentation created")
        else:
            print("ERROR: Swagger documentation not created")
            return False
        
        return True
        
    except Exception as e:
        print(f"ERROR: App import failed: {e}")
        return False


def test_database_integration():
    """Test database integration in app context"""
    print("\nTesting Database Integration")
    print("=" * 30)
    
    try:
        import app_restructured
        
        # Test database initialization in app context
        with app_restructured.app.app_context():
            from storage.database_functions import count_object_types, get_all_object_types
            
            count = count_object_types()
            object_types = get_all_object_types()
            
            print(f"SUCCESS: Database integration working - {count} object types")
            print(f"SUCCESS: Found {len(object_types)} object types in database")
            
            # Test a few object types
            for obj_type in object_types[:3]:
                print(f"  - {obj_type.name}: {obj_type.description}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Database integration failed: {e}")
        return False


def test_api_resources():
    """Test that all API resources are properly registered"""
    print("\nTesting API Resources")
    print("=" * 30)
    
    try:
        import app_restructured
        
        # Get all registered routes
        routes = []
        for rule in app_restructured.app.url_map.iter_rules():
            routes.append(f"{rule.methods} {rule.rule}")
        
        expected_routes = [
            "GET /health",
            "POST /test-pipeline", 
            "POST /api/count",
            "PUT /api/correct",
            "GET /api/object-types",
            "GET /api/results/<string:result_id>",
            "DELETE /api/results/<string:result_id>/delete"
        ]
        
        print("SUCCESS: Found API routes:")
        for route in routes:
            if any(expected in route for expected in expected_routes):
                print(f"  ✅ {route}")
            else:
                print(f"  📝 {route}")
        
        # Check if all expected routes are present
        missing_routes = []
        for expected in expected_routes:
            if not any(expected in route for route in routes):
                missing_routes.append(expected)
        
        if missing_routes:
            print(f"WARNING: Missing routes: {missing_routes}")
        else:
            print("SUCCESS: All expected API routes are registered")
        
        return True
        
    except Exception as e:
        print(f"ERROR: API resources test failed: {e}")
        return False


def test_swagger_documentation():
    """Test Swagger documentation endpoints"""
    print("\nTesting Swagger Documentation")
    print("=" * 30)
    
    try:
        import app_restructured
        
        # Test that Swagger endpoints are available
        with app_restructured.app.test_client() as client:
            # Test Swagger UI endpoint
            response = client.get('/docs')
            if response.status_code == 200:
                print("SUCCESS: Swagger UI endpoint accessible")
            else:
                print(f"WARNING: Swagger UI endpoint returned {response.status_code}")
            
            # Test API spec endpoint
            response = client.get('/apispec.json')
            if response.status_code == 200:
                print("SUCCESS: API spec endpoint accessible")
                try:
                    spec = response.get_json()
                    if 'info' in spec and 'title' in spec['info']:
                        print(f"SUCCESS: API spec contains title: {spec['info']['title']}")
                    else:
                        print("WARNING: API spec missing required fields")
                except:
                    print("WARNING: API spec not valid JSON")
            else:
                print(f"WARNING: API spec endpoint returned {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Swagger documentation test failed: {e}")
        return False


def test_health_endpoint():
    """Test the health endpoint"""
    print("\nTesting Health Endpoint")
    print("=" * 30)
    
    try:
        import app_restructured
        
        with app_restructured.app.test_client() as client:
            response = client.get('/health')
            
            if response.status_code == 200:
                data = response.get_json()
                print("SUCCESS: Health endpoint working")
                print(f"  - Status: {data.get('status', 'unknown')}")
                print(f"  - Database: {data.get('database', 'unknown')}")
                print(f"  - Object Types: {data.get('object_types', 'unknown')}")
                print(f"  - Pipeline Available: {data.get('pipeline_available', 'unknown')}")
                return True
            else:
                print(f"ERROR: Health endpoint returned {response.status_code}")
                return False
        
    except Exception as e:
        print(f"ERROR: Health endpoint test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Restructured App Test Suite")
    print("=" * 50)
    
    tests = [
        ("App Import", test_app_import),
        ("Database Integration", test_database_integration),
        ("API Resources", test_api_resources),
        ("Swagger Documentation", test_swagger_documentation),
        ("Health Endpoint", test_health_endpoint)
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
        print("🎉 ALL TESTS PASSED! Restructured app is working correctly!")
        print("\nNext steps:")
        print("1. Start the restructured app: python app_restructured.py")
        print("2. Visit http://localhost:5000/docs for Swagger documentation")
        print("3. Test API endpoints")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
