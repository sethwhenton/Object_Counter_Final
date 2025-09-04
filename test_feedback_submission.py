#!/usr/bin/env python3
"""
Test feedback/correction submission flow
"""

import requests
import json

def test_feedback_submission():
    """Test the feedback submission process"""
    print("📝 TESTING FEEDBACK SUBMISSION")
    print("=" * 50)
    
    # Step 1: Get existing results
    print("1️⃣ Getting existing results...")
    try:
        response = requests.get("http://127.0.0.1:5000/api/results", timeout=5)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            if results:
                test_result = results[0]  # Use first result for testing
                result_id = test_result['id']
                original_count = test_result['predicted_count']
                current_feedback = test_result['corrected_count']
                
                print(f"   ✅ Found result to test:")
                print(f"      ID: {result_id}")
                print(f"      Original Count: {original_count}")
                print(f"      Current Feedback: {current_feedback}")
                print()
                
                # Step 2: Submit a correction
                print("2️⃣ Submitting feedback correction...")
                correction_data = {
                    "result_id": result_id,
                    "corrected_count": original_count + 1  # Add 1 to original for testing
                }
                
                try:
                    correction_response = requests.put(
                        "http://127.0.0.1:5000/api/correct",
                        headers={'Content-Type': 'application/json'},
                        json=correction_data,
                        timeout=5
                    )
                    
                    if correction_response.status_code == 200:
                        correction_result = correction_response.json()
                        print(f"   ✅ Correction submitted successfully:")
                        print(f"      Result ID: {correction_result.get('result_id')}")
                        print(f"      Predicted: {correction_result.get('predicted_count')}")
                        print(f"      Corrected: {correction_result.get('corrected_count')}")
                        print(f"      Message: {correction_result.get('message')}")
                        print()
                        
                        # Step 3: Verify the correction was saved
                        print("3️⃣ Verifying correction was saved...")
                        verify_response = requests.get("http://127.0.0.1:5000/api/results", timeout=5)
                        if verify_response.status_code == 200:
                            verify_data = verify_response.json()
                            verify_results = verify_data.get('results', [])
                            
                            # Find our result
                            updated_result = None
                            for result in verify_results:
                                if result['id'] == result_id:
                                    updated_result = result
                                    break
                            
                            if updated_result:
                                saved_feedback = updated_result['corrected_count']
                                print(f"   ✅ Verification successful:")
                                print(f"      Result ID: {updated_result['id']}")
                                print(f"      Predicted: {updated_result['predicted_count']}")
                                print(f"      Saved Feedback: {saved_feedback}")
                                
                                if saved_feedback == correction_data['corrected_count']:
                                    print(f"   🎉 FEEDBACK STORAGE WORKING!")
                                else:
                                    print(f"   ❌ Feedback not saved correctly")
                                    print(f"      Expected: {correction_data['corrected_count']}")
                                    print(f"      Got: {saved_feedback}")
                            else:
                                print(f"   ❌ Result not found in verification")
                        else:
                            print(f"   ❌ Verification request failed: {verify_response.status_code}")
                    else:
                        print(f"   ❌ Correction failed: {correction_response.status_code}")
                        print(f"      Error: {correction_response.text}")
                        
                except Exception as e:
                    print(f"   ❌ Correction request error: {e}")
            else:
                print(f"   ❌ No results found to test")
        else:
            print(f"   ❌ Failed to get results: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Results request error: {e}")

if __name__ == "__main__":
    test_feedback_submission()




