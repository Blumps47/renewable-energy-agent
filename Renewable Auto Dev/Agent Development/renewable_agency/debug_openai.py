#!/usr/bin/env python3
"""
Debug OpenAI API key issue
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Debugging OpenAI API Key")
print("=" * 40)

# Check if key exists
api_key = os.getenv('OPENAI_API_KEY')
print(f"Key exists: {api_key is not None}")
print(f"Key length: {len(api_key) if api_key else 0}")
print(f"Key starts with: {api_key[:20] if api_key else 'None'}...")
print(f"Key ends with: {api_key[-10:] if api_key else 'None'}")

# Test OpenAI connection
try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    print("\n🧪 Testing OpenAI connection...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'hello'"}],
        max_tokens=5
    )
    print("✅ OpenAI connection successful!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ OpenAI connection failed: {str(e)}")
    
    # Check for common issues
    if "401" in str(e) or "invalid_api_key" in str(e):
        print("\n💡 Possible solutions:")
        print("1. Check if your API key is correct")
        print("2. Make sure you have credits in your OpenAI account")
        print("3. Verify the key hasn't expired")
        print("4. Try regenerating the key from OpenAI dashboard") 