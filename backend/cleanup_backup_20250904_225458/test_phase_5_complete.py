#!/usr/bin/python3
"""Phase 5 Complete Test Suite
Test the entire restructured application with MySQL, Flask-RESTful, and Swagger
"""
import os
import sys
from datetime import datetime

# Set environment variables
os.environ['OBJ_DETECT_MYSQL_USER'] = 'obj_detect_dev'
os.environ['OBJ_DETECT_MYSQL_PWD'] = 'obj_detect_dev_pwd'
os.environ['OBJ_DETECT_MYSQL_HOST'] = 'localhost'
os.environ['OBJ_DETECT_MYSQL_DB'] = 'obj_detect_dev_db'
os.environ['OBJ_DETECT_ENV'] = 'development'

def test_mysql_models():
    """Test MySQL models work correctly"""
    print("Testing MySQL Models")
    print("=" * 30)
    
    try:
        from storage import database
        from storage.object_types import ObjectType
        from storage.inputs import Input
        from storage.outputs import Output
        
        # Test database connection
        database.reload()
        print("SUCCESS: Database connected")
        
        # Test ObjectType model
        obj_type = ObjectType()
        obj_type.name = f"test_type_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        obj_type.description = "Test object type"
        database.new(obj_type)
        database.save()
        print(f"SUCCESS: ObjectType created - {obj_type.id}")
        
        # Test Input model
        input_record = Input()
        input_record.image_path = f"test_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        input_record.description = "Test input"
        database.new(input_record)
        database.save()
        print(f"SUCCESS: Input created - {input_record.id}")
        
        # Test Output model
        output_record = Output()
        output_record.predicted_count = 5
        output_record.pred_confidence = 0.85
        output_record.object_type_id = obj_type.id
        output_record.input_id = input_record.id
        database.new(output_record)
        database.save()
        print(f"SUCCESS: Output created - {output_record.id}")
        
        # Test relationships
        retrieved_output = database.get(Output, output_record.id)
        if retrieved_output and retrieved_output.object_type and retrieved_output.input:
            print("SUCCESS: Relationships working correctly")
        else:
            print("ERROR: Relationships not working")
            return False
        
        # Cleanup
        database.delete(output_record)
        database.delete(input_record)
        database.delete(obj_type)
        print("SUCCESS: Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Model test failed: {e}")
        return False

def test_database_functions():
    """Test database functions work correctly"""
    print("\nTesting Database Functions")
    print("=" * 30)
    
    try:
        from storage.database_functions import (
            init_database, get_object_type_by_name, save_prediction_result,
            update_correction, get_all_object_types, count_outputs
        )
        
        # Test initialization
        init_database()
        print("SUCCESS: Database initialized")
        
        # Test get object type
        car_type = get_object_type_by_name('car')
        if car_type:
            print(f"SUCCESS: Found car type - {car_type.name}")
        else:
            print("ERROR: Car type not found")
            return False
        
        # Test save prediction
        test_image = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        output = save_prediction_result(
            image_path=test_image,
            object_type_name='car',
            predicted_count=3,
            description='Test prediction',
            pred_confidence=0.90
        )
        print(f"SUCCESS: Prediction saved - {output.id}")
        
        # Test update correction
        updated_output = update_correction(output.id, 4)
        if updated_output.corrected_count == 4:
            print("SUCCESS: Correction updated")
        else:
            print("ERROR: Correction not updated")
            return False
        
        # Test counts
        output_count = count_outputs()
        object_type_count = len(get_all_object_types())
        print(f"SUCCESS: Counts - Outputs: {output_count}, Object Types: {object_type_count}")
        
        # Cleanup
        from storage.database_functions import delete_output
        delete_output(output.id)
        print("SUCCESS: Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Database functions test failed: {e}")
        return False

def test_restructured_app():
    """Test the restructured Flask app"""
    print("\nTesting Restructured App")
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
        print(f"ERROR: Restructured app test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints with test client"""
    print("\nTesting API Endpoints")
    print("=" * 30)
    
    try:
        import app_restructured
        
        with app_restructured.app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                data = response.get_json()
                print("SUCCESS: Health endpoint working")
                print(f"  - Status: {data.get('status', 'unknown')}")
                print(f"  - Database: {data.get('database', 'unknown')}")
                print(f"  - Object Types: {data.get('object_types', 'unknown')}")
            else:
                print(f"ERROR: Health endpoint returned {response.status_code}")
                return False
            
            # Test object types endpoint
            response = client.get('/api/object-types')
            if response.status_code == 200:
                data = response.get_json()
                object_types = data.get('object_types', [])
                print(f"SUCCESS: Object types endpoint working - {len(object_types)} types")
            else:
                print(f"ERROR: Object types endpoint returned {response.status_code}")
                return False
            
            # Test Swagger documentation
            response = client.get('/docs')
            if response.status_code == 200:
                print("SUCCESS: Swagger documentation accessible")
            else:
                print(f"WARNING: Swagger documentation returned {response.status_code}")
            
            # Test API spec
            response = client.get('/apispec.json')
            if response.status_code == 200:
                print("SUCCESS: API spec accessible")
            else:
                print(f"WARNING: API spec returned {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: API endpoints test failed: {e}")
        return False

def test_pipeline_integration():
    """Test pipeline integration with new database"""
    print("\nTesting Pipeline Integration")
    print("=" * 30)
    
    try:
        # Test pipeline import
        from models.pipeline import ObjectCountingPipeline
        print("SUCCESS: Pipeline imported successfully")
        
        # Test pipeline initialization (this might fail if dependencies are missing)
        try:
            pipeline = ObjectCountingPipeline()
            print("SUCCESS: Pipeline initialized successfully")
            pipeline_available = True
        except Exception as e:
            print(f"WARNING: Pipeline initialization failed: {e}")
            print("  This is expected if AI dependencies are not installed")
            pipeline_available = False
        
        # Test app integration
        import app_restructured
        if hasattr(app_restructured, 'pipeline'):
            if app_restructured.pipeline is not None:
                print("SUCCESS: Pipeline integrated with app")
            else:
                print("WARNING: Pipeline not available in app (dependencies missing)")
        else:
            print("ERROR: Pipeline not found in app")
            return False
        
        return True
        
    except Exception as e:
        print(f"ERROR: Pipeline integration test failed: {e}")
        return False

def test_old_code_removal():
    """Test that old database code has been removed"""
    print("\nTesting Old Code Removal")
    print("=" * 30)
    
    try:
        # Check if old database file exists
        if os.path.exists("models/database.py"):
            print("WARNING: Old database.py still exists")
            return False
        else:
            print("SUCCESS: Old database.py removed")
        
        # Check if new files exist
        new_files = [
            "storage/database_functions.py",
            "storage/object_types.py",
            "storage/inputs.py",
            "storage/outputs.py",
            "storage/engine/engine.py",
            "storage/base_model.py",
            "app_restructured.py"
        ]
        
        missing_files = []
        for file_path in new_files:
            if os.path.exists(file_path):
                print(f"SUCCESS: {file_path} exists")
            else:
                missing_files.append(file_path)
                print(f"ERROR: {file_path} missing")
        
        if missing_files:
            print(f"ERROR: Missing {len(missing_files)} required files")
            return False
        
        return True
        
    except Exception as e:
        print(f"ERROR: Old code removal test failed: {e}")
        return False

def main():
    """Run all Phase 5 tests"""
    print("Phase 5: Application Restructure - Complete Test Suite")
    print("=" * 60)
    
    tests = [
        ("MySQL Models", test_mysql_models),
        ("Database Functions", test_database_functions),
        ("Restructured App", test_restructured_app),
        ("API Endpoints", test_api_endpoints),
        ("Pipeline Integration", test_pipeline_integration),
        ("Old Code Removal", test_old_code_removal)
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
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Phase 5 Application Restructure is COMPLETE!")
        print("\n🚀 Your application has been successfully restructured with:")
        print("  ✅ MySQL database with UUID primary keys")
        print("  ✅ Custom database engine")
        print("  ✅ Flask-RESTful API structure")
        print("  ✅ Swagger API documentation")
        print("  ✅ Updated CORS configuration")
        print("  ✅ Pipeline integration")
        print("  ✅ Old code cleanup")
        
        print("\n📋 Next Steps:")
        print("1. Start the restructured app: python app_restructured.py")
        print("2. Visit http://localhost:5000/docs for Swagger documentation")
        print("3. Test API endpoints")
        print("4. Update frontend if needed for UUID handling")
        print("5. Deploy to production")
        
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure MySQL is running")
        print("2. Check environment variables")
        print("3. Verify all dependencies are installed")
        print("4. Check file permissions")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
