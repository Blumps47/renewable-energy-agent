"""Database models for the renewable energy AI agent ecosystem."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class AgentType(str, Enum):
    """Types of AI agents in the system."""
    GENERAL = "general"
    SOLAR = "solar"
    WIND = "wind"
    POLICY = "policy"
    FINANCIAL = "financial"
    ENVIRONMENTAL = "environmental"
    GRID = "grid"


class AgentStatus(str, Enum):
    """Status of AI agents."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class DocumentType(str, Enum):
    """Types of documents in the system."""
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    TEXT = "text"
    MARKDOWN = "markdown"


class ProjectStatus(str, Enum):
    """Status of renewable energy projects."""
    PLANNING = "planning"
    PERMITTING = "permitting"
    CONSTRUCTION = "construction"
    OPERATIONAL = "operational"
    DECOMMISSIONED = "decommissioned"


class Agent(BaseModel):
    """Model for AI agents."""
    id: Optional[str] = None
    name: str = Field(..., description="Agent name")
    type: AgentType = Field(..., description="Agent type")
    description: str = Field(..., description="Agent description")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    status: AgentStatus = Field(default=AgentStatus.ACTIVE, description="Agent status")
    model_config: Dict[str, Any] = Field(default_factory=dict, description="AI model configuration")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Document(BaseModel):
    """Model for documents in the system."""
    id: Optional[str] = None
    filename: str = Field(..., description="Document filename")
    type: DocumentType = Field(..., description="Document type")
    size: int = Field(..., description="Document size in bytes")
    checksum: str = Field(..., description="Document checksum")
    dropbox_path: str = Field(..., description="Path in Dropbox")
    processed: bool = Field(default=False, description="Whether document has been processed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    tags: List[str] = Field(default_factory=list, description="Document tags")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Embedding(BaseModel):
    """Model for vector embeddings."""
    id: Optional[str] = None
    document_id: str = Field(..., description="Associated document ID")
    chunk_text: str = Field(..., description="Text chunk")
    chunk_index: int = Field(..., description="Chunk index in document")
    embedding: List[float] = Field(..., description="Vector embedding")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")
    created_at: Optional[datetime] = None


class Conversation(BaseModel):
    """Model for user conversations."""
    id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: str = Field(..., description="Session identifier")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation messages")
    context: Dict[str, Any] = Field(default_factory=dict, description="Conversation context")
    started_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Project(BaseModel):
    """Model for renewable energy projects."""
    id: Optional[str] = None
    name: str = Field(..., description="Project name")
    type: str = Field(..., description="Project type (solar, wind, etc.)")
    status: ProjectStatus = Field(..., description="Project status")
    location: Dict[str, Any] = Field(default_factory=dict, description="Project location")
    capacity: Optional[float] = Field(None, description="Project capacity in MW")
    estimated_cost: Optional[float] = Field(None, description="Estimated project cost")
    timeline: Dict[str, Any] = Field(default_factory=dict, description="Project timeline")
    documents: List[str] = Field(default_factory=list, description="Associated document IDs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional project data")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class KnowledgeEntry(BaseModel):
    """Model for structured knowledge base entries."""
    id: Optional[str] = None
    title: str = Field(..., description="Knowledge entry title")
    content: str = Field(..., description="Knowledge content")
    category: str = Field(..., description="Knowledge category")
    tags: List[str] = Field(default_factory=list, description="Knowledge tags")
    source: Optional[str] = Field(None, description="Knowledge source")
    confidence: float = Field(default=1.0, description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AgentInteraction(BaseModel):
    """Model for inter-agent communication."""
    id: Optional[str] = None
    from_agent: str = Field(..., description="Source agent ID")
    to_agent: str = Field(..., description="Target agent ID")
    message_type: str = Field(..., description="Message type")
    content: Dict[str, Any] = Field(..., description="Message content")
    response: Optional[Dict[str, Any]] = Field(None, description="Response content")
    status: str = Field(default="pending", description="Interaction status")
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None 