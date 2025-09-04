#!/usr/bin/python3
"""Flask Application - Restructured with MySQL, Flask-RESTful, and Swagger
Updated to use the new MySQL database functions and models with modern API structure
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
from flask_restful import Api, Resource, reqparse
from flasgger import Swagger, swag_from
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from config import config, allowed_file

# Import new MySQL database functions
from storage.database_functions import (
    init_database, get_object_type_by_name, save_prediction_result,
    update_correction, get_all_object_types, get_output_by_id,
    delete_output, count_outputs, get_all_outputs, get_outputs_with_relationships,
    get_all_results
)

# Import MySQL models
from storage.object_types import ObjectType
from storage.inputs import Input
from storage.outputs import Output

from performance_monitor import get_performance_monitor
from performance_metrics import calculate_f1_metrics, calculate_legacy_accuracy, get_performance_badge_info

# Create Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"])  # Enable CORS for frontend integration

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Initialize Flask-RESTful API
api = Api(app)

# Initialize Swagger documentation
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Object Counting API",
        "description": "AI-powered object counting API with MySQL backend",
        "version": "2.0.0",
        "contact": {
            "name": "AI Engineering Lab",
            "email": "support@example.com"
        }
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http", "https"],
    "consumes": ["application/json", "multipart/form-data"],
    "produces": ["application/json"]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

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


# ============================================================================
# API RESOURCES (Flask-RESTful)
# ============================================================================

class HealthResource(Resource):
    """Health check endpoint"""
    
    @swag_from({
        'responses': {
            200: {
                'description': 'Health status',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string'},
                        'message': {'type': 'string'},
                        'database': {'type': 'string'},
                        'object_types': {'type': 'integer'},
                        'pipeline_available': {'type': 'boolean'}
                    }
                }
            }
        }
    })
    def get(self):
        """Get API health status"""
        try:
            # Check database connection
            object_types_count = len(get_all_object_types())
            return {
                "status": "healthy", 
                "message": "Object Counting API is running (MySQL)",
                "database": "connected",
                "object_types": object_types_count,
                "pipeline_available": pipeline is not None
            }, 200
        except Exception as e:
            return {
                "status": "degraded",
                "message": "API running but database issue",
                "error": str(e),
                "pipeline_available": pipeline is not None
            }, 503


class InitDatabaseResource(Resource):
    """Initialize database with default object types"""
    
    @swag_from({
        'responses': {
            200: {
                'description': 'Database initialized successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'message': {'type': 'string'},
                        'object_types_created': {'type': 'integer'}
                    }
                }
            },
            500: {'description': 'Server error'}
        }
    })
    def post(self):
        """Initialize database with default object types"""
        try:
            # Initialize database
            init_database()
            
            # Get count of object types
            object_types_count = len(get_all_object_types())
            
            return {
                "success": True,
                "message": "Database initialized successfully",
                "object_types_created": object_types_count
            }, 200
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }, 500


class TestPipelineResource(Resource):
    """Test endpoint to verify the AI pipeline works"""
    
    @swag_from({
        'parameters': [
            {
                'name': 'image',
                'in': 'formData',
                'type': 'file',
                'required': True,
                'description': 'Image file to test'
            },
            {
                'name': 'object_type',
                'in': 'formData',
                'type': 'string',
                'required': False,
                'default': 'car',
                'description': 'Object type to count'
            }
        ],
        'responses': {
            200: {
                'description': 'Pipeline test successful',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'object_type': {'type': 'string'},
                        'predicted_count': {'type': 'integer'},
                        'total_segments': {'type': 'integer'},
                        'processing_time': {'type': 'number'}
                    }
                }
            },
            400: {'description': 'Bad request'},
            500: {'description': 'Pipeline not available'}
        }
    })
    def post(self):
        """Test the AI pipeline with an image"""
        
        # Check if pipeline is available
        if pipeline is None:
            return {
                "error": "AI pipeline not available", 
                "details": pipeline_error,
                "solution": "Install dependencies using: py -m pip install torch torchvision transformers"
            }, 500
        
        try:
            # Check if image file is provided
            if 'image' not in request.files:
                return {"error": "No image file provided"}, 400
            
            image_file = request.files['image']
            if image_file.filename == '':
                return {"error": "No image file selected"}, 400
            
            # Get object type to count (default to 'car' for testing)
            object_type = request.form.get('object_type', 'car')
            
            # Process the image
            result = pipeline.count_objects(image_file, object_type)
            
            return {
                "success": True,
                "object_type": object_type,
                "predicted_count": result["count"],
                "total_segments": result["total_segments"],
                "processing_time": result["processing_time"]
            }, 200
            
        except Exception as e:
            return {"error": str(e)}, 500


class CountObjectsResource(Resource):
    """Production API endpoint for object counting"""
    
    @swag_from({
        'parameters': [
            {
                'name': 'image',
                'in': 'formData',
                'type': 'file',
                'required': True,
                'description': 'Image file to analyze'
            },
            {
                'name': 'object_type',
                'in': 'formData',
                'type': 'string',
                'required': True,
                'description': 'Type of object to count'
            },
            {
                'name': 'description',
                'in': 'formData',
                'type': 'string',
                'required': False,
                'description': 'Optional description'
            }
        ],
        'responses': {
            200: {
                'description': 'Object counting successful',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'result_id': {'type': 'string'},
                        'object_type': {'type': 'string'},
                        'predicted_count': {'type': 'integer'},
                        'total_segments': {'type': 'integer'},
                        'processing_time': {'type': 'number'},
                        'image_path': {'type': 'string'},
                        'created_at': {'type': 'string'}
                    }
                }
            },
            400: {'description': 'Bad request'},
            500: {'description': 'Server error'}
        }
    })
    def post(self):
        """Upload image and get object count prediction stored in MySQL database"""
        
        # Check if pipeline is available
        if pipeline is None:
            return {
                "error": "AI pipeline not available", 
                "details": pipeline_error,
                "solution": "Install dependencies and restart server"
            }, 500
        
        try:
            # Validate request
            if 'image' not in request.files:
                return {"error": "No image file provided"}, 400
            
            if 'object_type' not in request.form:
                return {"error": "No object_type specified"}, 400
            
            image_file = request.files['image']
            object_type_name = request.form['object_type']
            description = request.form.get('description', '')
            
            if image_file.filename == '':
                return {"error": "No image file selected"}, 400
            
            if not allowed_file(image_file.filename):
                return {
                    "error": "Invalid file type", 
                    "allowed_types": list(app.config['ALLOWED_EXTENSIONS'])
                }, 400
            
            # Verify object type exists
            object_type = get_object_type_by_name(object_type_name)
            if not object_type:
                available_types = [ot.name for ot in get_all_object_types()]
                return {
                    "error": f"Invalid object type: {object_type_name}",
                    "available_types": available_types
                }, 400
            
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
            
            return {
                "success": True,
                "result_id": output_record.id,
                "object_type": object_type_name,
                "predicted_count": result["count"],
                "total_segments": result["total_segments"],
                "processing_time": result["processing_time"],
                "image_path": f"uploads/{unique_filename}",  # Return path for frontend use
                "created_at": output_record.created_at.isoformat()
            }, 200
            
        except Exception as e:
            return {"error": str(e)}, 500


class CountAllObjectsResource(Resource):
    """API endpoint for single object type detection and counting"""
    
    @swag_from({
        'parameters': [
            {
                'name': 'image',
                'in': 'formData',
                'type': 'file',
                'required': True,
                'description': 'Image file to analyze'
            },
            {
                'name': 'object_type',
                'in': 'formData',
                'type': 'string',
                'required': True,
                'description': 'Object type to detect and count'
            },
            {
                'name': 'description',
                'in': 'formData',
                'type': 'string',
                'required': False,
                'description': 'Optional description'
            }
        ],
        'responses': {
            200: {
                'description': 'Single object detection successful',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'result_id': {'type': 'string'},
                        'object_type': {'type': 'string'},
                        'predicted_count': {'type': 'integer'},
                        'total_segments': {'type': 'integer'},
                        'processing_time': {'type': 'number'},
                        'image_path': {'type': 'string'},
                        'created_at': {'type': 'string'}
                    }
                }
            },
            400: {
                'description': 'Bad request - missing parameters or invalid file type',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'},
                        'allowed_types': {'type': 'array', 'items': {'type': 'string'}}
                    }
                }
            },
            500: {
                'description': 'Internal server error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def post(self):
        """Upload image and get multi-object detection and counting"""
        
        # Check if pipeline is available
        if pipeline is None:
            return {
                "error": "AI pipeline not available", 
                "details": pipeline_error,
                "solution": "Install dependencies and restart server"
            }, 500
        
        try:
            # Validate request
            if 'image' not in request.files:
                return {"error": "No image file provided"}, 400
            
            image_file = request.files['image']
            object_type = request.form.get('object_type', '')
            description = request.form.get('description', '')
            
            if image_file.filename == '':
                return {"error": "No image file selected"}, 400
            
            if not object_type:
                return {"error": "No object type specified"}, 400
            
            if not allowed_file(image_file.filename):
                return {
                    "error": "Invalid file type", 
                    "allowed_types": list(app.config['ALLOWED_EXTENSIONS'])
                }, 400
            
            # Save uploaded image
            filename = secure_filename(image_file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Ensure upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_file.save(image_path)
            
            # Process only the specified object type
            print(f"🎯 Processing image for object type: {object_type}")
            
            # Process image for the specified object type only
            try:
                result = pipeline.count_objects(image_file, object_type)
                
                detected_objects = [{
                    "type": object_type,
                    "count": result["count"]
                }]
                total_objects = result["count"]
                total_segments = result["total_segments"]
                processing_time = result["processing_time"]
                
                print(f"✅ Detected {result['count']} {object_type} objects in {result['processing_time']:.2f}s")
                
            except Exception as e:
                print(f"❌ Error detecting {object_type}: {e}")
                return {"error": f"Failed to detect {object_type}: {str(e)}"}, 500
            
            # Save the detection result
            output_record = save_prediction_result(
                image_path=unique_filename,
                object_type_name=object_type,
                predicted_count=total_objects,
                description=description or f"Single object detection: {object_type}",
                pred_confidence=0.85
            )
            
            return {
                "success": True,
                "result_id": output_record.id,
                "object_type": object_type,
                "predicted_count": total_objects,
                "total_segments": total_segments,
                "processing_time": processing_time,
                "image_path": f"uploads/{unique_filename}",
                "created_at": output_record.created_at.isoformat()
            }, 200
            
        except Exception as e:
            return {"error": str(e)}, 500


class CorrectPredictionResource(Resource):
    """API endpoint for correcting object count predictions"""
    
    @swag_from({
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'result_id': {'type': 'string', 'description': 'UUID of the result to correct'},
                        'corrected_count': {'type': 'integer', 'description': 'Corrected count value'}
                    },
                    'required': ['result_id', 'corrected_count']
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Correction saved successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'result_id': {'type': 'string'},
                        'predicted_count': {'type': 'integer'},
                        'corrected_count': {'type': 'integer'},
                        'updated_at': {'type': 'string'},
                        'message': {'type': 'string'}
                    }
                }
            },
            400: {'description': 'Bad request'},
            404: {'description': 'Result not found'},
            500: {'description': 'Server error'}
        }
    })
    def put(self):
        """Update prediction with user-provided correction"""
        
        try:
            # Validate request
            data = request.get_json()
            
            if not data:
                return {"error": "JSON data required"}, 400
            
            if 'result_id' not in data:
                return {"error": "result_id is required"}, 400
            
            if 'corrected_count' not in data:
                return {"error": "corrected_count is required"}, 400
            
            result_id = data['result_id']
            corrected_count = data['corrected_count']
            
            # Validate corrected_count is a non-negative integer
            if not isinstance(corrected_count, int) or corrected_count < 0:
                return {"error": "corrected_count must be a non-negative integer"}, 400
            
            # Update the prediction using MySQL function
            updated_output = update_correction(result_id, corrected_count)
            
            return {
                "success": True,
                "result_id": updated_output.id,
                "predicted_count": updated_output.predicted_count,
                "corrected_count": updated_output.corrected_count,
                "updated_at": updated_output.updated_at.isoformat(),
                "message": "Correction saved successfully"
            }, 200
            
        except ValueError as e:
            return {"error": str(e)}, 404
        except Exception as e:
            return {"error": str(e)}, 500


class ObjectTypesResource(Resource):
    """Get all available object types"""
    
    @swag_from({
        'responses': {
            200: {
                'description': 'List of object types',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'object_types': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'string'},
                                    'name': {'type': 'string'},
                                    'description': {'type': 'string'},
                                    'created_at': {'type': 'string'},
                                    'updated_at': {'type': 'string'}
                                }
                            }
                        }
                    }
                }
            },
            500: {'description': 'Server error'}
        }
    })
    def get(self):
        """Get all available object types"""
        try:
            object_types = get_all_object_types()
            return {
                "object_types": [
                    {
                        'id': obj_type.id,
                        'name': obj_type.name,
                        'description': obj_type.description,
                        'created_at': obj_type.created_at.isoformat(),
                        'updated_at': obj_type.updated_at.isoformat()
                    } for obj_type in object_types
                ]
            }, 200
        except Exception as e:
            return {"error": str(e)}, 500


class ResultsListResource(Resource):
    """Get all prediction results with pagination and filtering"""
    
    @swag_from({
        'parameters': [
            {
                'name': 'page',
                'in': 'query',
                'type': 'integer',
                'required': False,
                'description': 'Page number for pagination (default: 1)'
            },
            {
                'name': 'per_page',
                'in': 'query',
                'type': 'integer',
                'required': False,
                'description': 'Number of results per page (default: 10)'
            },
            {
                'name': 'object_type',
                'in': 'query',
                'type': 'string',
                'required': False,
                'description': 'Filter by object type name'
            }
        ],
        'responses': {
            200: {
                'description': 'Results retrieved successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'results': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'string'},
                                    'predicted_count': {'type': 'integer'},
                                    'corrected_count': {'type': 'integer'},
                                    'object_type': {'type': 'string'},
                                    'image_path': {'type': 'string'},
                                    'description': {'type': 'string'},
                                    'created_at': {'type': 'string'},
                                    'updated_at': {'type': 'string'},
                                    'pred_confidence': {'type': 'number'}
                                }
                            }
                        },
                        'pagination': {
                            'type': 'object',
                            'properties': {
                                'page': {'type': 'integer'},
                                'per_page': {'type': 'integer'},
                                'total': {'type': 'integer'},
                                'pages': {'type': 'integer'}
                            }
                        }
                    }
                }
            },
            500: {
                'description': 'Server error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def get(self):
        """Get all prediction results with pagination and filtering"""
        try:
            # Get query parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            object_type_filter = request.args.get('object_type')
            
            # Validate parameters
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 10
            
            print(f"🔍 API Request - Page: {page}, Per Page: {per_page}, Filter: {object_type_filter}")
            
            # Get results from database
            result_data = get_all_results(page, per_page, object_type_filter)
            
            print(f"📊 Database returned {len(result_data['results'])} results, total: {result_data['pagination']['total']}")
            
            return {
                "success": True,
                "results": result_data['results'],
                "pagination": result_data['pagination']
            }, 200
            
        except Exception as e:
            print(f"❌ Error getting results list: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}, 500


class ResultDetailsResource(Resource):
    """Get detailed information for a specific result"""
    
    @swag_from({
        'parameters': [
            {
                'name': 'result_id',
                'in': 'path',
                'type': 'string',
                'required': True,
                'description': 'UUID of the result'
            }
        ],
        'responses': {
            200: {
                'description': 'Result details',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'result': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'string'},
                                'predicted_count': {'type': 'integer'},
                                'corrected_count': {'type': 'integer'},
                                'pred_confidence': {'type': 'number'},
                                'object_type': {'type': 'string'},
                                'object_type_id': {'type': 'string'},
                                'image_path': {'type': 'string'},
                                'description': {'type': 'string'},
                                'created_at': {'type': 'string'},
                                'updated_at': {'type': 'string'},
                                'f1_score': {'type': 'number'},
                                'precision': {'type': 'number'},
                                'recall': {'type': 'number'},
                                'accuracy': {'type': 'number'},
                                'has_feedback': {'type': 'boolean'}
                            }
                        }
                    }
                }
            },
            404: {'description': 'Result not found'},
            500: {'description': 'Server error'}
        }
    })
    def get(self, result_id):
        """Get detailed information for a specific result"""
        try:
            # Get output record
            output = get_output_by_id(result_id)
            if not output:
                return {"error": "Result not found"}, 404
            
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
            
            return {
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
            }, 200
            
        except Exception as e:
            print(f"❌ Error getting result details for {result_id}: {e}")
            return {"error": str(e)}, 500


class DeleteResultResource(Resource):
    """Delete a specific result and its associated data"""
    
    @swag_from({
        'parameters': [
            {
                'name': 'result_id',
                'in': 'path',
                'type': 'string',
                'required': True,
                'description': 'UUID of the result to delete'
            }
        ],
        'responses': {
            200: {
                'description': 'Result deleted successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'message': {'type': 'string'},
                        'deleted_result_id': {'type': 'string'}
                    }
                }
            },
            500: {'description': 'Server error'}
        }
    })
    def delete(self, result_id):
        """Delete a specific result and its associated data"""
        try:
            # Use MySQL function to delete
            delete_success = delete_output(result_id)
            
            if delete_success:
                return {
                    "success": True,
                    "message": "Result deleted successfully",
                    "deleted_result_id": result_id
                }, 200
            else:
                return {"error": "Failed to delete result"}, 500
            
        except Exception as e:
            print(f"❌ Error deleting result {result_id}: {e}")
            return {"error": str(e)}, 500


# ============================================================================
# API ROUTES
# ============================================================================

# Add API resources
api.add_resource(HealthResource, '/health')
api.add_resource(InitDatabaseResource, '/api/init-db')
api.add_resource(TestPipelineResource, '/test-pipeline')
api.add_resource(CountObjectsResource, '/api/count')
api.add_resource(CountAllObjectsResource, '/api/count-all')
api.add_resource(CorrectPredictionResource, '/api/correct')
api.add_resource(ObjectTypesResource, '/api/object-types')
api.add_resource(ResultsListResource, '/api/results')
api.add_resource(ResultDetailsResource, '/api/results/<string:result_id>')
api.add_resource(DeleteResultResource, '/api/results/<string:result_id>/delete')


# ============================================================================
# LEGACY ROUTES (for backward compatibility)
# ============================================================================

@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    """
    Serve uploaded images for frontend display with proper headers
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
        
        # Get file extension to set proper content type
        file_ext = os.path.splitext(filename)[1].lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        
        content_type = content_types.get(file_ext, 'application/octet-stream')
        
        response = send_file(file_path, mimetype=content_type)
        
        # Add CORS headers for frontend access
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        # Add cache headers for better performance
        response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
        
        return response
        
    except Exception as e:
        print(f"❌ Error serving file {filename}: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    print("Starting Object Counting API (Restructured with MySQL)...")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /test-pipeline - Test the AI pipeline")
    print("  POST /api/count - Count objects in image")
    print("  POST /api/count-all - Count specific object type in image")
    print("  PUT  /api/correct - Correct prediction")
    print("  GET  /api/object-types - Get available object types")
    print("  GET  /api/results - Get all results with pagination")
    print("  GET  /api/results/<id> - Get result details")
    print("  DELETE /api/results/<id>/delete - Delete result")
    print("  GET  /docs - Swagger API documentation")
    print("  GET  /uploads/<filename> - Serve uploaded images")
    app.run(debug=True, host='0.0.0.0', port=5000)
