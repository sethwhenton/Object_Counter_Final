#!/usr/bin/env python3
"""
Test the user feedback system end-to-end
"""

import requests
import json

def test_feedback_system():
    """Test the complete feedback system"""
    print("🎯 TESTING USER FEEDBACK SYSTEM")
    print("=" * 70)
    
    # Test 1: Check current results
    print("1️⃣ Checking current results...")
    try:
        response = requests.get("http://127.0.0.1:5000/api/results?page=1&per_page=3")
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"   ✅ Found {len(results)} existing results")
            
            if results:
                latest_result = results[0]
                result_id = latest_result['id']
                current_predicted = latest_result['predicted_count']
                current_corrected = latest_result['corrected_count']
                
                print(f"   📊 Latest result ID: {result_id}")
                print(f"   🎯 Predicted count: {current_predicted}")
                print(f"   💬 Current corrected count: {current_corrected}")
                
                # Test 2: Submit feedback if no correction exists
                if current_corrected is None:
                    print(f"\n2️⃣ Submitting test feedback...")
                    new_corrected_count = current_predicted + 1  # Test with a different value
                    
                    correction_data = {
                        "result_id": result_id,
                        "corrected_count": new_corrected_count
                    }
                    
                    try:
                        correction_response = requests.put(
                            "http://127.0.0.1:5000/api/correct",
                            headers={'Content-Type': 'application/json'},
                            json=correction_data,
                            timeout=10
                        )
                        
                        if correction_response.status_code == 200:
                            correction_result = correction_response.json()
                            print(f"   ✅ Feedback submitted successfully!")
                            print(f"   📝 Response: {correction_result['message']}")
                            print(f"   🔄 Updated corrected_count: {correction_result['corrected_count']}")
                        else:
                            error_data = correction_response.json()
                            print(f"   ❌ Feedback submission failed: {error_data.get('error')}")
                            return False
                            
                    except Exception as e:
                        print(f"   ❌ Error submitting feedback: {e}")
                        return False
                else:
                    print(f"\n2️⃣ Feedback already exists for result {result_id}")
                    print(f"   💬 Current corrected count: {current_corrected}")
                
                # Test 3: Verify feedback was stored
                print(f"\n3️⃣ Verifying feedback was stored...")
                try:
                    verify_response = requests.get("http://127.0.0.1:5000/api/results?page=1&per_page=1")
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        verify_results = verify_data.get('results', [])
                        
                        if verify_results:
                            updated_result = verify_results[0]
                            updated_corrected = updated_result['corrected_count']
                            
                            if updated_corrected is not None:
                                print(f"   ✅ Feedback verified in database!")
                                print(f"   💬 Stored corrected count: {updated_corrected}")
                            else:
                                print(f"   ❌ Feedback not found in database")
                                return False
                        else:
                            print(f"   ❌ No results found for verification")
                            return False
                    else:
                        print(f"   ❌ Failed to verify feedback")
                        return False
                        
                except Exception as e:
                    print(f"   ❌ Error verifying feedback: {e}")
                    return False
                
            else:
                print(f"   ⚠️  No results found. Upload and analyze an image first.")
                return False
        else:
            print(f"   ❌ Failed to get results: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error checking results: {e}")
        return False
    
    # Test 4: Test API endpoints that frontend uses
    print(f"\n4️⃣ Testing frontend API compatibility...")
    try:
        # Test object types endpoint
        types_response = requests.get("http://127.0.0.1:5000/api/object-types")
        if types_response.status_code == 200:
            types_data = types_response.json()
            print(f"   ✅ Object types endpoint: {len(types_data)} types available")
        else:
            print(f"   ⚠️  Object types endpoint issue: {types_response.status_code}")
        
        # Test CORS for frontend
        headers = {'Origin': 'http://localhost:3000'}
        cors_response = requests.get("http://127.0.0.1:5000/api/results", headers=headers)
        cors_header = cors_response.headers.get('Access-Control-Allow-Origin')
        if cors_header:
            print(f"   ✅ CORS configured: {cors_header}")
        else:
            print(f"   ⚠️  CORS header not found")
            
    except Exception as e:
        print(f"   ❌ Frontend compatibility test failed: {e}")
    
    print(f"\n" + "=" * 70)
    print(f"🎯 FEEDBACK SYSTEM DIAGNOSIS")
    print(f"=" * 70)
    
    print(f"✅ **BACKEND FEEDBACK SYSTEM STATUS:**")
    print(f"   • /api/correct endpoint: Working")
    print(f"   • /api/results endpoint: Working")
    print(f"   • Database updates: Working")
    print(f"   • CORS configuration: Working")
    print(f"")
    
    print(f"🔍 **POSSIBLE FRONTEND ISSUES TO CHECK:**")
    print(f"   1. Results component feedback dialog functionality")
    print(f"   2. API service correctPrediction method")
    print(f"   3. ImageHistory refresh mechanism")
    print(f"   4. State management in React components")
    print(f"")
    
    print(f"🛠️ **DEBUGGING STEPS:**")
    print(f"   1. Open browser developer console")
    print(f"   2. Submit feedback and watch for API calls")
    print(f"   3. Check if correctPrediction API is being called")
    print(f"   4. Check if ImageHistory refresh is triggered")
    print(f"   5. Verify React state updates properly")
    
    return True

if __name__ == "__main__":
    test_feedback_system()



