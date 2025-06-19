#!/usr/bin/env python3
"""
API Keys Validation Script for Renewable Energy RAG System
=========================================================

This script tests all configured API keys to ensure they're working properly.
Run: python test_api_keys.py
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Tuple

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class APIKeyValidator:
    def __init__(self):
        self.results = {}

    def print_header(self, title: str):
        """Print a formatted header"""
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)

    def print_test(self, service: str, status: str, message: str):
        """Print test result"""
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {service}: {message}")

    async def test_openai_key(self) -> Tuple[str, str]:
        """Test OpenAI API key"""
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key or api_key.startswith('your-'):
            return "SKIP", "API key not configured"
        
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            
            # Test with a simple completion
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return "PASS", "API key is valid and working"
        except ImportError:
            return "SKIP", "OpenAI package not installed (pip install openai)"
        except Exception as e:
            return "FAIL", f"API key test failed: {str(e)}"

    async def test_supabase_connection(self) -> Tuple[str, str]:
        """Test Supabase connection"""
        url = os.getenv('SUPABASE_URL')
        service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not url or not service_key or url.startswith('your-'):
            return "SKIP", "Supabase credentials not configured"
        
        try:
            from supabase import create_client
            supabase = create_client(url, service_key)
            
            # Test connection with a simple query
            result = supabase.table('information_schema.tables').select('table_name').limit(1).execute()
            return "PASS", "Connection successful"
        except ImportError:
            return "SKIP", "Supabase package not installed (pip install supabase)"
        except Exception as e:
            return "FAIL", f"Connection failed: {str(e)}"

    async def test_dropbox_access(self) -> Tuple[str, str]:
        """Test Dropbox access token"""
        access_token = os.getenv('DROPBOX_ACCESS_TOKEN')
        
        if not access_token or access_token.startswith('your-'):
            return "SKIP", "Access token not configured"
        
        try:
            import dropbox
            dbx = dropbox.Dropbox(access_token)
            
            # Test with account info
            account = dbx.users_get_current_account()
            return "PASS", f"Connected as {account.name.display_name}"
        except ImportError:
            return "SKIP", "Dropbox package not installed (pip install dropbox)"
        except Exception as e:
            return "FAIL", f"Access token test failed: {str(e)}"

    async def test_google_drive_credentials(self) -> Tuple[str, str]:
        """Test Google Drive credentials"""
        credentials = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
        
        if not credentials or credentials.startswith('your-'):
            return "SKIP", "Credentials not configured"
        
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            # Parse credentials (assuming JSON string)
            import json
            creds_info = json.loads(credentials)
            credentials = service_account.Credentials.from_service_account_info(creds_info)
            
            # Build the service
            service = build('drive', 'v3', credentials=credentials)
            
            # Test with a simple query
            results = service.files().list(pageSize=1).execute()
            return "PASS", "Credentials valid and working"
        except ImportError:
            return "SKIP", "Google API packages not installed"
        except Exception as e:
            return "FAIL", f"Credentials test failed: {str(e)}"

    async def run_validation(self):
        """Run all API key validations"""
        self.print_header("🔑 API Keys Validation")
        print("Testing all configured API keys...\n")

        # Test required APIs
        print("Required APIs:")
        print("-" * 20)
        
        # OpenAI
        status, message = await self.test_openai_key()
        self.print_test("OpenAI", status, message)
        self.results['openai'] = (status, message)
        
        # Supabase
        status, message = await self.test_supabase_connection()
        self.print_test("Supabase", status, message)
        self.results['supabase'] = (status, message)
        
        # Test optional APIs
        print("\nOptional APIs:")
        print("-" * 20)
        
        # Dropbox
        status, message = await self.test_dropbox_access()
        self.print_test("Dropbox", status, message)
        self.results['dropbox'] = (status, message)
        
        # Google Drive
        status, message = await self.test_google_drive_credentials()
        self.print_test("Google Drive", status, message)
        self.results['google_drive'] = (status, message)
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print validation summary"""
        self.print_header("📊 Validation Summary")
        
        passed = sum(1 for status, _ in self.results.values() if status == "PASS")
        failed = sum(1 for status, _ in self.results.values() if status == "FAIL")
        skipped = sum(1 for status, _ in self.results.values() if status == "SKIP")
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Skipped: {skipped}")
        
        # Check required APIs
        openai_status = self.results.get('openai', ('SKIP', ''))[0]
        supabase_status = self.results.get('supabase', ('SKIP', ''))[0]
        
        if openai_status == "PASS" and supabase_status == "PASS":
            print("\n🚀 System is ready to run!")
            print("All required APIs are configured and working.")
        elif openai_status == "FAIL" or supabase_status == "FAIL":
            print("\n❌ System has issues!")
            print("Some required APIs are failing. Please check your configuration.")
        else:
            print("\n⚠️ System needs setup!")
            print("Required APIs are not configured. Run: python setup_api_keys.py")
        
        print(f"\n📝 Next steps:")
        if openai_status != "PASS" or supabase_status != "PASS":
            print("1. Run: python setup_api_keys.py")
            print("2. Configure missing API keys")
            print("3. Re-run this validation script")
        else:
            print("1. Set up database: Run SQL in backend/database_schema.sql")
            print("2. Test the system: python backend/test_rag_system.py")
            print("3. Start the server: uvicorn backend.main:app --reload")

async def main():
    """Main entry point"""
    validator = APIKeyValidator()
    await validator.run_validation()

if __name__ == "__main__":
    asyncio.run(main()) 