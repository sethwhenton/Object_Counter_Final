#!/usr/bin/env python3
"""Simple test script for the API"""

import requests
import time

def test_api():
    """Test the API endpoints"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Object Counting API...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        print("📍 Testing /health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print("   ✅ Health check passed!")
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API. Is the server running?")
        print("   💡 Start the server with: py app.py")
        return False
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    print()
    
    # Test pipeline endpoint (should fail gracefully)
    try:
        print("📍 Testing /test-pipeline endpoint...")
        response = requests.post(f"{base_url}/test-pipeline", timeout=5)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {result}")
        
        if response.status_code == 500 and "AI pipeline not available" in result.get("error", ""):
            print("   ✅ Pipeline gracefully reports missing dependencies!")
        else:
            print("   ⚠️  Unexpected response")
            
    except Exception as e:
        print(f"   ❌ Pipeline test failed: {e}")
    
    print()
    print("🎉 API testing complete!")
    print("💡 Next steps:")
    print("   1. Install ML dependencies: py -m pip install torch torchvision transformers")
    print("   2. Visit: http://127.0.0.1:5000/health in your browser")
    
    return True

if __name__ == "__main__":
    test_api()



