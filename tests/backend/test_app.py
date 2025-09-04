"""
Minimal Flask app to test if Python/Flask works
This bypasses the AI pipeline to isolate the Python environment issue
"""

print("Starting minimal Flask test...")

try:
    from flask import Flask, jsonify
    print("✅ Flask import successful")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")
    exit(1)

try:
    from flask_cors import CORS
    print("✅ Flask-CORS import successful")
except ImportError as e:
    print(f"❌ Flask-CORS import failed: {e}")
    # Continue without CORS for testing

# Create minimal Flask app
app = Flask(__name__)

try:
    CORS(app)
    print("✅ CORS enabled")
except:
    print("⚠️ CORS not available, continuing without it")

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check without database dependencies"""
    return jsonify({
        "status": "healthy",
        "message": "Minimal Flask server is running",
        "python_working": True
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint"""
    return jsonify({
        "message": "Python Flask server is working!",
        "success": True
    })

if __name__ == '__main__':
    print("🚀 Starting minimal Flask server...")
    print("📍 Health check: http://127.0.0.1:5000/health")
    print("📍 Test endpoint: http://127.0.0.1:5000/test")
    
    app.run(host='127.0.0.1', port=5000, debug=True)





