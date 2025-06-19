#!/usr/bin/env python3
"""
Test script for existing Supabase schema and API keys
"""
import os
import sys
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

async def test_openai():
    """Test OpenAI API connection"""
    try:
        from openai import OpenAI
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return False, "API key not found in environment"
        
        client = OpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, test connection"}],
            max_tokens=10
        )
        
        return True, f"Connected successfully. Model: {response.model}"
        
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

async def test_supabase():
    """Test Supabase connection with existing schema"""
    try:
        from supabase import create_client, Client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not url or not key:
            return False, "Supabase credentials not found"
        
        supabase: Client = create_client(url, key)
        
        # Test connection by querying existing tables
        # First, let's try to get table information
        try:
            result = supabase.table('users').select('id').limit(1).execute()
            return True, f"Connected successfully. Users table accessible."
        except Exception as e:
            # If users table fails, try organizations
            try:
                result = supabase.table('organizations').select('id').limit(1).execute()
                return True, f"Connected successfully. Organizations table accessible."
            except Exception as e2:
                return False, f"Tables not accessible: {str(e2)}"
        
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

async def test_dropbox():
    """Test Dropbox API connection"""
    try:
        import dropbox
        
        access_token = os.getenv('DROPBOX_ACCESS_TOKEN')
        if not access_token:
            return False, "Access token not found"
        
        dbx = dropbox.Dropbox(access_token)
        account_info = dbx.users_get_current_account()
        
        return True, f"Connected as {account_info.name.display_name}"
        
    except ImportError:
        return False, "Dropbox package not installed (pip install dropbox)"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

async def main():
    """Run all tests"""
    print("=" * 60)
    print(" 🔑 API Keys Validation (Existing Schema)")
    print("=" * 60)
    
    tests = [
        ("OpenAI", test_openai(), True),
        ("Supabase", test_supabase(), True),
        ("Dropbox", test_dropbox(), False),
    ]
    
    results = []
    
    print("\nRunning tests...")
    print("-" * 30)
    
    for name, test_coro, required in tests:
        try:
            success, message = await test_coro
            
            if success:
                status = "✅"
                print(f"{status} {name}: {message}")
                results.append("passed")
            else:
                status = "❌" if required else "⚠️"
                print(f"{status} {name}: {message}")
                results.append("failed" if required else "skipped")
                
        except Exception as e:
            status = "❌" if required else "⚠️"
            print(f"{status} {name}: Unexpected error: {str(e)}")
            results.append("failed" if required else "skipped")
    
    # Summary
    print("\n" + "=" * 60)
    print(" 📊 Validation Summary")
    print("=" * 60)
    
    passed = results.count("passed")
    failed = results.count("failed")
    skipped = results.count("skipped")
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️ Skipped: {skipped}")
    
    if failed > 0:
        print(f"\n❌ System has issues!")
        print("Some required APIs are failing. Please check your configuration.")
        return False
    else:
        print(f"\n✅ All required systems are working!")
        print("You can now start the server with: python backend/main.py")
        return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 