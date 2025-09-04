#!/usr/bin/python3
"""Flask Application - MySQL Version
Updated to use the new MySQL database functions and models
"""
import os

# Set MySQL environment variables before importing anything else
os.environ['OBJ_DETECT_MYSQL_USER'] = 'obj_detect_dev'
os.environ['OBJ_DETECT_MYSQL_PWD'] = 'obj_detect_dev_pwd'
os.environ['OBJ_DETECT_MYSQL_HOST'] = 'localhost'
os.environ['OBJ_DETECT_MYSQL_DB'] = 'obj_detect_dev_db'
os.environ['OBJ_DETECT_ENV'] = 'development'

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from config import config, allowed_file

# Import new MySQL database functions
from storage.database_functions import (
    init_database, get_object_type_by_name, save_prediction_result,
    update_correction, get_all_object_types, get_output_by_id,
    delete_output, count_outputs, get_all_outputs
)

# Import MySQL models
from storage.object_types import ObjectType
from storage.inputs import Input
from storage.outputs import Output

from performance_monitor import get_performance_monitor
from performance_metrics import calculate_f1_metrics, calculate_legacy_accuracy, get_performance_badge_info

# Create Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:3001"])  # Enable CORS for frontend integration

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Initialize MySQL database
init_database()

# Initialize the AI pipeline with error handling
pipeline = None
pipeline_error = None

try:
    from models.pipeline import ObjectCountingPipeline
    pipeline = ObjectCountingPipeline()
    print("✅ AI Pipeline initialized successfully!")
except Exception as e:
    pipeline_error = str(e)
    print(f"❌ Failed to initialize AI pipeline: {e}")
    print("💡 Make sure all dependencies are installed. See INSTALL_STEPS.md")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        object_types_count = count_object_types()
        return jsonify({
            "status": "healthy", 
            "message": "Object Counting API is running (MySQL)",
            "database": "connected",
            "object_types": object_types_count,
            "pipeline_available": pipeline is not None
        })
    except Exception as e:
        return jsonify({
            "status": "degraded",
            "message": "API running but database issue",
            "error": str(e),
            "pipeline_available": pipeline is not None
        }), 503


@app.route('/test-pipeline', methods=['POST'])
def test_pipeline():
    """Test endpoint to verify the AI pipeline works"""
    
    # Check if pipeline is available
    if pipeline is None:
        return jsonify({
            "error": "AI pipeline not available", 
            "details": pipeline_error,
            "solution": "Install dependencies using: py -m pip install torch torchvision transformers"
        }), 500
    
    try:
        # Check if image file is provided
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "No image file selected"}), 400
        
        # Get object type to count (default to 'car' for testing)
        object_type = request.form.get('object_type', 'car')
        
        # Process the image
        result = pipeline.count_objects(image_file, object_type)
        
        return jsonify({
            "success": True,
            "object_type": object_type,
            "predicted_count": result["count"],
            "total_segments": result["total_segments"],
            "processing_time": result["processing_time"]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/count', methods=['POST'])
def count_objects():
    """
    Production API endpoint for object counting
    Upload image and get object count prediction stored in MySQL database
    """
    
    # Check if pipeline is available
    if pipeline is None:
        return jsonify({
            "error": "AI pipeline not available", 
            "details": pipeline_error,
            "solution": "Install dependencies and restart server"
        }), 500
    
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        if 'object_type' not in request.form:
            return jsonify({"error": "No object_type specified"}), 400
        
        image_file = request.files['image']
        object_type_name = request.form['object_type']
        description = request.form.get('description', '')
        
        if image_file.filename == '':
            return jsonify({"error": "No image file selected"}), 400
        
        if not allowed_file(image_file.filename):
            return jsonify({
                "error": "Invalid file type", 
                "allowed_types": list(app.config['ALLOWED_EXTENSIONS'])
            }), 400
        
        # Verify object type exists
        object_type = get_object_type_by_name(object_type_name)
        if not object_type:
            available_types = [ot.name for ot in get_all_object_types()]
            return jsonify({
                "error": f"Invalid object type: {object_type_name}",
                "available_types": available_types
            }), 400
        
        # Save uploaded image
        filename = secure_filename(image_file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        image_file.save(image_path)
        
        # Process image with AI pipeline
        image_file.seek(0)  # Reset file pointer for pipeline processing
        result = pipeline.count_objects(image_file, object_type_name)
        
        # Save result to MySQL database (store relative path)
        output_record = save_prediction_result(
            image_path=unique_filename,  # Store just the filename, not full path
            object_type_name=object_type_name,
            predicted_count=result["count"],
            description=description,
            pred_confidence=0.85  # Default confidence, can be enhanced later
        )
        
        return jsonify({
            "success": True,
            "result_id": output_record.id,
            "object_type": object_type_name,
            "predicted_count": result["count"],
            "total_segments": result["total_segments"],
            "processing_time": result["processing_time"],
            "image_path": f"uploads/{unique_filename}",  # Return path for frontend use
            "created_at": output_record.created_at.isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/count-all', methods=['POST'])
def count_all_objects():
    """
    Multi-object detection API endpoint
    Upload image and get counts for ALL detected objects
    """
    
    # Check if pipeline is available
    if pipeline is None:
        return jsonify({
            "error": "AI pipeline not available", 
            "details": pipeline_error,
            "solution": "Install dependencies and restart server"
        }), 500
    
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        image_file = request.files['image']
        description = request.form.get('description', '')
        
        if image_file.filename == '':
            return jsonify({"error": "No image file selected"}), 400
        
        if not allowed_file(image_file.filename):
            return jsonify({
                "error": "Invalid file type", 
                "allowed_types": list(app.config['ALLOWED_EXTENSIONS'])
            }), 400
        
        # Save uploaded image
        filename = secure_filename(image_file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        image_file.save(image_path)
        
        # Process image with AI pipeline for multi-object detection
        image_file.seek(0)  # Reset file pointer for pipeline processing
        result = pipeline.count_all_objects(image_file)
        
        # Store results for all detected object types in database
        # We'll use the most common object type as the primary for now
        # (This can be enhanced later for better multi-object storage)
        if result["objects"]:
            # Find the most detected object type
            primary_object = max(result["objects"], key=lambda x: x["count"])
            primary_object_type = get_object_type_by_name(primary_object["type"])
            
            if primary_object_type:
                # Save primary result to database
                output_record = save_prediction_result(
                    image_path=unique_filename,
                    object_type_name=primary_object["type"],
                    predicted_count=result["total_objects"],  # Store total count
                    description=description,
                    pred_confidence=0.85
                )
                result_id = output_record.id
            else:
                # Fallback to first available object type
                fallback_type = get_all_object_types()[0]
                output_record = save_prediction_result(
                    image_path=unique_filename,
                    object_type_name=fallback_type.name,
                    predicted_count=result["total_objects"],
                    description=description,
                    pred_confidence=0.85
                )
                result_id = output_record.id
        else:
            # No objects detected - store with first available type
            fallback_type = get_all_object_types()[0]
            output_record = save_prediction_result(
                image_path=unique_filename,
                object_type_name=fallback_type.name,
                predicted_count=0,
                description=description,
                pred_confidence=0.85
            )
            result_id = output_record.id
        
        return jsonify({
            "success": True,
            "result_id": result_id,
            "objects": result["objects"],
            "total_objects": result["total_objects"],
            "total_segments": result["total_segments"],
            "processing_time": result["processing_time"],
            "image_path": f"uploads/{unique_filename}",
            "created_at": output_record.created_at.isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/correct', methods=['PUT'])
def correct_prediction():
    """
    API endpoint for correcting object count predictions
    Update prediction with user-provided correction
    """
    
    try:
        # Validate request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON data required"}), 400
        
        if 'result_id' not in data:
            return jsonify({"error": "result_id is required"}), 400
        
        if 'corrected_count' not in data:
            return jsonify({"error": "corrected_count is required"}), 400
        
        result_id = data['result_id']
        corrected_count = data['corrected_count']
        
        # Validate corrected_count is a non-negative integer
        if not isinstance(corrected_count, int) or corrected_count < 0:
            return jsonify({"error": "corrected_count must be a non-negative integer"}), 400
        
        # Update the prediction using MySQL function
        updated_output = update_correction(result_id, corrected_count)
        
        return jsonify({
            "success": True,
            "result_id": updated_output.id,
            "predicted_count": updated_output.predicted_count,
            "corrected_count": updated_output.corrected_count,
            "updated_at": updated_output.updated_at.isoformat(),
            "message": "Correction saved successfully"
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/object-types', methods=['GET'])
def get_object_types():
    """Get all available object types"""
    try:
        object_types = get_all_object_types()
        return jsonify({
            "object_types": [
                {
                    'id': obj_type.id,
                    'name': obj_type.name,
                    'description': obj_type.description,
                    'created_at': obj_type.created_at.isoformat(),
                    'updated_at': obj_type.updated_at.isoformat()
                } for obj_type in object_types
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    """
    Serve uploaded images for frontend display
    """
    try:
        upload_folder = app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, filename)
        
        # Security check: ensure file exists and is in uploads directory
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
        
        # Ensure the file is within the uploads directory (prevent directory traversal)
        if not os.path.abspath(file_path).startswith(os.path.abspath(upload_folder)):
            return jsonify({"error": "Access denied"}), 403
        
        return send_file(file_path)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/results/<result_id>', methods=['DELETE'])
def delete_result(result_id):
    """Delete a specific result and its associated data"""
    try:
        # Use MySQL function to delete
        delete_success = delete_output(result_id)
        
        if delete_success:
            return jsonify({
                "success": True,
                "message": "Result deleted successfully",
                "deleted_result_id": result_id
            })
        else:
            return jsonify({"error": "Failed to delete result"}), 500
        
    except Exception as e:
        print(f"❌ Error deleting result {result_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/results/<result_id>', methods=['GET'])
def get_result_details(result_id):
    """Get detailed information for a specific result"""
    try:
        # Get output record
        output = get_output_by_id(result_id)
        if not output:
            return jsonify({"error": "Result not found"}), 404
        
        # Get related data
        object_type = get_object_type_by_name(output.object_type.name) if output.object_type else None
        
        # Calculate F1 Score if feedback exists
        f1_metrics = None
        f1_score = None
        precision = None
        recall = None
        accuracy = None
        performance_explanation = None
        
        if output.corrected_count is not None:
            # Use utility function for consistent F1 Score calculation
            f1_metrics = calculate_f1_metrics(output.predicted_count, output.corrected_count)
            f1_score = f1_metrics['f1_score']
            precision = f1_metrics['precision']
            recall = f1_metrics['recall']
            performance_explanation = f1_metrics['explanation']
            
            # Keep legacy accuracy calculation for compatibility
            accuracy = calculate_legacy_accuracy(output.predicted_count, output.corrected_count)
        
        return jsonify({
            "success": True,
            "result": {
                "id": output.id,
                "predicted_count": output.predicted_count,
                "corrected_count": output.corrected_count,
                "pred_confidence": output.pred_confidence,
                "object_type": object_type.name if object_type else None,
                "object_type_id": object_type.id if object_type else None,
                "image_path": output.input.image_path if output.input else None,
                "description": output.input.description if output.input else "",
                "created_at": output.created_at.isoformat(),
                "updated_at": output.updated_at.isoformat(),
                # F1 Score metrics (primary)
                "f1_score": f1_score,
                "precision": precision,
                "recall": recall,
                "performance_explanation": performance_explanation,
                "performance_metrics": f1_metrics,
                # Legacy metrics (for compatibility)
                "accuracy": accuracy,
                "difference": abs(output.predicted_count - output.corrected_count) if output.corrected_count is not None else None,
                "has_feedback": output.corrected_count is not None
            }
        })
        
    except Exception as e:
        print(f"❌ Error getting result details for {result_id}: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    print("Starting Object Counting API (MySQL Version)...")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /test-pipeline - Test the AI pipeline")
    print("  POST /api/count - Count objects in image")
    print("  POST /api/count-all - Count all objects in image")
    print("  PUT  /api/correct - Correct prediction")
    print("  GET  /api/object-types - Get available object types")
    print("  GET  /api/results/<id> - Get result details")
    print("  DELETE /api/results/<id> - Delete result")
    app.run(debug=True, host='0.0.0.0', port=5000)
