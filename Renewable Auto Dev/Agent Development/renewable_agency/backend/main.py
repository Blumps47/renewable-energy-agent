"""
FastAPI application for Renewable Energy Analyst Agent with RAG System
"""

import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from agent.renewable_agent import RenewableEnergyAgent
from agent.models import MathResponse, ChatMessage, UserRegistration, AgentResponse
from api_routes import router as rag_router
from datetime import datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Renewable Energy Analyst API with RAG System...")
    yield
    # Shutdown
    print("🛑 Shutting down Renewable Energy Analyst API...")


# Initialize FastAPI app
app = FastAPI(
    title="Renewable Energy Analyst Agent API with RAG",
    description="A specialized AI agent for renewable energy analysis with document intelligence and RAG capabilities",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include RAG router
app.include_router(rag_router)

# Initialize the agent
renewable_agent = RenewableEnergyAgent()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Renewable Energy Analyst Agent API with RAG System",
        "version": "2.0.0",
        "status": "active",
        "features": [
            "AI Agent Chat",
            "Document Intelligence",
            "RAG System",
            "Project Management",
            "Multi-tenant Security"
        ],
        "documentation": "/docs",
        "rag_endpoints": "/api/rag"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "renewable-energy-agent-rag",
        "version": "2.0.0",
        "features": {
            "basic_agent": "active",
            "rag_system": "active",
            "document_processing": "active",
            "project_management": "active"
        }
    }


@app.post("/api/chat", response_model=AgentResponse)
async def chat_with_agent(message: ChatMessage):
    """
    Send a message to the agent and receive a structured response
    
    Args:
        message: ChatMessage containing user's message and optional context
        
    Returns:
        AgentResponse: Structured response with MathResponse data
    """
    try:
        # Process the message through the agent
        response = await renewable_agent.process_message(
            message.message, 
            message.user_id
        )
        
        return AgentResponse(
            success=True,
            data=response.model_dump(),
            error=None,
            message="Agent response generated successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing agent request: {str(e)}"
        )


@app.post("/api/register", response_model=AgentResponse)
async def register_user(user_data: UserRegistration):
    """
    Register a new user with name and email
    
    Args:
        user_data: UserRegistration with name and email
        
    Returns:
        AgentResponse: Registration result with user ID
    """
    try:
        # Create user ID from email hash
        user_id = f"user_{hash(user_data.email) % 10000}"
        
        # Store user data (in production, this would go to database)
        user_info = {
            "user_id": user_id,
            "name": user_data.name,
            "email": user_data.email,
            "interests": user_data.interests,
            "registered_at": datetime.now().isoformat()
        }
        
        return AgentResponse(
            success=True,
            data=user_info,
            error=None,
            message=f"User {user_data.name} registered successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Registration failed: {str(e)}"
        )


@app.get("/api/conversation/{user_id}")
async def get_conversation_history(user_id: str):
    """
    Get conversation history for a specific user
    
    Args:
        user_id: User identifier
        
    Returns:
        dict: Conversation history and user data
    """
    try:
        history = renewable_agent.get_conversation_history()
        user_data = renewable_agent.get_user_data()
        
        # Filter history for specific user (in production, use proper filtering)
        filtered_history = [
            msg for msg in history 
            if msg.get("user_id") == user_id or msg.get("role") == "assistant"
        ]
        
        return {
            "user_id": user_id,
            "conversation_history": filtered_history,
            "user_data": user_data,
            "total_messages": len(filtered_history)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving conversation history: {str(e)}"
        )


@app.post("/api/user/preferences")
async def set_user_preference(user_id: str, key: str, value: str):
    """
    Set a user preference
    
    Args:
        user_id: User identifier
        key: Preference key
        value: Preference value
        
    Returns:
        dict: Success confirmation
    """
    try:
        renewable_agent.set_user_preference(f"{user_id}_{key}", value)
        
        return {
            "success": True,
            "message": f"Preference {key} set for user {user_id}",
            "user_id": user_id,
            "preference": {key: value}
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error setting user preference: {str(e)}"
        )


@app.get("/api/user/preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """
    Get user preferences
    
    Args:
        user_id: User identifier
        
    Returns:
        dict: User preferences
    """
    try:
        all_prefs = renewable_agent.get_user_preferences()
        
        # Filter preferences for specific user
        user_prefs = {
            k.replace(f"{user_id}_", ""): v 
            for k, v in all_prefs.items() 
            if k.startswith(f"{user_id}_")
        }
        
        return {
            "user_id": user_id,
            "preferences": user_prefs
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user preferences: {str(e)}"
        )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested endpoint was not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle internal server errors"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "details": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "localhost")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print(f"🌱 Starting Renewable Energy Analyst API on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 