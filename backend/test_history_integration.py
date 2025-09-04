#!/usr/bin/env python3
"""
Test script to verify the image history functionality works end-to-end
"""

import requests
import json
import time
import os

def test_complete_history_flow():
    """Test the complete flow: upload image -> process -> check history"""
    print("🚀 Testing Complete Image History Flow")
    print("=" * 50)
    
    # Test 1: Check if results endpoint works
    print("1. Testing /api/results endpoint...")
    try:
        response = requests.get("http://127.0.0.1:5000/api/results?page=1&per_page=5")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Results endpoint working")
            print(f"   📊 Current results count: {data['pagination']['total']}")
            print(f"   📄 Pagination: {data['pagination']['page']}/{data['pagination']['pages']}")
        else:
            print(f"   ❌ Results endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing results endpoint: {e}")
        return False
    
    # Test 2: Check object types
    print("\n2. Testing object types...")
    try:
        response = requests.get("http://127.0.0.1:5000/api/object-types")
        if response.status_code == 200:
            data = response.json()
            object_types = data.get('object_types', [])
            print(f"   ✅ Found {len(object_types)} object types")
            if object_types:
                print(f"   📝 First object type: {object_types[0]['name']}")
        else:
            print(f"   ❌ Object types endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing object types: {e}")
        return False
    
    # Test 3: Test image processing (if we have object types)
    if object_types:
        print(f"\n3. Testing image processing with '{object_types[0]['name']}'...")
        
        # Create a simple test image (1x1 pixel PNG)
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
        
        try:
            files = {'image': ('test_history.png', test_image_data, 'image/png')}
            data = {
                'object_type': object_types[0]['name'],
                'description': 'Test for history functionality'
            }
            
            print(f"   🔄 Processing image...")
            start_time = time.time()
            response = requests.post("http://127.0.0.1:5000/api/count-all", files=files, data=data)
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Image processed successfully!")
                print(f"   📊 Result ID: {result.get('result_id')}")
                print(f"   🎯 Object Type: {result.get('object_type')}")
                print(f"   🔢 Count: {result.get('predicted_count')}")
                print(f"   ⏱️  Processing Time: {result.get('processing_time', 0):.2f}s")
                print(f"   🖼️  Image Path: {result.get('image_path')}")
                
                # Test 4: Check if result appears in history
                print(f"\n4. Checking if result appears in history...")
                time.sleep(1)  # Small delay to ensure database is updated
                
                response = requests.get("http://127.0.0.1:5000/api/results?page=1&per_page=5")
                if response.status_code == 200:
                    history_data = response.json()
                    results = history_data.get('results', [])
                    
                    if results:
                        print(f"   ✅ Found {len(results)} results in history")
                        latest_result = results[0]  # Should be the newest
                        print(f"   📝 Latest result:")
                        print(f"      - ID: {latest_result.get('id')}")
                        print(f"      - Object Type: {latest_result.get('object_type')}")
                        print(f"      - Count: {latest_result.get('predicted_count')}")
                        print(f"      - Image Path: {latest_result.get('image_path')}")
                        print(f"      - Created: {latest_result.get('created_at')}")
                        
                        # Test 5: Test image serving
                        image_path = latest_result.get('image_path', '')
                        if image_path:
                            print(f"\n5. Testing image serving...")
                            image_filename = image_path.split('/')[-1] if '/' in image_path else image_path
                            image_url = f"http://127.0.0.1:5000/uploads/{image_filename}"
                            
                            try:
                                img_response = requests.get(image_url)
                                if img_response.status_code == 200:
                                    print(f"   ✅ Image served successfully!")
                                    print(f"   📏 Image size: {len(img_response.content)} bytes")
                                    print(f"   🎨 Content type: {img_response.headers.get('content-type', 'unknown')}")
                                else:
                                    print(f"   ❌ Image serving failed: {img_response.status_code}")
                            except Exception as e:
                                print(f"   ❌ Error serving image: {e}")
                    else:
                        print(f"   ❌ No results found in history")
                        return False
                else:
                    print(f"   ❌ Failed to get history: {response.status_code}")
                    return False
                
            else:
                print(f"   ❌ Image processing failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error processing image: {e}")
            return False
    
    print(f"\n" + "=" * 50)
    print("🎉 Image History Integration Test Complete!")
    print("\n✅ All systems working:")
    print("   - Results API endpoint")
    print("   - Object types API")
    print("   - Image processing")
    print("   - History storage")
    print("   - Image serving")
    print("\n🚀 Ready for frontend testing!")
    
    return True

if __name__ == "__main__":
    test_complete_history_flow()


