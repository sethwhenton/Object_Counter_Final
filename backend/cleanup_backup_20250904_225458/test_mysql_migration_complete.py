#!/usr/bin/python3
"""Complete MySQL Migration Test
Test all components of the MySQL migration to ensure everything works together
"""
import os
import sys
from datetime import datetime

# Set environment variables for MySQL connection
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


def test_app_integration():
    """Test that the new app can be imported and initialized"""
    print("\nTesting App Integration")
    print("=" * 30)
    
    try:
        # Test importing the new app
        import app_mysql
        print("SUCCESS: app_mysql imported successfully")
        
        # Test app initialization
        app = app_mysql.app
        if app:
            print("SUCCESS: Flask app created")
        else:
            print("ERROR: Flask app not created")
            return False
        
        # Test database initialization in app context
        with app.app_context():
            from storage.database_functions import count_object_types
            count = count_object_types()
            print(f"SUCCESS: App context working - {count} object types")
        
        return True
        
    except Exception as e:
        print(f"ERROR: App integration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("MySQL Migration Complete Test Suite")
    print("=" * 50)
    
    tests = [
        ("MySQL Models", test_mysql_models),
        ("Database Functions", test_database_functions),
        ("App Integration", test_app_integration)
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
        print("🎉 ALL TESTS PASSED! MySQL migration is complete and working!")
        print("\nNext steps:")
        print("1. Update app.py to use app_mysql.py")
        print("2. Test the full application")
        print("3. Update frontend integration if needed")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
