#!/usr/bin/env python3
"""
Simple Flask server for testing image serving without AI pipeline
"""

from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import os
from models.database import db, init_database, ObjectType, Input, Output

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:3001"])

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///object_counting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database tables and data
init_database(app)

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "Simple server running",
        "database": "connected",
        "object_types": 12
    })

@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    """Serve uploaded images"""
    try:
        upload_folder = 'uploads'
        file_path = os.path.join(upload_folder, filename)
        
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
        
        if not os.path.abspath(file_path).startswith(os.path.abspath(upload_folder)):
            return jsonify({"error": "Access denied"}), 403
        
        return send_file(file_path)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/results')
def get_results():
    """Get real results from database with pagination and filtering"""
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        object_type_filter = request.args.get('object_type')
        
        # Base query joining Input and Output tables
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
        
        # Format results
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
                "pages": paginated.pages
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/object-types')
def get_object_types():
    """Get real object types from database"""
    try:
        object_types = ObjectType.query.all()
        return jsonify({
            "object_types": [obj_type.to_dict() for obj_type in object_types]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Simple test server starting...")
    print("📁 Serving files from uploads/ directory")
    print("🖼️ Image URLs: http://127.0.0.1:5000/uploads/<filename>")
    print("📊 History API: http://127.0.0.1:5000/api/results")
    app.run(debug=True, host='0.0.0.0', port=5000)
