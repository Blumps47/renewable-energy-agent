#!/usr/bin/env python3
"""
Interactive API Keys Setup Script for Renewable Energy RAG System
================================================================

This script helps you set up all the required API keys for the system.
Run: python setup_api_keys.py
"""

import os
import sys
import json
import asyncio
from typing import Dict, Optional, Tuple
from pathlib import Path
import secrets
import string

class APIKeySetup:
    def __init__(self):
        self.env_file = Path(".env")
        self.current_config = {}
        self.load_current_config()

    def load_current_config(self):
        """Load current environment configuration"""
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self.current_config[key.strip()] = value.strip()

    def save_config(self):
        """Save configuration to .env file"""
        with open(self.env_file, 'w') as f:
            f.write("# Renewable Energy RAG System Configuration\n\n")
            
            # Core AI Services
            f.write("# Core AI Services\n")
            f.write(f"OPENAI_API_KEY={self.current_config.get('OPENAI_API_KEY', 'your-openai-api-key-here')}\n\n")
            
            # Database & Storage
            f.write("# Database & Storage\n")
            f.write(f"SUPABASE_URL={self.current_config.get('SUPABASE_URL', 'your-supabase-project-url')}\n")
            f.write(f"SUPABASE_SERVICE_KEY={self.current_config.get('SUPABASE_SERVICE_KEY', 'your-supabase-service-key')}\n")
            f.write(f"SUPABASE_ANON_KEY={self.current_config.get('SUPABASE_ANON_KEY', 'your-supabase-anon-key')}\n\n")
            
            # Document Sources
            f.write("# Document Sources (Optional)\n")
            f.write(f"DROPBOX_ACCESS_TOKEN={self.current_config.get('DROPBOX_ACCESS_TOKEN', 'your-dropbox-access-token')}\n")
            f.write(f"GOOGLE_DRIVE_CREDENTIALS={self.current_config.get('GOOGLE_DRIVE_CREDENTIALS', 'your-google-drive-credentials-json')}\n\n")
            
            # Authentication & Security
            f.write("# Authentication & Security\n")
            f.write(f"JWT_SECRET={self.current_config.get('JWT_SECRET', self.generate_jwt_secret())}\n")
            f.write(f"JWT_ALGORITHM={self.current_config.get('JWT_ALGORITHM', 'HS256')}\n\n")
            
            # Application Configuration
            f.write("# Application Configuration\n")
            f.write(f"ENVIRONMENT={self.current_config.get('ENVIRONMENT', 'development')}\n")
            f.write(f"DEBUG={self.current_config.get('DEBUG', 'true')}\n")
            f.write(f"API_HOST={self.current_config.get('API_HOST', 'localhost')}\n")
            f.write(f"API_PORT={self.current_config.get('API_PORT', '8000')}\n")

    def generate_jwt_secret(self) -> str:
        """Generate a secure JWT secret"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(64))

    def get_user_input(self, prompt: str, current_value: str = "", required: bool = True) -> str:
        """Get user input with current value display"""
        if current_value and not current_value.startswith('your-'):
            display_value = current_value[:20] + "..." if len(current_value) > 20 else current_value
            prompt_text = f"{prompt} [Current: {display_value}]: "
        else:
            prompt_text = f"{prompt}: "
        
        value = input(prompt_text).strip()
        if not value and current_value:
            return current_value
        elif not value and required:
            print("❌ This field is required!")
            return self.get_user_input(prompt, current_value, required)
        return value or current_value

    def setup_openai(self):
        """Setup OpenAI API key"""
        print("\n🤖 OpenAI API Key Setup")
        print("=" * 50)
        print("OpenAI powers the AI agent and embeddings for the RAG system.")
        print("\nInstructions:")
        print("1. Go to: https://platform.openai.com/api-keys")
        print("2. Click 'Create new secret key'")
        print("3. Copy the key (starts with 'sk-')")
        
        current_key = self.current_config.get('OPENAI_API_KEY', '')
        api_key = self.get_user_input("OpenAI API Key", current_key)
        
        if api_key and api_key.startswith('sk-'):
            self.current_config['OPENAI_API_KEY'] = api_key
            print("✅ OpenAI API key saved!")
            return True
        else:
            print("❌ Invalid OpenAI API key format. Should start with 'sk-'")
            return False

    def setup_supabase(self):
        """Setup Supabase configuration"""
        print("\n🗄️ Supabase Database Setup")
        print("=" * 50)
        print("Supabase provides the vector database and document storage.")
        print("\nInstructions:")
        print("1. Go to: https://supabase.com")
        print("2. Create a new project")
        print("3. Go to Settings → API")
        print("4. Copy the URL and keys")
        
        # Get Supabase URL
        current_url = self.current_config.get('SUPABASE_URL', '')
        url = self.get_user_input("Supabase Project URL", current_url)
        
        # Get Service Key
        current_service_key = self.current_config.get('SUPABASE_SERVICE_KEY', '')
        service_key = self.get_user_input("Supabase Service Key", current_service_key)
        
        # Get Anon Key
        current_anon_key = self.current_config.get('SUPABASE_ANON_KEY', '')
        anon_key = self.get_user_input("Supabase Anon Key", current_anon_key)
        
        if url and service_key and anon_key:
            self.current_config['SUPABASE_URL'] = url
            self.current_config['SUPABASE_SERVICE_KEY'] = service_key
            self.current_config['SUPABASE_ANON_KEY'] = anon_key
            print("✅ Supabase configuration saved!")
            return True
        
        return False

    def setup_optional_apis(self):
        """Setup optional API keys"""
        print("\n📁 Optional APIs Setup")
        print("=" * 50)
        print("These APIs enable document synchronization features.")
        
        # Dropbox setup
        print("\n🔹 Dropbox API (Optional)")
        setup_dropbox = input("Set up Dropbox API? (y/n): ").lower() == 'y'
        
        if setup_dropbox:
            print("\nDropbox Instructions:")
            print("1. Go to: https://www.dropbox.com/developers/apps")
            print("2. Create a new app")
            print("3. Generate an access token")
            
            current_token = self.current_config.get('DROPBOX_ACCESS_TOKEN', '')
            token = self.get_user_input("Dropbox Access Token", current_token, required=False)
            if token:
                self.current_config['DROPBOX_ACCESS_TOKEN'] = token
                print("✅ Dropbox API configured!")
        
        # Google Drive setup
        print("\n🔹 Google Drive API (Optional)")
        setup_gdrive = input("Set up Google Drive API? (y/n): ").lower() == 'y'
        
        if setup_gdrive:
            print("\nGoogle Drive Instructions:")
            print("1. Go to: https://console.developers.google.com")
            print("2. Create project and enable Drive API")
            print("3. Create service account credentials")
            
            current_creds = self.current_config.get('GOOGLE_DRIVE_CREDENTIALS', '')
            creds = self.get_user_input("Google Drive Credentials JSON", current_creds, required=False)
            if creds:
                self.current_config['GOOGLE_DRIVE_CREDENTIALS'] = creds
                print("✅ Google Drive API configured!")

    def run_setup(self):
        """Run the complete setup process"""
        print("🌱 Renewable Energy RAG System - API Keys Setup")
        print("=" * 60)
        print("This script will help you configure all the API keys needed for the system.")
        print("\n🔑 Required APIs:")
        print("  • OpenAI - AI agent and embeddings")
        print("  • Supabase - Vector database and storage")
        print("\n🔑 Optional APIs:")
        print("  • Dropbox - Document synchronization")
        print("  • Google Drive - Document synchronization")
        
        proceed = input("\n🚀 Ready to start? (y/n): ").lower()
        if proceed != 'y':
            print("Setup cancelled.")
            return
        
        # Setup required APIs
        success_count = 0
        
        if self.setup_openai():
            success_count += 1
        
        if self.setup_supabase():
            success_count += 1
        
        # Setup optional APIs
        self.setup_optional_apis()
        
        # Generate JWT secret if not present
        if not self.current_config.get('JWT_SECRET'):
            self.current_config['JWT_SECRET'] = self.generate_jwt_secret()
            print("\n🔐 Generated secure JWT secret")
        
        # Save configuration
        self.save_config()
        
        # Final summary
        print("\n🎉 Setup Complete!")
        print("=" * 60)
        print(f"✅ Configured {success_count}/2 required APIs")
        print(f"📁 Configuration saved to: {self.env_file.absolute()}")
        
        if success_count == 2:
            print("\n🚀 Your system is ready to run!")
            print("\nNext steps:")
            print("1. Set up database: Run the SQL in backend/database_schema.sql in Supabase")
            print("2. Test the system: python backend/test_rag_system.py")
            print("3. Start the server: uvicorn backend.main:app --reload")
        else:
            print("\n⚠️ Some required APIs are not configured.")
            print("The system may not work properly until all required keys are set up.")

def main():
    """Main entry point"""
    setup = APIKeySetup()
    setup.run_setup()

if __name__ == "__main__":
    main() 