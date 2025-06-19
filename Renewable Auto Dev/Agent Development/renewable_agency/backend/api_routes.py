"""
API Routes for Renewable Energy RAG System

Comprehensive FastAPI routes for document management, RAG queries,
project management, and enhanced chat functionality.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import jwt

from .services.document_ingestion import DocumentIngestionService
from .services.document_processor import DocumentProcessor
from .services.rag_engine import RAGQueryEngine
from .services.project_service import ProjectService
from .agent.enhanced_renewable_agent import EnhancedRenewableAgent, AgentResponse

logger = logging.getLogger(__name__)

# Initialize security
security = HTTPBearer()

# Pydantic models for request/response
class ProjectCreate(BaseModel):
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    market: Optional[str] = Field(None, description="Renewable energy market type")
    location: Optional[str] = Field(None, description="Project location")
    owner: Optional[str] = Field(None, description="Project owner/developer")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    market: Optional[str] = None
    location: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DropboxSyncRequest(BaseModel):
    project_id: str = Field(..., description="Project UUID to associate documents with")
    access_token: str = Field(..., description="Dropbox access token")
    folder_path: str = Field(default="", description="Dropbox folder path")

class GoogleDriveSyncRequest(BaseModel):
    project_id: str = Field(..., description="Project UUID to associate documents with")
    credentials: Dict[str, Any] = Field(..., description="Google OAuth2 credentials")
    folder_id: Optional[str] = Field(None, description="Google Drive folder ID")

class EnhancedChatRequest(BaseModel):
    message: str = Field(..., description="User message/query")
    project_ids: Optional[List[str]] = Field(None, description="Specific project IDs for context")
    use_rag: bool = Field(default=True, description="Whether to use RAG for context")
    conversation_history: Optional[List[Dict[str, str]]] = Field(None, description="Previous conversation messages")

class DocumentQuery(BaseModel):
    query: str = Field(..., description="Search query")
    project_ids: Optional[List[str]] = Field(None, description="Project IDs to search within")
    limit: int = Field(default=5, description="Maximum results to return")
    similarity_threshold: float = Field(default=0.7, description="Minimum similarity threshold")

class ProjectInsightsRequest(BaseModel):
    project_id: str = Field(..., description="Project UUID")
    insight_type: str = Field(default="general", description="Type of insights to generate")

class ProjectSummaryRequest(BaseModel):
    project_id: str = Field(..., description="Project UUID")
    summary_type: str = Field(default="executive", description="Type of summary to generate")

class ProjectComparisonRequest(BaseModel):
    project_ids: List[str] = Field(..., description="Project UUIDs to compare")
    comparison_aspects: Optional[List[str]] = Field(None, description="Specific aspects to focus on")

# Initialize services (these would be dependency injected in production)
def get_services():
    """Get initialized services."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not all([supabase_url, supabase_key, openai_api_key]):
        raise HTTPException(
            status_code=500,
            detail="Missing required environment variables"
        )
    
    # Initialize services
    document_ingestion = DocumentIngestionService(supabase_url, supabase_key)
    document_processor = DocumentProcessor(supabase_url, supabase_key, openai_api_key)
    rag_engine = RAGQueryEngine(supabase_url, supabase_key, openai_api_key)
    project_service = ProjectService(supabase_url, supabase_key)
    enhanced_agent = EnhancedRenewableAgent(
        openai_api_key, rag_engine, project_service
    )
    
    return {
        "document_ingestion": document_ingestion,
        "document_processor": document_processor,
        "rag_engine": rag_engine,
        "project_service": project_service,
        "enhanced_agent": enhanced_agent
    }

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from JWT token."""
    try:
        # In production, you'd verify the JWT token properly
        # For now, we'll use a simple approach
        token = credentials.credentials
        
        # Decode JWT token (replace with proper verification)
        payload = jwt.decode(
            token, 
            os.getenv("JWT_SECRET", "your-secret-key"), 
            algorithms=["HS256"]
        )
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return user_id
        
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Create router
router = APIRouter(prefix="/api/rag", tags=["RAG System"])

# Project Management Routes
@router.post("/projects", response_model=Dict[str, Any])
async def create_project(
    project: ProjectCreate,
    current_user: str = Depends(get_current_user)
):
    """Create a new renewable energy project."""
    try:
        services = get_services()
        project_data = await services["project_service"].create_project(
            user_id=current_user,
            name=project.name,
            description=project.description,
            market=project.market,
            location=project.location,
            owner=project.owner,
            metadata=project.metadata
        )
        
        return {
            "success": True,
            "project": project_data,
            "message": "Project created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects", response_model=Dict[str, Any])
async def list_projects(
    status: Optional[str] = None,
    market: Optional[str] = None,
    include_stats: bool = True,
    current_user: str = Depends(get_current_user)
):
    """List all projects for the current user."""
    try:
        services = get_services()
        projects = await services["project_service"].list_user_projects(
            user_id=current_user,
            status=status,
            market=market,
            include_stats=include_stats
        )
        
        return {
            "success": True,
            "projects": projects,
            "count": len(projects)
        }
        
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}", response_model=Dict[str, Any])
async def get_project(
    project_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get a specific project by ID."""
    try:
        services = get_services()
        project = await services["project_service"].get_project(
            user_id=current_user,
            project_id=project_id
        )
        
        return {
            "success": True,
            "project": project
        }
        
    except Exception as e:
        logger.error(f"Error getting project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/projects/{project_id}", response_model=Dict[str, Any])
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: str = Depends(get_current_user)
):
    """Update an existing project."""
    try:
        services = get_services()
        updated_project = await services["project_service"].update_project(
            user_id=current_user,
            project_id=project_id,
            **project_update.dict(exclude_unset=True)
        )
        
        return {
            "success": True,
            "project": updated_project,
            "message": "Project updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/projects/{project_id}", response_model=Dict[str, Any])
async def delete_project(
    project_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete a project and all associated documents."""
    try:
        services = get_services()
        success = await services["project_service"].delete_project(
            user_id=current_user,
            project_id=project_id
        )
        
        return {
            "success": success,
            "message": "Project deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Document Management Routes
@router.post("/documents/sync/dropbox", response_model=Dict[str, Any])
async def sync_dropbox_folder(
    sync_request: DropboxSyncRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Synchronize documents from Dropbox."""
    try:
        services = get_services()
        
        # Start sync in background
        background_tasks.add_task(
            _sync_and_process_dropbox,
            services["document_ingestion"],
            services["document_processor"],
            current_user,
            sync_request.project_id,
            sync_request.access_token,
            sync_request.folder_path
        )
        
        return {
            "success": True,
            "message": "Dropbox sync started in background",
            "project_id": sync_request.project_id
        }
        
    except Exception as e:
        logger.error(f"Error starting Dropbox sync: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/sync/google-drive", response_model=Dict[str, Any])
async def sync_google_drive_folder(
    sync_request: GoogleDriveSyncRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Synchronize documents from Google Drive."""
    try:
        services = get_services()
        
        # Start sync in background
        background_tasks.add_task(
            _sync_and_process_google_drive,
            services["document_ingestion"],
            services["document_processor"],
            current_user,
            sync_request.project_id,
            sync_request.credentials,
            sync_request.folder_id
        )
        
        return {
            "success": True,
            "message": "Google Drive sync started in background",
            "project_id": sync_request.project_id
        }
        
    except Exception as e:
        logger.error(f"Error starting Google Drive sync: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/upload", response_model=Dict[str, Any])
async def upload_document(
    background_tasks: BackgroundTasks,
    project_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """Upload a document file."""
    try:
        services = get_services()
        
        # Read file content
        file_content = await file.read()
        
        # Upload document
        document_id = await services["document_ingestion"].upload_local_document(
            user_id=current_user,
            project_id=project_id,
            file_path=file.filename,
            file_name=file.filename,
            file_content=file_content
        )
        
        # Process document in background
        background_tasks.add_task(
            services["document_processor"].process_document,
            document_id
        )
        
        return {
            "success": True,
            "document_id": document_id,
            "message": "Document uploaded and processing started",
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=Dict[str, Any])
async def list_documents(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """List documents for the current user."""
    try:
        services = get_services()
        documents = await services["document_ingestion"].get_user_documents(
            user_id=current_user,
            project_id=project_id,
            status=status
        )
        
        return {
            "success": True,
            "documents": documents,
            "count": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/{document_id}/process", response_model=Dict[str, Any])
async def process_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Process or reprocess a document."""
    try:
        services = get_services()
        
        # Start processing in background
        background_tasks.add_task(
            services["document_processor"].process_document,
            document_id
        )
        
        return {
            "success": True,
            "document_id": document_id,
            "message": "Document processing started"
        }
        
    except Exception as e:
        logger.error(f"Error starting document processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}/status", response_model=Dict[str, Any])
async def get_document_status(
    document_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get document processing status."""
    try:
        services = get_services()
        status = await services["document_processor"].get_processing_status(document_id)
        
        return {
            "success": True,
            "document_id": document_id,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Error getting document status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}", response_model=Dict[str, Any])
async def delete_document(
    document_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete a document and its chunks."""
    try:
        services = get_services()
        success = await services["document_ingestion"].delete_document(
            user_id=current_user,
            document_id=document_id
        )
        
        return {
            "success": success,
            "message": "Document deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# RAG Query Routes
@router.post("/query", response_model=Dict[str, Any])
async def query_documents(
    query: DocumentQuery,
    current_user: str = Depends(get_current_user)
):
    """Query documents using RAG."""
    try:
        services = get_services()
        results = await services["rag_engine"].query_documents(
            user_id=current_user,
            query=query.query,
            project_ids=query.project_ids,
            limit=query.limit,
            similarity_threshold=query.similarity_threshold
        )
        
        return {
            "success": True,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error querying documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/enhanced", response_model=Dict[str, Any])
async def enhanced_chat(
    chat_request: EnhancedChatRequest,
    current_user: str = Depends(get_current_user)
):
    """Enhanced chat with RAG integration."""
    try:
        services = get_services()
        response = await services["enhanced_agent"].query_with_context(
            user_id=current_user,
            query=chat_request.message,
            project_ids=chat_request.project_ids,
            use_rag=chat_request.use_rag,
            conversation_history=chat_request.conversation_history
        )
        
        return {
            "success": True,
            "response": response.dict()
        }
        
    except Exception as e:
        logger.error(f"Error in enhanced chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Project Analysis Routes
@router.post("/projects/insights", response_model=Dict[str, Any])
async def get_project_insights(
    insights_request: ProjectInsightsRequest,
    current_user: str = Depends(get_current_user)
):
    """Get AI-generated project insights."""
    try:
        services = get_services()
        insights = await services["enhanced_agent"].get_project_insights(
            user_id=current_user,
            project_id=insights_request.project_id,
            insight_type=insights_request.insight_type
        )
        
        return {
            "success": True,
            "insights": insights.dict()
        }
        
    except Exception as e:
        logger.error(f"Error generating project insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/summary", response_model=Dict[str, Any])
async def generate_project_summary(
    summary_request: ProjectSummaryRequest,
    current_user: str = Depends(get_current_user)
):
    """Generate project summary."""
    try:
        services = get_services()
        summary = await services["enhanced_agent"].generate_project_summary(
            user_id=current_user,
            project_id=summary_request.project_id,
            summary_type=summary_request.summary_type
        )
        
        return {
            "success": True,
            "summary": summary.dict()
        }
        
    except Exception as e:
        logger.error(f"Error generating project summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects/compare", response_model=Dict[str, Any])
async def compare_projects(
    comparison_request: ProjectComparisonRequest,
    current_user: str = Depends(get_current_user)
):
    """Compare multiple projects."""
    try:
        services = get_services()
        comparison = await services["project_service"].compare_projects(
            user_id=current_user,
            project_ids=comparison_request.project_ids
        )
        
        return {
            "success": True,
            "comparison": comparison
        }
        
    except Exception as e:
        logger.error(f"Error comparing projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/analytics", response_model=Dict[str, Any])
async def get_project_analytics(
    project_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get detailed project analytics."""
    try:
        services = get_services()
        analytics = await services["project_service"].get_project_analytics(
            user_id=current_user,
            project_id=project_id
        )
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Error getting project analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health Check Route
@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint."""
    try:
        # Test basic service initialization
        services = get_services()
        
        return {
            "success": True,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "document_ingestion": "ready",
                "document_processor": "ready",
                "rag_engine": "ready",
                "project_service": "ready",
                "enhanced_agent": "ready"
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Background task functions
async def _sync_and_process_dropbox(
    document_ingestion: DocumentIngestionService,
    document_processor: DocumentProcessor,
    user_id: str,
    project_id: str,
    access_token: str,
    folder_path: str
):
    """Background task to sync and process Dropbox documents."""
    try:
        # Sync documents
        sync_stats = await document_ingestion.sync_dropbox_folder(
            user_id=user_id,
            project_id=project_id,
            access_token=access_token,
            folder_path=folder_path
        )
        
        logger.info(f"Dropbox sync completed: {sync_stats}")
        
        # Process new documents
        await document_processor.batch_process_documents(
            user_id=user_id,
            project_id=project_id,
            status_filter="pending"
        )
        
    except Exception as e:
        logger.error(f"Error in Dropbox sync background task: {str(e)}")

async def _sync_and_process_google_drive(
    document_ingestion: DocumentIngestionService,
    document_processor: DocumentProcessor,
    user_id: str,
    project_id: str,
    credentials: Dict[str, Any],
    folder_id: Optional[str]
):
    """Background task to sync and process Google Drive documents."""
    try:
        # Sync documents
        sync_stats = await document_ingestion.sync_google_drive_folder(
            user_id=user_id,
            project_id=project_id,
            credentials=credentials,
            folder_id=folder_id
        )
        
        logger.info(f"Google Drive sync completed: {sync_stats}")
        
        # Process new documents
        await document_processor.batch_process_documents(
            user_id=user_id,
            project_id=project_id,
            status_filter="pending"
        )
        
    except Exception as e:
        logger.error(f"Error in Google Drive sync background task: {str(e)}") 