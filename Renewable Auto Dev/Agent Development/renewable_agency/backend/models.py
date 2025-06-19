"""
Database models for the Renewable Energy RAG System
Updated to match existing Supabase schema
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, UUID4
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

# Organization Models
class OrganizationBase(BaseModel):
    name: str
    slug: str

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# User Models
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    role: UserRole

class UserCreate(UserBase):
    organization_id: Optional[UUID4] = None

class User(UserBase):
    id: UUID4
    organization_id: Optional[UUID4] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Client Models
class ClientBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class ClientCreate(ClientBase):
    organization_id: Optional[UUID4] = None

class Client(ClientBase):
    id: UUID4
    organization_id: Optional[UUID4] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Project Models
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: ProjectStatus

class ProjectCreate(ProjectBase):
    organization_id: Optional[UUID4] = None

class Project(ProjectBase):
    id: UUID4
    organization_id: Optional[UUID4] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Project Details Models
class ProjectDetailsBase(BaseModel):
    name: str
    owner: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    power_market: Optional[str] = None
    status: Optional[str] = None
    capacity_mw: Optional[float] = None
    technology: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None

class ProjectDetailsCreate(ProjectDetailsBase):
    project_id: UUID4

class ProjectDetails(ProjectDetailsBase):
    id: UUID4
    project_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Document Models
class DocumentBase(BaseModel):
    name: str
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DocumentCreate(DocumentBase):
    project_id: Optional[UUID4] = None

class Document(DocumentBase):
    id: UUID4
    project_id: Optional[UUID4] = None
    vector_embedding: Optional[List[float]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Agent Data Models
class AgentDataBase(BaseModel):
    agent_type: str
    data: Dict[str, Any]

class AgentDataCreate(AgentDataBase):
    project_id: Optional[UUID4] = None

class AgentData(AgentDataBase):
    id: UUID4
    project_id: Optional[UUID4] = None
    vector_embedding: Optional[List[float]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Audit Log Models
class AuditLogBase(BaseModel):
    action: str
    table_name: str
    record_id: UUID4
    old_data: Optional[Dict[str, Any]] = None
    new_data: Optional[Dict[str, Any]] = None

class AuditLogCreate(AuditLogBase):
    user_id: Optional[UUID4] = None

class AuditLog(AuditLogBase):
    id: UUID4
    user_id: Optional[UUID4] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Chat/Query Models (for API responses)
class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message/query")
    project_id: Optional[UUID4] = Field(None, description="Project context for the query")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI agent's response")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents used")
    conversation_id: str = Field(..., description="Conversation identifier")
    timestamp: datetime = Field(default_factory=datetime.now)

# Document Upload Models
class DocumentUploadRequest(BaseModel):
    project_id: UUID4
    file_name: str
    file_content: str
    metadata: Optional[Dict[str, Any]] = None

class DocumentUploadResponse(BaseModel):
    document_id: UUID4
    status: str
    message: str

# Search Models
class SearchRequest(BaseModel):
    query: str
    project_id: Optional[UUID4] = None
    limit: int = Field(default=5, ge=1, le=50)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

class SearchResult(BaseModel):
    document_id: UUID4
    document_name: str
    content_snippet: str
    similarity_score: float
    metadata: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int
    query: str 