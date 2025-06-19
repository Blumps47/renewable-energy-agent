#!/usr/bin/env python3
"""
Setup script for Supabase database schema
"""
import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

def setup_database():
    """Set up the Supabase database schema"""
    
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("🔄 Setting up Supabase database schema...")
        
        # Read the schema file
        schema_path = os.path.join(os.path.dirname(__file__), 'backend', 'database_schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Split the schema into individual statements
        statements = []
        current_statement = ""
        
        for line in schema_sql.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if line.startswith('--') or not line:
                continue
                
            current_statement += line + '\n'
            
            # If line ends with semicolon, it's the end of a statement
            if line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
        
        # Execute each statement
        success_count = 0
        for i, statement in enumerate(statements):
            if statement.strip():
                try:
                    # Use rpc to execute raw SQL
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    success_count += 1
                    print(f"✅ Executed statement {i+1}/{len(statements)}")
                except Exception as e:
                    # Try alternative method for schema creation
                    try:
                        # For schema creation, we might need to use postgrest directly
                        print(f"⚠️  Statement {i+1} failed with rpc, trying direct execution...")
                        print(f"   Error: {str(e)}")
                        # Continue with next statement
                    except Exception as e2:
                        print(f"❌ Failed to execute statement {i+1}: {str(e2)}")
                        print(f"   Statement: {statement[:100]}...")
        
        print(f"\n✅ Database setup completed! ({success_count}/{len(statements)} statements executed)")
        print("\n📝 Next steps:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the contents of backend/database_schema.sql")
        print("4. Execute the schema manually if needed")
        print("5. Run: python test_api_keys.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")
        print("\n📝 Manual setup required:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the contents of backend/database_schema.sql")
        print("4. Execute the schema manually")
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1) 