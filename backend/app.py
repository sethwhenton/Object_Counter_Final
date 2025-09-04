from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from config import config, allowed_file
from models.database import db, init_database, save_prediction_result, update_correction, get_object_type_by_name, ObjectType, Output, Input
from performance_monitor import get_performance_monitor
from performance_metrics import calculate_f1_metrics, calculate_legacy_accuracy, get_performance_badge_info

# Create Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:3001"])  # Enable CORS for frontend integration

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Initialize database
init_database(app)

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
        object_types_count = ObjectType.query.count()
        return jsonify({
            "status": "healthy", 
            "message": "Object Counting API is running",
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
    Upload image and get object count prediction stored in database
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
            available_types = [ot.name for ot in ObjectType.query.all()]
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
        
        # Save result to database (store relative path)
        output_record = save_prediction_result(
            image_path=unique_filename,  # Store just the filename, not full path
            object_type_name=object_type_name,
            predicted_count=result["count"],
            description=description
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
                    description=description
                )
                result_id = output_record.id
            else:
                # Fallback to first available object type
                fallback_type = ObjectType.query.first()
                output_record = save_prediction_result(
                    image_path=unique_filename,
                    object_type_name=fallback_type.name,
                    predicted_count=result["total_objects"],
                    description=description
                )
                result_id = output_record.id
        else:
            # No objects detected - store with first available type
            fallback_type = ObjectType.query.first()
            output_record = save_prediction_result(
                image_path=unique_filename,
                object_type_name=fallback_type.name,
                predicted_count=0,
                description=description
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
        
        # Update the prediction
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

@app.route('/api/results', methods=['GET'])
def get_results():
    """Get all prediction results with pagination and complete data"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        object_type_filter = request.args.get('object_type')
        
        # Base query joining Output, Input, and ObjectType tables
        query = db.session.query(Output, Input, ObjectType).join(
            Input, Output.input_fk == Input.id
        ).join(
            ObjectType, Output.object_type_fk == ObjectType.id
        )
        
        # Apply object type filter if specified
        if object_type_filter and object_type_filter != 'all':
            query = query.filter(ObjectType.name == object_type_filter)
        
        # Order by creation date (newest first)
        query = query.order_by(Output.created_at.desc())
        
        # Apply pagination
        paginated = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Format results for frontend
        results = []
        for output, input_record, object_type in paginated.items:
            results.append({
                "id": output.id,
                "object_type": object_type.name,
                "predicted_count": output.predicted_count,
                "corrected_count": output.corrected_count,
                "image_path": input_record.image_path,
                "description": input_record.description or "",
                "created_at": output.created_at.isoformat(),
                "input_id": input_record.id
            })
        
        return jsonify({
            "success": True,
            "results": results,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": paginated.total,
                "pages": paginated.pages,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/object-types', methods=['GET'])
def get_object_types():
    """Get all available object types"""
    try:
        object_types = ObjectType.query.all()
        return jsonify({
            "object_types": [obj_type.to_dict() for obj_type in object_types]
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

# History management endpoints
@app.route('/api/results/<int:result_id>', methods=['DELETE'])
def delete_result(result_id):
    """Delete a specific result and its associated data"""
    try:
        # Find the output record
        output = Output.query.get(result_id)
        if not output:
            return jsonify({"error": "Result not found"}), 404
        
        # Find the associated input record
        input_record = Input.query.get(output.input_fk)
        
        # Delete the image file if it exists
        if input_record and input_record.image_path:
            try:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], input_record.image_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🗑️  Deleted image file: {input_record.image_path}")
            except Exception as e:
                print(f"⚠️  Warning: Could not delete image file: {e}")
        
        # Delete the records from database
        db.session.delete(output)
        if input_record:
            db.session.delete(input_record)
        
        db.session.commit()
        
        print(f"✅ Deleted result {result_id} and associated data")
        
        return jsonify({
            "success": True,
            "message": "Result deleted successfully",
            "deleted_result_id": result_id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting result {result_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/results/<int:result_id>/feedback', methods=['PUT'])
def update_result_feedback(result_id):
    """Update feedback for a specific result"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        corrected_count = data.get('corrected_count')
        object_type_name = data.get('object_type')
        
        if corrected_count is None:
            return jsonify({"error": "corrected_count is required"}), 400
        
        # Find the output record
        output = Output.query.get(result_id)
        if not output:
            return jsonify({"error": "Result not found"}), 404
        
        # Update the corrected count
        old_corrected_count = output.corrected_count
        output.corrected_count = corrected_count
        output.updated_at = datetime.utcnow()
        
        # Update object type if provided
        if object_type_name:
            object_type = ObjectType.query.filter_by(name=object_type_name).first()
            if object_type:
                output.object_type_id = object_type.id
        
        db.session.commit()
        
        print(f"✅ Updated feedback for result {result_id}: {old_corrected_count} -> {corrected_count}")
        
        return jsonify({
            "success": True,
            "message": "Feedback updated successfully",
            "result_id": result_id,
            "predicted_count": output.predicted_count,
            "corrected_count": output.corrected_count,
            "updated_at": output.updated_at.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating feedback for result {result_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/results/<int:result_id>', methods=['GET'])
def get_result_details(result_id):
    """Get detailed information for a specific result"""
    try:
        # Query the specific result with all related data
        result = db.session.query(Output, Input, ObjectType)\
            .join(Input, Output.input_fk == Input.id)\
            .join(ObjectType, Output.object_type_fk == ObjectType.id)\
            .filter(Output.id == result_id)\
            .first()
        
        if not result:
            return jsonify({"error": "Result not found"}), 404
        
        output, input_record, object_type = result
        
        # Calculate F1 Score if feedback exists (better than accuracy for object counting)
        f1_metrics = None
        f1_score = None
        precision = None
        recall = None
        accuracy = None  # Keep for backward compatibility
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
                "object_type": object_type.name,
                "object_type_id": object_type.id,
                "image_path": input_record.image_path,
                "description": input_record.description or "",
                "created_at": output.created_at.isoformat(),
                "updated_at": output.updated_at.isoformat(),
                "processing_time": getattr(output, 'processing_time', None),
                "total_segments": getattr(output, 'total_segments', None),
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

@app.route('/api/results/bulk-delete', methods=['DELETE'])
def bulk_delete_results():
    """Delete multiple results and their associated data"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        result_ids = data.get('result_ids', [])
        if not result_ids:
            return jsonify({"error": "No result IDs provided"}), 400
        
        if not isinstance(result_ids, list):
            return jsonify({"error": "result_ids must be a list"}), 400
        
        # Validate all IDs are integers
        try:
            result_ids = [int(id) for id in result_ids]
        except (ValueError, TypeError):
            return jsonify({"error": "All result IDs must be integers"}), 400
        
        deleted_results = []
        deleted_files = []
        failed_deletions = []
        
        for result_id in result_ids:
            try:
                # Find the output record
                output = Output.query.get(result_id)
                if not output:
                    failed_deletions.append({"id": result_id, "reason": "Result not found"})
                    continue
                
                # Find the associated input record
                input_record = Input.query.get(output.input_id)
                
                # Delete the image file if it exists
                if input_record and input_record.image_path:
                    try:
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], input_record.image_path)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            deleted_files.append(input_record.image_path)
                            print(f"🗑️  Deleted image file: {input_record.image_path}")
                    except Exception as e:
                        print(f"⚠️  Warning: Could not delete image file for result {result_id}: {e}")
                
                # Delete the records from database
                db.session.delete(output)
                if input_record:
                    db.session.delete(input_record)
                
                deleted_results.append(result_id)
                
            except Exception as e:
                failed_deletions.append({"id": result_id, "reason": str(e)})
                print(f"❌ Error deleting result {result_id}: {e}")
        
        # Commit all successful deletions
        if deleted_results:
            db.session.commit()
            print(f"✅ Bulk deleted {len(deleted_results)} results: {deleted_results}")
        
        # Prepare response
        response_data = {
            "success": True,
            "deleted_count": len(deleted_results),
            "deleted_result_ids": deleted_results,
            "deleted_files": deleted_files,
            "failed_count": len(failed_deletions),
            "failures": failed_deletions,
            "message": f"Successfully deleted {len(deleted_results)} results"
        }
        
        if failed_deletions:
            response_data["message"] += f", {len(failed_deletions)} failures"
        
        return jsonify(response_data)
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in bulk deletion: {e}")
        return jsonify({"error": str(e)}), 500

# Performance monitoring endpoints
@app.route('/api/performance/start', methods=['POST'])
def start_performance_monitoring():
    """Start performance monitoring for a processing session"""
    try:
        data = request.get_json() or {}
        total_images = data.get('total_images', 1)
        
        monitor = get_performance_monitor()
        monitor.start_monitoring(total_images)
        
        return jsonify({
            "success": True,
            "message": "Performance monitoring started",
            "total_images": total_images
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/performance/stop', methods=['POST'])
def stop_performance_monitoring():
    """Stop performance monitoring"""
    try:
        monitor = get_performance_monitor()
        summary = monitor.get_metrics_summary()
        monitor.stop_monitoring()
        
        return jsonify({
            "success": True,
            "message": "Performance monitoring stopped",
            "summary": summary
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/performance/metrics', methods=['GET'])
def get_performance_metrics():
    """Get current real-time performance metrics"""
    try:
        monitor = get_performance_monitor()
        metrics = monitor.get_current_metrics()
        
        return jsonify(metrics)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/performance/update-stage', methods=['POST'])
def update_performance_stage():
    """Update the current processing stage"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON data required"}), 400
            
        stage = data.get('stage', 'unknown')
        image_index = data.get('image_index')
        
        monitor = get_performance_monitor()
        monitor.update_stage(stage, image_index)
        
        return jsonify({
            "success": True,
            "stage": stage,
            "image_index": image_index
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/performance/summary', methods=['GET'])
def get_performance_summary():
    """Get performance summary and statistics"""
    try:
        monitor = get_performance_monitor()
        summary = monitor.get_metrics_summary()
        
        return jsonify(summary)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    print("Starting Object Counting API...")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /test-pipeline - Test the AI pipeline")
    print("  POST /api/performance/start - Start performance monitoring")
    print("  POST /api/performance/stop - Stop performance monitoring")
    print("  GET  /api/performance/metrics - Get real-time metrics")
    print("  POST /api/performance/update-stage - Update processing stage")
    print("  GET  /api/performance/summary - Get performance summary")
    app.run(debug=True, host='0.0.0.0', port=5000)
