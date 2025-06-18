"""Supabase client for database operations."""

from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from ..core.config import settings
from ..core.logging import get_logger
from .models import *

logger = get_logger(__name__)


class SupabaseClient:
    """Supabase client wrapper for database operations."""
    
    def __init__(self):
        """Initialize the Supabase client."""
        self.client: Client = create_client(
            settings.database.supabase_url,
            settings.database.supabase_key
        )
        logger.info("Supabase client initialized")
    
    # Agent operations
    async def create_agent(self, agent: Agent) -> Agent:
        """Create a new agent."""
        try:
            data = agent.model_dump(exclude_none=True)
            result = self.client.table("agents").insert(data).execute()
            logger.info(f"Created agent: {agent.name}")
            return Agent(**result.data[0])
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            raise
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        try:
            result = self.client.table("agents").select("*").eq("id", agent_id).execute()
            if result.data:
                return Agent(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get agent {agent_id}: {e}")
            raise
    
    async def list_agents(self, agent_type: Optional[AgentType] = None) -> List[Agent]:
        """List all agents, optionally filtered by type."""
        try:
            query = self.client.table("agents").select("*")
            if agent_type:
                query = query.eq("type", agent_type.value)
            result = query.execute()
            return [Agent(**agent) for agent in result.data]
        except Exception as e:
            logger.error(f"Failed to list agents: {e}")
            raise
    
    async def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Agent:
        """Update an agent."""
        try:
            result = self.client.table("agents").update(updates).eq("id", agent_id).execute()
            logger.info(f"Updated agent: {agent_id}")
            return Agent(**result.data[0])
        except Exception as e:
            logger.error(f"Failed to update agent {agent_id}: {e}")
            raise
    
    # Document operations
    async def create_document(self, document: Document) -> Document:
        """Create a new document."""
        try:
            data = document.model_dump(exclude_none=True)
            result = self.client.table("documents").insert(data).execute()
            logger.info(f"Created document: {document.filename}")
            return Document(**result.data[0])
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        try:
            result = self.client.table("documents").select("*").eq("id", document_id).execute()
            if result.data:
                return Document(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get document {document_id}: {e}")
            raise
    
    async def list_documents(self, processed_only: bool = False) -> List[Document]:
        """List all documents."""
        try:
            query = self.client.table("documents").select("*")
            if processed_only:
                query = query.eq("processed", True)
            result = query.execute()
            return [Document(**doc) for doc in result.data]
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            raise
    
    async def mark_document_processed(self, document_id: str) -> None:
        """Mark a document as processed."""
        try:
            self.client.table("documents").update({"processed": True}).eq("id", document_id).execute()
            logger.info(f"Marked document as processed: {document_id}")
        except Exception as e:
            logger.error(f"Failed to mark document as processed {document_id}: {e}")
            raise
    
    # Embedding operations
    async def create_embedding(self, embedding: Embedding) -> Embedding:
        """Create a new embedding."""
        try:
            data = embedding.model_dump(exclude_none=True)
            result = self.client.table("embeddings").insert(data).execute()
            return Embedding(**result.data[0])
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            raise
    
    async def search_similar_embeddings(
        self, 
        query_embedding: List[float], 
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Embedding]:
        """Search for similar embeddings using vector similarity."""
        try:
            # Note: This requires pgvector extension and proper RPC function
            result = self.client.rpc(
                "match_embeddings",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": similarity_threshold,
                    "match_count": limit
                }
            ).execute()
            return [Embedding(**emb) for emb in result.data]
        except Exception as e:
            logger.error(f"Failed to search similar embeddings: {e}")
            raise
    
    # Conversation operations
    async def create_conversation(self, conversation: Conversation) -> Conversation:
        """Create a new conversation."""
        try:
            data = conversation.model_dump(exclude_none=True)
            result = self.client.table("conversations").insert(data).execute()
            logger.info(f"Created conversation: {conversation.session_id}")
            return Conversation(**result.data[0])
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            raise
    
    async def get_conversation(self, session_id: str) -> Optional[Conversation]:
        """Get a conversation by session ID."""
        try:
            result = self.client.table("conversations").select("*").eq("session_id", session_id).execute()
            if result.data:
                return Conversation(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get conversation {session_id}: {e}")
            raise
    
    async def update_conversation(self, session_id: str, updates: Dict[str, Any]) -> Conversation:
        """Update a conversation."""
        try:
            result = self.client.table("conversations").update(updates).eq("session_id", session_id).execute()
            return Conversation(**result.data[0])
        except Exception as e:
            logger.error(f"Failed to update conversation {session_id}: {e}")
            raise
    
    # Project operations
    async def create_project(self, project: Project) -> Project:
        """Create a new project."""
        try:
            data = project.model_dump(exclude_none=True)
            result = self.client.table("projects").insert(data).execute()
            logger.info(f"Created project: {project.name}")
            return Project(**result.data[0])
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise
    
    async def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        try:
            result = self.client.table("projects").select("*").eq("id", project_id).execute()
            if result.data:
                return Project(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {e}")
            raise
    
    async def list_projects(self, status: Optional[ProjectStatus] = None) -> List[Project]:
        """List all projects, optionally filtered by status."""
        try:
            query = self.client.table("projects").select("*")
            if status:
                query = query.eq("status", status.value)
            result = query.execute()
            return [Project(**project) for project in result.data]
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            raise
    
    # Knowledge base operations
    async def create_knowledge_entry(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        """Create a new knowledge entry."""
        try:
            data = entry.model_dump(exclude_none=True)
            result = self.client.table("knowledge_base").insert(data).execute()
            logger.info(f"Created knowledge entry: {entry.title}")
            return KnowledgeEntry(**result.data[0])
        except Exception as e:
            logger.error(f"Failed to create knowledge entry: {e}")
            raise
    
    async def search_knowledge(self, query: str, category: Optional[str] = None) -> List[KnowledgeEntry]:
        """Search knowledge base entries."""
        try:
            search_query = self.client.table("knowledge_base").select("*")
            if category:
                search_query = search_query.eq("category", category)
            # Full-text search on title and content
            search_query = search_query.text_search("title,content", query)
            result = search_query.execute()
            return [KnowledgeEntry(**entry) for entry in result.data]
        except Exception as e:
            logger.error(f"Failed to search knowledge base: {e}")
            raise


# Global client instance
db_client = SupabaseClient() 