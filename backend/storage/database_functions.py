#!/usr/bin/python3
"""Database Functions - MySQL Version
Migrated functions that work with our new MySQL models using UUID primary keys
"""
from typing import Optional, List, Dict, Any, Union
import os
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from . import database
from typing import Optional, List, Dict, Any, Union
from .object_types import ObjectType
from typing import Optional, List, Dict, Any, Union
from .inputs import Input
from typing import Optional, List, Dict, Any, Union
from .outputs import Output


def init_database() -> None:
    """Initialize MySQL database with default object types"""
    try:
        # Ensure database is connected
        database.reload()
        
        # Check if object types already exist
        existing_types = database.get_all(ObjectType)
        if not existing_types:
            print("SUCCESS: Initializing object types...")
            
            object_types = [
                {'name': 'car', 'description': 'Automobiles and vehicles'},
                {'name': 'cat', 'description': 'Domestic cats'},
                {'name': 'tree', 'description': 'Trees and large plants'},
                {'name': 'dog', 'description': 'Dogs and canines'},
                {'name': 'building', 'description': 'Buildings and structures'},
                {'name': 'person', 'description': 'People and humans'},
                {'name': 'sky', 'description': 'Sky and atmospheric elements'},
                {'name': 'ground', 'description': 'Ground and terrain'},
                {'name': 'hardware', 'description': 'Tools and hardware items'},
                {'name': 'motorcycle', 'description': 'Motorcycles and bikes'},
                {'name': 'bicycle', 'description': 'Bicycles and cycles'},
                {'name': 'bus', 'description': 'Buses and public transport'},
                {'name': 'truck', 'description': 'Trucks and large vehicles'},
                {'name': 'boat', 'description': 'Boats and watercraft'},
                {'name': 'airplane', 'description': 'Aircraft and planes'}
            ]
            
            for obj_type in object_types:
                new_type = ObjectType()
                new_type.name = obj_type['name']
                new_type.description = obj_type['description']
                database.new(new_type)
            
            database.save()
            print(f"SUCCESS: Created {len(object_types)} object types")
        else:
            print(f"SUCCESS: Database already initialized with {len(existing_types)} object types")
            
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to initialize database: {e}")
        database.rollback()
        raise e


def get_object_type_by_name(name) -> None:
    """Get object type by name using MySQL engine"""
    try:
        return database.get_by_name(ObjectType, name)
    except Exception as e:
        print(f"ERROR: Failed to get object type '{name}': {e}")
        return None


def save_prediction_result(image_path, object_type_name, predicted_count, description=None, pred_confidence=0.85) -> None:
    """Save a prediction result to MySQL database using UUID models"""
    try:
        # Get object type
        object_type = get_object_type_by_name(object_type_name)
        if not object_type:
            raise ValueError(f"Object type '{object_type_name}' not found")
        
        # Create input record
        input_record = Input()
        input_record.image_path = image_path
        input_record.description = description or ""
        
        # Create output record
        output_record = Output()
        output_record.predicted_count = predicted_count
        output_record.pred_confidence = pred_confidence
        output_record.object_type_id = object_type.id
        output_record.input_id = input_record.id  # This will be set after input is saved
        
        # Save input first to get UUID
        database.new(input_record)
        database.save()
        
        # Now set the input_id for output
        output_record.input_id = input_record.id
        
        # Save output
        database.new(output_record)
        database.save()
        
        print(f"SUCCESS: Saved prediction result - {object_type_name}: {predicted_count} objects")
        return output_record
        
    except Exception as e:
        print(f"ERROR: Failed to save prediction result: {e}")
        database.rollback()
        raise e


def update_correction(output_id, corrected_count) -> None:
    """Update a prediction with user correction using MySQL engine"""
    try:
        # Get output record by UUID
        output = database.get(Output, output_id)
        if not output:
            raise ValueError(f"Output with ID {output_id} not found")
        
        # Update corrected count
        output.corrected_count = corrected_count
        output.updated_at = datetime.now()
        
        # Save changes
        database.save()
        
        print(f"SUCCESS: Updated correction for output {output_id}: {corrected_count}")
        return output
        
    except Exception as e:
        print(f"ERROR: Failed to update correction: {e}")
        database.rollback()
        raise e


def get_all_object_types() -> None:
    """Get all object types from MySQL database"""
    try:
        return database.get_all(ObjectType)
    except Exception as e:
        print(f"ERROR: Failed to get object types: {e}")
        return []


def get_all_outputs() -> None:
    """Get all outputs from MySQL database"""
    try:
        return database.get_all(Output)
    except Exception as e:
        print(f"ERROR: Failed to get outputs: {e}")
        return []


def get_all_inputs() -> None:
    """Get all inputs from MySQL database"""
    try:
        return database.get_all(Input)
    except Exception as e:
        print(f"ERROR: Failed to get inputs: {e}")
        return []


def get_all_results(page=1, per_page=10, object_type_filter=None):
    """Get all results with pagination and filtering from MySQL database"""
    try:
        # Get all outputs first
        all_outputs = database.get_all(Output)
        
        # Filter by object type if specified
        if object_type_filter and object_type_filter != 'all':
            filtered_outputs = []
            for output in all_outputs:
                if output.object_type and output.object_type.name == object_type_filter:
                    filtered_outputs.append(output)
            all_outputs = filtered_outputs
        
        # Sort by creation date (newest first)
        all_outputs.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        total_count = len(all_outputs)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_outputs = all_outputs[start_idx:end_idx]
        
        # Format results
        formatted_results = []
        for output in paginated_outputs:
            # Get related data
            input_record = database.get(Input, output.input_id) if output.input_id else None
            object_type = database.get(ObjectType, output.object_type_id) if output.object_type_id else None
            
            formatted_results.append({
                'id': output.id,
                'predicted_count': output.predicted_count,
                'corrected_count': output.corrected_count,
                'object_type': object_type.name if object_type else 'Unknown',
                'image_path': input_record.image_path if input_record else '',
                'description': input_record.description if input_record else '',
                'created_at': output.created_at.isoformat(),
                'updated_at': output.updated_at.isoformat(),
                'pred_confidence': output.pred_confidence
            })
        
        return {
            'results': formatted_results,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        }
        
    except Exception as e:
        print(f"ERROR: Failed to get results: {e}")
        return {
            'results': [],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': 0,
                'pages': 0
            }
        }


def get_results_by_object_type(object_type_name, page=1, per_page=10):
    """Get results filtered by object type with pagination"""
    return get_all_results(page, per_page, object_type_name)


def get_output_by_id(output_id) -> None:
    """Get output by UUID"""
    try:
        return database.get(Output, output_id)
    except Exception as e:
        print(f"ERROR: Failed to get output {output_id}: {e}")
        return None


def get_input_by_id(input_id) -> None:
    """Get input by UUID"""
    try:
        return database.get(Input, input_id)
    except Exception as e:
        print(f"ERROR: Failed to get input {input_id}: {e}")
        return None


def delete_output(output_id) -> None:
    """Delete output and associated input by UUID"""
    try:
        # Get output record
        output = database.get(Output, output_id)
        if not output:
            raise ValueError(f"Output with ID {output_id} not found")
        
        # Get associated input
        input_record = database.get(Input, output.input_id)
        
        # Delete output first (due to foreign key constraints)
        database.delete(output)
        
        # Delete input if it exists
        if input_record:
            database.delete(input_record)
        
        print(f"SUCCESS: Deleted output {output_id} and associated input")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to delete output {output_id}: {e}")
        database.rollback()
        raise e


def get_outputs_with_relationships() -> None:
    """Get all outputs with their related object types and inputs"""
    try:
        # This is a more complex query that joins the tables
        # For now, we'll get all outputs and their relationships separately
        outputs = database.get_all(Output)
        results = []
        
        for output in outputs:
            object_type = database.get(ObjectType, output.object_type_id)
            input_record = database.get(Input, output.input_id)
            
            results.append({
                'output': output,
                'object_type': object_type,
                'input': input_record
            })
        
        return results
        
    except Exception as e:
        print(f"ERROR: Failed to get outputs with relationships: {e}")
        return []


def count_outputs() -> None:
    """Count total number of outputs"""
    try:
        return database.count(Output)
    except Exception as e:
        print(f"ERROR: Failed to count outputs: {e}")
        return 0


def count_object_types() -> None:
    """Count total number of object types"""
    try:
        return database.count(ObjectType)
    except Exception as e:
        print(f"ERROR: Failed to count object types: {e}")
        return 0


def count_inputs() -> None:
    """Count total number of inputs"""
    try:
        return database.count(Input)
    except Exception as e:
        print(f"ERROR: Failed to count inputs: {e}")
        return 0
