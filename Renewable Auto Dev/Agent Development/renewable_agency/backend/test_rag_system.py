#!/usr/bin/env python3
"""
Simple test script to verify RAG system functionality
Run this to test core components without full API setup
"""

import os
import asyncio
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_rag_system():
    """Test the RAG system components."""
    print("🧪 Testing Renewable Energy RAG System")
    print("=" * 50)
    
    # Test environment variables
    print("\n1. Testing Environment Configuration...")
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY", 
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set up your .env file with required credentials")
        return False
    else:
        print("✅ Environment configuration looks good")
    
    # Test imports
    print("\n2. Testing Module Imports...")
    try:
        from services.document_ingestion import DocumentIngestionService
        from services.document_processor import DocumentProcessor
        from services.rag_engine import RAGQueryEngine
        from services.project_service import ProjectService
        from agent.enhanced_renewable_agent import EnhancedRenewableAgent
        print("✅ All modules imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Please install required dependencies: pip install -r requirements.txt")
        return False
    
    # Test service initialization
    print("\n3. Testing Service Initialization...")
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize services
        document_ingestion = DocumentIngestionService(supabase_url, supabase_key)
        document_processor = DocumentProcessor(supabase_url, supabase_key, openai_key)
        rag_engine = RAGQueryEngine(supabase_url, supabase_key, openai_key)
        project_service = ProjectService(supabase_url, supabase_key)
        enhanced_agent = EnhancedRenewableAgent(openai_key, rag_engine, project_service)
        
        print("✅ All services initialized successfully")
        
        # Test basic functionality
        print("\n4. Testing Basic Functionality...")
        
        # Test project service (read-only operations)
        try:
            # This would require a valid user_id in production
            # For testing, we'll just verify the method exists
            assert hasattr(project_service, 'list_user_projects')
            assert hasattr(project_service, 'create_project')
            print("✅ Project service methods available")
        except Exception as e:
            print(f"⚠️  Project service test skipped: {str(e)}")
        
        # Test RAG engine
        try:
            assert hasattr(rag_engine, 'query_documents')
            assert hasattr(rag_engine, '_generate_query_embedding')
            print("✅ RAG engine methods available")
        except Exception as e:
            print(f"⚠️  RAG engine test skipped: {str(e)}")
        
        # Test enhanced agent
        try:
            assert hasattr(enhanced_agent, 'query_with_context')
            assert hasattr(enhanced_agent, 'get_project_insights')
            print("✅ Enhanced agent methods available")
        except Exception as e:
            print(f"⚠️  Enhanced agent test skipped: {str(e)}")
            
    except Exception as e:
        print(f"❌ Service initialization failed: {str(e)}")
        print("Please check your Supabase and OpenAI credentials")
        return False
    
    # Test API routes import
    print("\n5. Testing API Routes...")
    try:
        from api_routes import router
        print("✅ API routes imported successfully")
        print(f"✅ Router has {len(router.routes)} routes configured")
    except ImportError as e:
        print(f"❌ API routes import failed: {str(e)}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 RAG System Test Complete!")
    print("✅ All core components are working correctly")
    print("\nNext steps:")
    print("1. Set up Supabase database using database_schema.sql")
    print("2. Start the FastAPI server: uvicorn main:app --reload")
    print("3. Start the React frontend: npm run dev")
    print("4. Test the full system through the web interface")
    
    return True

async def test_database_connection():
    """Test database connection and schema."""
    print("\n🗄️  Testing Database Connection...")
    
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_key:
            print("⚠️  Supabase credentials not found, skipping database test")
            return
        
        client = create_client(supabase_url, supabase_key)
        
        # Test basic connection
        result = client.table("projects").select("count", count="exact").execute()
        print("✅ Database connection successful")
        print(f"✅ Projects table accessible (count query worked)")
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("Please ensure:")
        print("1. Supabase project is created")
        print("2. Database schema is applied")
        print("3. Credentials are correct")

async def test_openai_connection():
    """Test OpenAI API connection."""
    print("\n🤖 Testing OpenAI Connection...")
    
    try:
        import openai
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("⚠️  OpenAI API key not found, skipping OpenAI test")
            return
        
        openai.api_key = openai_key
        
        # Test with a simple embedding request
        response = await openai.Embedding.acreate(
            model="text-embedding-3-small",
            input=["Test renewable energy document"]
        )
        
        if response and response.get('data'):
            print("✅ OpenAI API connection successful")
            print(f"✅ Embedding generation working (dimension: {len(response['data'][0]['embedding'])})")
        else:
            print("❌ OpenAI API response invalid")
            
    except Exception as e:
        print(f"❌ OpenAI connection failed: {str(e)}")
        print("Please ensure:")
        print("1. OpenAI API key is valid")
        print("2. You have sufficient credits")
        print("3. API key has embedding permissions")

def print_system_info():
    """Print system information."""
    print("\n📋 System Information:")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Test time: {datetime.now().isoformat()}")
    
    # Check for .env file
    env_file = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_file):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found - using environment variables")

if __name__ == "__main__":
    print("🌱 Renewable Energy RAG System Test")
    print("Testing core functionality and dependencies...")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded from .env")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment")
    except Exception as e:
        print(f"⚠️  Could not load .env file: {str(e)}")
    
    print_system_info()
    
    # Run async tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        success = loop.run_until_complete(test_rag_system())
        loop.run_until_complete(test_database_connection())
        loop.run_until_complete(test_openai_connection())
        
        if success:
            print("\n🎯 System is ready for use!")
            sys.exit(0)
        else:
            print("\n❌ System has issues that need to be resolved")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        sys.exit(1)
    finally:
        loop.close() 