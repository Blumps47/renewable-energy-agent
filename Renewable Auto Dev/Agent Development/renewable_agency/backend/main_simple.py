"""
Simple FastAPI server for testing the renewable energy RAG system
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

# Load environment variables
load_dotenv()

# Debug info
USE_MOCK_MODE = os.getenv("USE_MOCK_MODE", "false").lower() == "true"
print(f"🎭 USE_MOCK_MODE: {USE_MOCK_MODE}")

# Check OpenAI API key
openai_key = os.getenv("OPENAI_API_KEY")
print(f"🔑 OpenAI API Key found: {'Yes' if openai_key else 'No'}")
if openai_key:
    print(f"🔑 Key length: {len(openai_key)} characters")

# Create FastAPI app
app = FastAPI(
    title="Renewable Energy RAG API",
    description="AI-powered renewable energy project analysis and consultation system",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Models
class ChatRequest(BaseModel):
    message: str
    userId: str
    conversationId: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    success: bool
    message: str

# Mock authentication (make it optional)
def get_current_user(token = Depends(security)) -> str:
    return "test-user"

# Routes
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint"""
    return {
        "message": "Renewable Energy RAG API v2.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "message": "Renewable Energy RAG API is running",
            "version": "2.0.0",
            "openai_configured": bool(openai_key),
            "supabase_configured": bool(os.getenv("SUPABASE_URL")),
            "dropbox_configured": bool(os.getenv("DROPBOX_ACCESS_TOKEN"))
        }
    }

@app.post("/chat", response_model=Dict[str, Any])
async def chat(chat_request: ChatRequest):
    """Simple chat endpoint for testing"""
    try:
        # Test OpenAI connection
        if not USE_MOCK_MODE and openai_key:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful renewable energy consultant. Provide detailed information about renewable energy technologies, calculations, and sustainability practices."},
                    {"role": "user", "content": chat_request.message}
                ],
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
        else:
            ai_response = f"Mock response to: {chat_request.message}. This is a renewable energy consultation system."
        
        # Return in ApiResponse format that frontend expects
        return {
            "success": True,
            "data": {
                "response": ai_response,
                "math_response": {
                    "result": 0,
                    "operation": "information",
                    "explanation": "N/A",
                    "renewable_context": ai_response,
                    "confidence": 90
                }
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Chat failed: {str(e)}",
            "message": "Failed to process chat request"
        }

@app.get("/test-apis", response_model=Dict[str, Any])
async def test_apis():
    """Test all API connections"""
    results = {}
    
    # Test OpenAI
    try:
        if openai_key:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            results["openai"] = {"status": "success", "message": "Connected"}
        else:
            results["openai"] = {"status": "error", "message": "No API key"}
    except Exception as e:
        results["openai"] = {"status": "error", "message": str(e)}
    
    # Test Supabase
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        if supabase_url and supabase_key:
            from supabase import create_client
            supabase = create_client(supabase_url, supabase_key)
            result = supabase.table('users').select('id').limit(1).execute()
            results["supabase"] = {"status": "success", "message": "Connected"}
        else:
            results["supabase"] = {"status": "error", "message": "No credentials"}
    except Exception as e:
        results["supabase"] = {"status": "error", "message": str(e)}
    
    # Test Dropbox
    try:
        dropbox_token = os.getenv("DROPBOX_ACCESS_TOKEN")
        if dropbox_token:
            import dropbox
            dbx = dropbox.Dropbox(dropbox_token)
            account = dbx.users_get_current_account()
            results["dropbox"] = {"status": "success", "message": f"Connected as {account.name.display_name}"}
        else:
            results["dropbox"] = {"status": "error", "message": "No access token"}
    except Exception as e:
        results["dropbox"] = {"status": "error", "message": str(e)}
    
    return {
        "success": True,
        "results": results
    }

if __name__ == "__main__":
    # Run the server
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "localhost")
    
    print(f"🚀 Starting server at http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    
    uvicorn.run(
        "main_simple:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    ) 