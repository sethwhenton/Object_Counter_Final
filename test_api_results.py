#!/usr/bin/env python3
"""
Test the API results to verify images and object types are working
"""

import requests

def test_api_results():
    """Test the /api/results endpoint"""
    print("🧪 TESTING API RESULTS")
    print("=" * 40)
    
    try:
        response = requests.get("http://127.0.0.1:5000/api/results", timeout=5)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"✅ API Response: {response.status_code}")
            print(f"📊 Found: {len(results)} results")
            print()
            
            for i, result in enumerate(results[:4], 1):
                print(f"Result {i}:")
                print(f"   🆔 ID: {result.get('id')}")
                print(f"   🎯 Object Type: '{result.get('object_type')}'")
                print(f"   🔢 Predicted Count: {result.get('predicted_count')}")
                print(f"   🖼️  Image Path: '{result.get('image_path')}'")
                print(f"   💬 Feedback: {result.get('corrected_count')}")
                print(f"   📅 Created: {result.get('created_at')}")
                print()
                
                # Test image URL
                if result.get('image_path'):
                    image_url = f"http://127.0.0.1:5000/uploads/{result.get('image_path')}"
                    try:
                        img_response = requests.head(image_url, timeout=3)
                        if img_response.status_code == 200:
                            print(f"   ✅ Image accessible: {image_url}")
                        else:
                            print(f"   ❌ Image failed ({img_response.status_code}): {image_url}")
                    except Exception as e:
                        print(f"   ❌ Image error: {e}")
                    print()
        else:
            print(f"❌ API failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api_results()




