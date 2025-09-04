#!/usr/bin/python3
"""Test Database Functions - MySQL Version
Test the new database functions that work with MySQL models
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

# Import the new database functions
from storage.database_functions import (
    init_database, get_object_type_by_name, save_prediction_result,
    update_correction, get_all_object_types, get_all_outputs,
    get_output_by_id, delete_output, count_outputs, count_object_types
)


def test_database_functions():
    """Test all the new database functions"""
    print("Database Functions Test Suite")
    print("=" * 50)
    
    try:
        # Test 1: Initialize database
        print("\nTest 1: Initialize Database")
        print("-" * 30)
        init_database()
        print("SUCCESS: Database initialized")
        
        # Test 2: Get object types
        print("\nTest 2: Get Object Types")
        print("-" * 30)
        object_types = get_all_object_types()
        print(f"SUCCESS: Found {len(object_types)} object types")
        for obj_type in object_types[:3]:  # Show first 3
            print(f"  - {obj_type.name}: {obj_type.description}")
        
        # Test 3: Get object type by name
        print("\nTest 3: Get Object Type by Name")
        print("-" * 30)
        car_type = get_object_type_by_name('car')
        if car_type:
            print(f"SUCCESS: Found car type - {car_type.name}: {car_type.description}")
        else:
            print("ERROR: Car type not found")
        
        # Test 4: Save prediction result
        print("\nTest 4: Save Prediction Result")
        print("-" * 30)
        test_image_path = f"test_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        output_record = save_prediction_result(
            image_path=test_image_path,
            object_type_name='car',
            predicted_count=5,
            description='Test prediction',
            pred_confidence=0.92
        )
        print(f"SUCCESS: Saved prediction result")
        print(f"  - Output ID: {output_record.id}")
        print(f"  - Predicted count: {output_record.predicted_count}")
        print(f"  - Confidence: {output_record.pred_confidence}")
        
        # Test 5: Get output by ID
        print("\nTest 5: Get Output by ID")
        print("-" * 30)
        retrieved_output = get_output_by_id(output_record.id)
        if retrieved_output:
            print(f"SUCCESS: Retrieved output {retrieved_output.id}")
            print(f"  - Predicted count: {retrieved_output.predicted_count}")
            print(f"  - Confidence: {retrieved_output.pred_confidence}")
        else:
            print("ERROR: Could not retrieve output")
        
        # Test 6: Update correction
        print("\nTest 6: Update Correction")
        print("-" * 30)
        updated_output = update_correction(output_record.id, 7)
        if updated_output:
            print(f"SUCCESS: Updated correction")
            print(f"  - Predicted count: {updated_output.predicted_count}")
            print(f"  - Corrected count: {updated_output.corrected_count}")
        else:
            print("ERROR: Could not update correction")
        
        # Test 7: Count records
        print("\nTest 7: Count Records")
        print("-" * 30)
        output_count = count_outputs()
        object_type_count = count_object_types()
        print(f"SUCCESS: Counts retrieved")
        print(f"  - Outputs: {output_count}")
        print(f"  - Object types: {object_type_count}")
        
        # Test 8: Get all outputs
        print("\nTest 8: Get All Outputs")
        print("-" * 30)
        all_outputs = get_all_outputs()
        print(f"SUCCESS: Retrieved {len(all_outputs)} outputs")
        
        # Test 9: Cleanup - Delete test output
        print("\nTest 9: Cleanup - Delete Test Output")
        print("-" * 30)
        delete_success = delete_output(output_record.id)
        if delete_success:
            print("SUCCESS: Test output deleted")
        else:
            print("ERROR: Could not delete test output")
        
        print("\n" + "=" * 50)
        print("SUCCESS: All database function tests passed!")
        print("Database functions are working correctly with MySQL models")
        
    except Exception as e:
        print(f"\nERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = test_database_functions()
    if success:
        print("\n🎉 All tests passed! Database functions are ready for production.")
    else:
        print("\n❌ Tests failed! Please check the errors above.")
        sys.exit(1)
