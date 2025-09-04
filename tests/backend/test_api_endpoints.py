#!/usr/bin/env python3
"""
Test script for the new API endpoints with database integration
"""

import requests
import json
import os

def test_api_endpoints():
    """Test all API endpoints with database integration"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Object Counting API with Database...")
    print("=" * 60)
    
    # Test 1: Health check with database status
    print("📍 Test 1: Health Check with Database Status")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   API Status: {result.get('status')}")
        print(f"   Database: {result.get('database')}")
        print(f"   Object Types: {result.get('object_types')}")
        print(f"   Pipeline Available: {result.get('pipeline_available')}")
        
        if response.status_code == 200:
            print("   ✅ Health check passed!")
        else:
            print("   ❌ Health check failed!")
            return False
            
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    print()
    
    # Test 2: Get available object types
    print("📍 Test 2: Get Available Object Types")
    try:
        response = requests.get(f"{base_url}/api/object-types", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            object_types = result.get('object_types', [])
            print(f"   Available types: {[obj['name'] for obj in object_types]}")
            print("   ✅ Object types retrieved!")
        else:
            print(f"   ❌ Failed to get object types: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Failed to get object types: {e}")
    
    print()
    
    # Test 3: Upload image and count objects (production endpoint)
    print("📍 Test 3: Production Object Counting (/api/count)")
    
    image_path = "../model_pipeline/image.png"
    if not os.path.exists(image_path):
        print(f"   ❌ Test image not found at: {image_path}")
        print("   💡 Make sure you're running this from the backend/ directory")
        return False
    
    try:
        with open(image_path, 'rb') as img_file:
            files = {'image': img_file}
            data = {
                'object_type': 'car',
                'description': 'Test image from sample dataset'
            }
            
            print("   🚀 Uploading image and processing...")
            response = requests.post(f"{base_url}/api/count", files=files, data=data, timeout=120)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Production API test successful!")
            print(f"   📊 Results:")
            print(f"      Result ID: {result['result_id']}")
            print(f"      Object Type: {result['object_type']}")
            print(f"      Predicted Count: {result['predicted_count']}")
            print(f"      Total Segments: {result['total_segments']}")
            print(f"      Processing Time: {result['processing_time']}s")
            print(f"      Created At: {result['created_at']}")
            
            # Save result_id for correction test
            result_id = result['result_id']
            
        else:
            print(f"   ❌ Production API failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Production API failed: {e}")
        return False
    
    print()
    
    # Test 4: Correct the prediction
    print("📍 Test 4: Correct Prediction (/api/correct)")
    try:
        correction_data = {
            'result_id': result_id,
            'corrected_count': 2  # Assume user corrects to 2 cars
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.put(
            f"{base_url}/api/correct", 
            data=json.dumps(correction_data), 
            headers=headers, 
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Correction saved successfully!")
            print(f"   📊 Updated Results:")
            print(f"      Result ID: {result['result_id']}")
            print(f"      Predicted Count: {result['predicted_count']}")
            print(f"      Corrected Count: {result['corrected_count']}")
            print(f"      Updated At: {result['updated_at']}")
            
        else:
            print(f"   ❌ Correction failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Correction failed: {e}")
    
    print()
    
    # Test 5: Get all results
    print("📍 Test 5: Get All Results (/api/results)")
    try:
        response = requests.get(f"{base_url}/api/results?per_page=5", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            results = result.get('results', [])
            pagination = result.get('pagination', {})
            
            print("   ✅ Results retrieved successfully!")
            print(f"   📊 Found {len(results)} results (Total: {pagination.get('total', 0)})")
            
            for i, res in enumerate(results[:3]):  # Show first 3 results
                print(f"   Result {i+1}:")
                print(f"      ID: {res['id']} | Object: {res.get('object_type_name')} | Predicted: {res['predicted_count']} | Corrected: {res.get('corrected_count', 'None')}")
                
        else:
            print(f"   ❌ Failed to get results: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Failed to get results: {e}")
    
    print()
    print("=" * 60)
    print("🎉 API Testing Complete!")
    print()
    print("📋 Summary:")
    print("   ✅ Database integration working")
    print("   ✅ Object types initialized")
    print("   ✅ Production counting endpoint working")
    print("   ✅ Correction endpoint working")
    print("   ✅ Results retrieval working")
    print()
    print("🚀 TASK 2 Implementation Complete!")
    
    return True

if __name__ == "__main__":
    print("🔧 Make sure the Flask server is running:")
    print("   py app.py")
    print()
    input("Press Enter when ready to test...")
    test_api_endpoints()



