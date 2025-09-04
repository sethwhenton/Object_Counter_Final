#!/usr/bin/env python3
"""
Simple test script to verify the AI pipeline works
"""

import requests
import os
import sys

def test_pipeline():
    """Test the pipeline with the sample image"""
    
    # API endpoint
    url = "http://localhost:5000/test-pipeline"
    
    # Path to test image
    image_path = "../model_pipeline/image.png"
    
    if not os.path.exists(image_path):
        print(f"❌ Test image not found at: {image_path}")
        print("Make sure you're running this from the backend/ directory")
        return False
    
    print("🔍 Testing Object Counting Pipeline...")
    print(f"📸 Using image: {image_path}")
    
    try:
        # Prepare the request
        with open(image_path, 'rb') as img_file:
            files = {'image': img_file}
            data = {'object_type': 'car'}  # Test counting cars
            
            print("🚀 Sending request to API...")
            response = requests.post(url, files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Pipeline test successful!")
            print(f"📊 Results:")
            print(f"   Object Type: {result['object_type']}")
            print(f"   Predicted Count: {result['predicted_count']}")
            print(f"   Total Segments: {result['total_segments']}")
            print(f"   Processing Time: {result['processing_time']}s")
            return True
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure Flask app is running:")
        print("   cd backend && python app.py")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API")
        return False

if __name__ == "__main__":
    print("🧪 Starting API Tests...")
    print("=" * 50)
    
    # Test health endpoint first
    if test_health():
        # Test the main pipeline
        test_pipeline()
    
    print("=" * 50)
    print("✨ Test complete!")



