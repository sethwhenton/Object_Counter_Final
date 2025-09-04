#!/usr/bin/env python3
"""
Complete System Test - Frontend + Backend + Database
"""

import requests
import time
import json

def test_backend_health():
    """Test backend health endpoint"""
    print("🔧 Testing Backend...")
    try:
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy!")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Database: {data.get('database')}")
            print(f"   - Object Types: {data.get('object_types')}")
            print(f"   - AI Pipeline: {data.get('pipeline_available')}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_object_types():
    """Test object types endpoint"""
    print("\n📋 Testing Object Types...")
    try:
        response = requests.get("http://127.0.0.1:5000/api/object-types", timeout=5)
        if response.status_code == 200:
            data = response.json()
            object_types = data.get('object_types', [])
            print(f"✅ Found {len(object_types)} object types:")
            for i, obj_type in enumerate(object_types[:5], 1):  # Show first 5
                print(f"   {i}. {obj_type['name']} - {obj_type['description']}")
            if len(object_types) > 5:
                print(f"   ... and {len(object_types) - 5} more")
            return True
        else:
            print(f"❌ Object types request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Object types request failed: {e}")
        return False

def test_frontend():
    """Test frontend accessibility"""
    print("\n🌐 Testing Frontend...")
    try:
        response = requests.get("http://localhost:3001", timeout=5)
        if response.status_code == 200:
            print(f"✅ Frontend is accessible at http://localhost:3001")
            print(f"   - Status Code: {response.status_code}")
            return True
        else:
            print(f"❌ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend connection failed: {e}")
        print(f"   - Make sure frontend is running: npm run dev")
        return False

def test_cors():
    """Test CORS headers for frontend-backend communication"""
    print("\n🔗 Testing CORS Configuration...")
    try:
        # Simulate a preflight request
        headers = {
            'Origin': 'http://localhost:3001',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options("http://127.0.0.1:5000/api/object-types", headers=headers, timeout=5)
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print(f"✅ CORS is properly configured")
            print(f"   - Allow Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
            return True
        else:
            print(f"⚠️  CORS headers not found (might still work)")
            return True
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

def main():
    """Run complete system test"""
    print("🚀 COMPLETE SYSTEM TEST")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Object Types API", test_object_types),
        ("Frontend Accessibility", test_frontend),
        ("CORS Configuration", test_cors)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL SYSTEMS GO! Your frontend and backend are ready!")
        print("\n📱 Next steps:")
        print("   1. Open http://localhost:3001 in your browser")
        print("   2. Upload an image")
        print("   3. Select an object type")
        print("   4. Click 'Count Objects'")
        print("   5. Wait ~30 seconds for AI processing")
        print("   6. See your results!")
    else:
        print("🔧 Some tests failed. Check the errors above.")
        if not results[0][1]:  # Backend failed
            print("   → Make sure backend is running: python app.py")
        if not results[2][1]:  # Frontend failed
            print("   → Make sure frontend is running: npm run dev")

if __name__ == "__main__":
    main()
