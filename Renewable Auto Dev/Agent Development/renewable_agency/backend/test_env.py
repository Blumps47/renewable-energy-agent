#!/usr/bin/env python3
"""
Test environment variable loading from backend directory
"""

import os
from dotenv import load_dotenv

# Load environment variables from the correct path
load_dotenv('../../.env')

# Check OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"✅ API Key found: length={len(api_key)}, starts with: {api_key[:10]}...")
    if api_key.startswith("sk-"):
        print("✅ API Key format looks correct (starts with 'sk-')")
    else:
        print("❌ API Key format incorrect (should start with 'sk-')")
else:
    print("❌ No API Key found in environment")

# Test basic imports
try:
    import fastapi
    print("✅ FastAPI imported successfully")
except ImportError as e:
    print(f"❌ FastAPI import failed: {e}")

try:
    import pydantic_ai
    print("✅ PydanticAI imported successfully")
except ImportError as e:
    print(f"❌ PydanticAI import failed: {e}")

try:
    import openai
    print("✅ OpenAI imported successfully")
except ImportError as e:
    print(f"❌ OpenAI import failed: {e}")

print("\n🧪 Environment Test Complete") 