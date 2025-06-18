"""
Test script for the real OpenAI API integration
"""
import requests
import json
import time

def test_real_api():
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Renewable Energy Agent API with Real OpenAI")
    print("=" * 60)
    
    # Wait a moment for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Test health check
    try:
        print("\n1. Testing health check...")
        response = requests.get(f"{base_url}/api/health")
        print(f"✅ Status: {response.status_code}")
        print(f"📋 Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test chat endpoint with a mathematical question
    try:
        print("\n2. Testing chat with math question...")
        chat_data = {
            "message": "Can you help me add 25 kW and 15 kW of solar capacity?",
            "user_id": "test_user_real"
        }
        response = requests.post(f"{base_url}/api/chat", json=chat_data)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📋 Response Summary:")
            print(f"   Success: {result.get('success')}")
            if result.get('data'):
                data = result['data']
                print(f"   Result: {data.get('result')}")
                print(f"   Operation: {data.get('operation')}")
                print(f"   Explanation: {data.get('explanation')[:100]}...")
                print(f"   Renewable Context: {data.get('renewable_context')[:100]}...")
                print(f"   Confidence: {data.get('confidence')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
    
    # Test another question
    try:
        print("\n3. Testing general renewable energy question...")
        chat_data = {
            "message": "What's the difference between 100 MW and 75 MW wind farm capacity?",
            "user_id": "test_user_real"
        }
        response = requests.post(f"{base_url}/api/chat", json=chat_data)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('data'):
                data = result['data']
                print(f"   Result: {data.get('result')}")
                print(f"   Operation: {data.get('operation')}")
                print(f"   Explanation: {data.get('explanation')[:150]}...")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Second chat test failed: {e}")

if __name__ == "__main__":
    test_real_api() 