#!/usr/bin/env python3
"""
API Keys Validation Script
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_keys():
    print("🔑 API Keys Validation")
    print("=" * 60)
    
    # Test OpenAI
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and not openai_key.startswith('your-'):
        print("✅ OpenAI API Key: Configured")
    else:
        print("❌ OpenAI API Key: Not configured")
    
    # Test Supabase
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    if supabase_url and supabase_key and not supabase_url.startswith('your-'):
        print("✅ Supabase: Configured")
    else:
        print("❌ Supabase: Not configured")
    
    # Test optional APIs
    dropbox_token = os.getenv('DROPBOX_ACCESS_TOKEN')
    if dropbox_token and not dropbox_token.startswith('your-'):
        print("✅ Dropbox: Configured")
    else:
        print("⚠️ Dropbox: Optional - Not configured")
    
    print("\n📝 Run 'python setup_api_keys.py' to configure missing keys")

if __name__ == "__main__":
    test_api_keys() 