"""Base agent class for renewable energy AI agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from datetime import datetime
import uuid

from pydantic_ai import Agent as PydanticAgent, ModelRetry
from pydantic_ai.models import OpenAIModel
from pydantic import BaseModel, Field

from ..core.config import settings
from ..core.logging import get_logger
from ..database.models import Agent as AgentModel, AgentType, AgentStatus
from ..database.supabase_client import db_client

logger = get_logger(__name__)


class AgentResponse(BaseModel):
    """Standard response format for all agents."""
    content: str = Field(..., description="Response content")
    confidence: float = Field(..., description="Confidence score 0-1")
    sources: List[str] = Field(default_factory=list, description="Information sources")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class AgentContext(BaseModel):
    """Context passed between agents and RAG system."""
    user_query: str = Field(..., description="User's original query")
    session_id: str = Field(..., description="Session identifier")
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation history")
    retrieved_documents: List[Dict[str, Any]] = Field(default_factory=list, description="RAG retrieved docs")
    project_context: Optional[Dict[str, Any]] = Field(None, description="Current project context")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")


class BaseRenewableEnergyAgent(ABC):
    """Base class for all renewable energy AI agents."""
    
    def __init__(
        self,
        name: str,
        agent_type: AgentType,
        description: str,
        capabilities: List[str],
        model_name: str = None
    ):
        """Initialize the base agent."""
        self.name = name
        self.agent_type = agent_type
        self.description = description
        self.capabilities = capabilities
        self.model_name = model_name or settings.ai.openai_model
        self.agent_id = str(uuid.uuid4())
        
        # Initialize Pydantic AI agent
        self.model = OpenAIModel(
            model=self.model_name,
            api_key=settings.ai.openai_api_key
        )
        
        self.pydantic_agent = PydanticAgent(
            model=self.model,
            result_type=AgentResponse,
            system_prompt=self._get_system_prompt()
        )
        
        # Register agent in database
        self._register_agent()
        
        logger.info(f"Initialized {self.name} agent")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        base_prompt = f"""
You are {self.name}, a specialized AI agent for renewable energy development tasks.

Your expertise areas include: {', '.join(self.capabilities)}

Guidelines:
1. Provide accurate, helpful information about renewable energy topics
2. Always cite sources when making specific claims
3. Be transparent about confidence levels in your responses
4. Focus on practical, actionable advice
5. Consider environmental, economic, and technical factors
6. Stay updated with current renewable energy trends and regulations
7. Prioritize safety and regulatory compliance

Your response should be structured, informative, and tailored to the user's specific needs.
"""
        return base_prompt + self._get_specialized_prompt()
    
    @abstractmethod
    def _get_specialized_prompt(self) -> str:
        """Get the specialized system prompt for this specific agent type."""
        pass
    
    async def _register_agent(self):
        """Register this agent in the database."""
        try:
            agent_model = AgentModel(
                id=self.agent_id,
                name=self.name,
                type=self.agent_type,
                description=self.description,
                capabilities=self.capabilities,
                status=AgentStatus.ACTIVE,
                model_config={
                    "model_name": self.model_name,
                    "max_tokens": settings.ai.max_tokens,
                    "timeout": settings.ai.agent_timeout
                }
            )
            await db_client.create_agent(agent_model)
        except Exception as e:
            logger.warning(f"Failed to register agent in database: {e}")
    
    async def process_query(self, context: AgentContext) -> AgentResponse:
        """Process a user query with context."""
        try:
            # Prepare the prompt with context
            prompt = self._prepare_prompt(context)
            
            # Run the Pydantic AI agent
            result = await self.pydantic_agent.run(prompt)
            
            # Add agent-specific metadata
            result.metadata.update({
                "agent_name": self.name,
                "agent_type": self.agent_type.value,
                "model_used": self.model_name,
                "capabilities": self.capabilities
            })
            
            logger.info(f"Agent {self.name} processed query successfully")
            return result
            
        except Exception as e:
            logger.error(f"Agent {self.name} failed to process query: {e}")
            # Return error response
            return AgentResponse(
                content=f"I apologize, but I encountered an error processing your request: {str(e)}",
                confidence=0.0,
                metadata={
                    "agent_name": self.name,
                    "error": str(e),
                    "agent_type": self.agent_type.value
                }
            )
    
    def _prepare_prompt(self, context: AgentContext) -> str:
        """Prepare the prompt with context information."""
        prompt_parts = [
            f"User Query: {context.user_query}",
            ""
        ]
        
        # Add conversation history if available
        if context.conversation_history:
            prompt_parts.extend([
                "Previous Conversation:",
                *[f"- {msg.get('role', 'unknown')}: {msg.get('content', '')}" 
                  for msg in context.conversation_history[-3:]],  # Last 3 messages
                ""
            ])
        
        # Add retrieved documents from RAG
        if context.retrieved_documents:
            prompt_parts.extend([
                "Relevant Context from Documents:",
                *[f"- {doc.get('content', '')[:200]}..." 
                  for doc in context.retrieved_documents],
                ""
            ])
        
        # Add project context if available
        if context.project_context:
            prompt_parts.extend([
                "Current Project Context:",
                f"- Project: {context.project_context.get('name', 'Unknown')}",
                f"- Type: {context.project_context.get('type', 'Unknown')}",
                f"- Status: {context.project_context.get('status', 'Unknown')}",
                ""
            ])
        
        prompt_parts.append("Please provide a comprehensive and helpful response.")
        
        return "\n".join(prompt_parts)
    
    @abstractmethod
    async def can_handle_query(self, query: str) -> float:
        """
        Determine if this agent can handle the given query.
        Returns confidence score 0-1.
        """
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        return {
            "name": self.name,
            "type": self.agent_type.value,
            "status": "active",
            "capabilities": self.capabilities,
            "model": self.model_name,
            "id": self.agent_id
        } 