#!/usr/bin/python3
"""Output Model Migration Utility"""

import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variables
os.environ['OBJ_DETECT_MYSQL_USER'] = os.getenv('OBJ_DETECT_MYSQL_USER', 'obj_detect_dev')
os.environ['OBJ_DETECT_MYSQL_PWD'] = os.getenv('OBJ_DETECT_MYSQL_PWD', 'obj_detect_dev_pwd')
os.environ['OBJ_DETECT_MYSQL_HOST'] = os.getenv('OBJ_DETECT_MYSQL_HOST', 'localhost')
os.environ['OBJ_DETECT_MYSQL_DB'] = os.getenv('OBJ_DETECT_MYSQL_DB', 'obj_detect_dev_db')
os.environ['OBJ_DETECT_ENV'] = os.getenv('OBJ_DETECT_ENV', 'development')

def create_sample_outputs():
    """Create sample outputs for testing"""
    print("Creating Sample Outputs...")
    print("=" * 40)
    
    try:
        from storage.engine.engine import Engine
        from storage.outputs import Output
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        engine = Engine()
        engine.reload()
        
        # Get existing object types
        object_types = engine.get_all(ObjectType)
        if not object_types:
            print("ERROR: No object types found. Please create object types first.")
            return False
        
        # Get existing inputs or create test inputs
        inputs = engine.get_all(Input)
        if not inputs:
            print("Creating test inputs...")
            test_inputs = [
                {"path": "/test/images/cars_parking.jpg", "desc": "Cars in parking lot"},
                {"path": "/test/images/people_crowd.jpg", "desc": "People in crowd"},
                {"path": "/test/images/bottles_table.jpg", "desc": "Bottles on table"}
            ]
            
            for input_data in test_inputs:
                test_input = Input()
                test_input.image_path = input_data["path"]
                test_input.description = input_data["desc"]
                engine.new(test_input)
            engine.save()
            inputs = engine.get_all(Input)
        
        # Create sample outputs
        sample_outputs = [
            {
                "predicted_count": 5,
                "corrected_count": 7,
                "confidence": 0.85,
                "object_type": "person",
                "input_desc": "People in crowd"
            },
            {
                "predicted_count": 12,
                "corrected_count": None,
                "confidence": 0.92,
                "object_type": "car",
                "input_desc": "Cars in parking lot"
            },
            {
                "predicted_count": 3,
                "corrected_count": 3,
                "confidence": 0.78,
                "object_type": "bottle",
                "input_desc": "Bottles on table"
            },
            {
                "predicted_count": 1,
                "corrected_count": None,
                "confidence": 0.99,
                "object_type": "person",
                "input_desc": "People in crowd"
            }
        ]
        
        created_count = 0
        for output_data in sample_outputs:
            # Find matching object type
            obj_type = None
            for ot in object_types:
                if ot.name == output_data["object_type"]:
                    obj_type = ot
                    break
            
            if not obj_type:
                print(f"WARNING: Object type '{output_data['object_type']}' not found, skipping")
                continue
            
            # Find matching input
            matching_input = None
            for inp in inputs:
                if output_data["input_desc"] in inp.description:
                    matching_input = inp
                    break
            
            if not matching_input:
                print(f"WARNING: No matching input found for '{output_data['input_desc']}', skipping")
                continue
            
            # Create output
            output = Output()
            output.predicted_count = output_data["predicted_count"]
            output.corrected_count = output_data["corrected_count"]
            output.pred_confidence = output_data["confidence"]
            output.object_type_id = obj_type.id
            output.input_id = matching_input.id
            
            engine.new(output)
            created_count += 1
            print(f"Created: {output_data['object_type']} - {output_data['predicted_count']} objects, {output_data['confidence']*100}% confidence")
        
        if created_count > 0:
            engine.save()
            print(f"\nSUCCESS: Created {created_count} sample outputs")
        else:
            print("\nINFO: No sample outputs created")
        
        # Show all outputs
        all_outputs = engine.get_all(Output)
        print(f"\nTotal outputs in database: {len(all_outputs)}")
        for output in all_outputs:
            obj_type_name = "Unknown"
            for ot in object_types:
                if ot.id == output.object_type_id:
                    obj_type_name = ot.name
                    break
            
            correction_info = f" (corrected: {output.corrected_count})" if output.corrected_count else ""
            print(f"  - {obj_type_name}: {output.predicted_count} objects, {output.pred_confidence*100:.1f}% confidence{correction_info}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create sample outputs: {e}")
        return False

def verify_outputs():
    """Verify outputs are working correctly"""
    print("\nVerifying Outputs...")
    print("=" * 40)
    
    try:
        from storage.engine.engine import Engine
        from storage.outputs import Output
        from storage.object_types import ObjectType
        from storage.inputs import Input
        
        engine = Engine()
        engine.reload()  # Initialize the session
        
        # Test basic operations
        all_outputs = engine.get_all(Output)
        print(f"Found {len(all_outputs)} outputs")
        
        if all_outputs:
            # Test getting by ID
            first_output = all_outputs[0]
            retrieved = engine.get(Output, id=first_output.id)
            if retrieved:
                print(f"SUCCESS: Retrieved by ID: {retrieved.id}")
            else:
                print("ERROR: Failed to retrieve by ID")
                return False
            
            # Test relationships
            obj_type = engine.get(ObjectType, id=first_output.object_type_id)
            if obj_type:
                print(f"SUCCESS: Found related ObjectType: {obj_type.name}")
            else:
                print("ERROR: Failed to find related ObjectType")
                return False
            
            input_obj = engine.get(Input, id=first_output.input_id)
            if input_obj:
                print(f"SUCCESS: Found related Input: {input_obj.image_path}")
            else:
                print("ERROR: Failed to find related Input")
                return False
        
        print("SUCCESS: Output verification passed")
        return True
        
    except Exception as e:
        print(f"ERROR: Output verification failed: {e}")
        return False

def analyze_outputs():
    """Analyze output data"""
    print("\nAnalyzing Output Data...")
    print("=" * 40)
    
    try:
        from storage.engine.engine import Engine
        from storage.outputs import Output
        from storage.object_types import ObjectType
        
        engine = Engine()
        engine.reload()  # Initialize the session
        
        outputs = engine.get_all(Output)
        object_types = engine.get_all(ObjectType)
        
        if not outputs:
            print("No outputs to analyze")
            return True
        
        # Create object type lookup
        obj_type_lookup = {ot.id: ot.name for ot in object_types}
        
        # Analyze by object type
        by_object_type = {}
        total_confidence = 0
        corrected_count = 0
        
        for output in outputs:
            obj_type_name = obj_type_lookup.get(output.object_type_id, "Unknown")
            if obj_type_name not in by_object_type:
                by_object_type[obj_type_name] = {
                    "count": 0,
                    "total_predicted": 0,
                    "total_corrected": 0,
                    "confidence_sum": 0
                }
            
            by_object_type[obj_type_name]["count"] += 1
            by_object_type[obj_type_name]["total_predicted"] += output.predicted_count
            by_object_type[obj_type_name]["confidence_sum"] += output.pred_confidence
            
            if output.corrected_count is not None:
                by_object_type[obj_type_name]["total_corrected"] += output.corrected_count
                corrected_count += 1
            
            total_confidence += output.pred_confidence
        
        # Print analysis
        print(f"Total outputs: {len(outputs)}")
        print(f"Average confidence: {(total_confidence / len(outputs)) * 100:.1f}%")
        print(f"Outputs with corrections: {corrected_count}")
        print(f"Correction rate: {(corrected_count / len(outputs)) * 100:.1f}%")
        
        print("\nBy Object Type:")
        for obj_type, stats in by_object_type.items():
            avg_confidence = (stats["confidence_sum"] / stats["count"]) * 100
            print(f"  {obj_type}:")
            print(f"    Count: {stats['count']} outputs")
            print(f"    Total predicted: {stats['total_predicted']} objects")
            print(f"    Total corrected: {stats['total_corrected']} objects")
            print(f"    Average confidence: {avg_confidence:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Output analysis failed: {e}")
        return False

def main():
    """Main migration function"""
    print("Output Model Migration Utility")
    print("=" * 50)
    
    # Create sample outputs
    if not create_sample_outputs():
        print("ERROR: Failed to create sample outputs")
        return False
    
    # Verify everything is working
    if not verify_outputs():
        print("ERROR: Output verification failed")
        return False
    
    # Analyze the data
    if not analyze_outputs():
        print("ERROR: Output analysis failed")
        return False
    
    print("\n" + "=" * 50)
    print("SUCCESS: Output model migration completed!")
    print("Ready to proceed to database functions migration")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
