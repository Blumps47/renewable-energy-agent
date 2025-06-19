"""
Fixed API Routes with correct parameter ordering
"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Pydantic Models
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

# Mock services function for now
def get_services():
    """Get service instances"""
    return {
        "document_ingestion": None,
        "document_processor": None,
        "rag_engine": None,
        "enhanced_agent": None,
        "project_service": None
    }

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Mock user authentication"""
    # For now, return a mock user ID
    return "mock-user-123"

# Fixed Routes with correct parameter order
@router.post("/documents/upload", response_model=Dict[str, Any])
async def upload_document(
    background_tasks: BackgroundTasks,
    project_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """Upload a document file."""
    try:
        return {
            "success": True,
            "message": "Document upload endpoint working",
            "filename": file.filename,
            "project_id": project_id
        }
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/sync/dropbox", response_model=Dict[str, Any])
async def sync_dropbox_folder(
    background_tasks: BackgroundTasks,
    sync_request: DropboxSyncRequest,
    current_user: str = Depends(get_current_user)
):
    """Synchronize documents from Dropbox."""
    try:
        return {
            "success": True,
            "message": "Dropbox sync endpoint working",
            "project_id": sync_request.project_id
        }
    except Exception as e:
        logger.error(f"Error starting Dropbox sync: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/sync/google-drive", response_model=Dict[str, Any])
async def sync_google_drive_folder(
    background_tasks: BackgroundTasks,
    sync_request: GoogleDriveSyncRequest,
    current_user: str = Depends(get_current_user)
):
    """Synchronize documents from Google Drive."""
    try:
        return {
            "success": True,
            "message": "Google Drive sync endpoint working",
            "project_id": sync_request.project_id
        }
    except Exception as e:
        logger.error(f"Error starting Google Drive sync: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/{document_id}/process", response_model=Dict[str, Any])
async def process_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
):
    """Process or reprocess a document."""
    try:
        return {
            "success": True,
            "document_id": document_id,
            "message": "Document processing endpoint working"
        }
    except Exception as e:
        logger.error(f"Error starting document processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Basic routes without BackgroundTasks
@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Renewable Energy RAG API is running",
        "version": "2.0.0"
    }

@router.post("/chat", response_model=Dict[str, Any])
async def basic_chat(
    message: Dict[str, str],
    current_user: str = Depends(get_current_user)
):
    """Basic chat endpoint for testing."""
    try:
        return {
            "success": True,
            "response": f"Echo: {message.get('message', 'No message provided')}",
            "user": current_user
        }
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects", response_model=Dict[str, Any])
async def list_projects(
    status: Optional[str] = None,
    market: Optional[str] = None,
    include_stats: bool = True,
    current_user: str = Depends(get_current_user)
):
    """List projects for the current user."""
    try:
        return {
            "success": True,
            "projects": [],
            "count": 0,
            "message": "Projects endpoint working"
        }
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/projects", response_model=Dict[str, Any])
async def create_project(
    project: ProjectCreate,
    current_user: str = Depends(get_current_user)
):
    """Create a new project."""
    try:
        return {
            "success": True,
            "project": project.dict(),
            "message": "Project creation endpoint working"
        }
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 