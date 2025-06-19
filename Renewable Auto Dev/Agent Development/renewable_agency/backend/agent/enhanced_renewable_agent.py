"""
Enhanced Renewable Energy Agent with RAG Integration

Extends the base renewable energy agent with document context capabilities,
providing more informed responses based on user's project documents.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from ..services.rag_engine import RAGQueryEngine
from ..services.project_service import ProjectService

logger = logging.getLogger(__name__)

class EnhancedAgentDependencies(BaseModel):
    """Dependencies for the enhanced renewable energy agent."""
    rag_engine: RAGQueryEngine
    project_service: ProjectService
    user_id: str

class EnhancedQueryContext(BaseModel):
    """Context for enhanced queries with RAG integration."""
    query: str
    user_id: str
    project_ids: Optional[List[str]] = None
    use_rag: bool = True
    rag_limit: int = 5
    similarity_threshold: float = 0.7

class AgentResponse(BaseModel):
    """Enhanced agent response with source attribution."""
    response: str = Field(description="The agent's response to the user query")
    sources_used: List[Dict[str, Any]] = Field(default_factory=list, description="Sources used in the response")
    context_relevance: float = Field(default=0.0, description="Relevance score of the context used")
    response_type: str = Field(default="general", description="Type of response: general, document_based, project_specific")
    confidence_score: float = Field(default=0.8, description="Confidence in the response")
    suggestions: List[str] = Field(default_factory=list, description="Additional suggestions or follow-up questions")

class EnhancedRenewableAgent:
    """Enhanced renewable energy agent with RAG capabilities."""
    
    def __init__(
        self,
        openai_api_key: str,
        rag_engine: RAGQueryEngine,
        project_service: ProjectService,
        model_name: str = "gpt-4o-mini"
    ):
        """Initialize the enhanced renewable energy agent."""
        self.rag_engine = rag_engine
        self.project_service = project_service
        
        # Initialize the PydanticAI agent
        self.agent = Agent(
            model=OpenAIModel(model_name, api_key=openai_api_key),
            result_type=AgentResponse,
            system_prompt=self._get_enhanced_system_prompt(),
            deps_type=EnhancedAgentDependencies
        )
        
        # Register tools
        self._register_tools()
    
    def _get_enhanced_system_prompt(self) -> str:
        """Get the enhanced system prompt with RAG capabilities."""
        return """
You are an expert renewable energy consultant AI with access to the user's project documents and data. 
Your expertise covers all aspects of renewable energy development including:

CORE EXPERTISE:
- Solar PV and thermal systems design and analysis
- Wind energy (onshore and offshore) development
- Hydroelectric power systems and feasibility
- Battery energy storage systems (BESS) integration
- Grid interconnection and power purchase agreements (PPAs)
- Environmental impact assessments and permitting
- Financial modeling, LCOE analysis, and project economics
- Regulatory compliance and policy analysis
- Due diligence and risk assessment
- Construction and operations management

ENHANCED CAPABILITIES:
You have access to the user's project documents through a RAG (Retrieval Augmented Generation) system.
When responding to queries, you can:

1. **Access Project Documents**: Retrieve relevant information from uploaded documents including:
   - Feasibility studies and technical reports
   - Environmental assessments and permits
   - Financial models and economic analyses
   - Engineering drawings and specifications
   - Regulatory filings and correspondence
   - Due diligence reports and site assessments

2. **Provide Contextual Responses**: Use document context to give specific, detailed answers based on actual project data rather than general information.

3. **Source Attribution**: Always cite specific documents and sections when using information from the user's files.

4. **Cross-Project Analysis**: Compare and analyze information across multiple projects when relevant.

RESPONSE GUIDELINES:
- Always prioritize information from the user's documents when available
- Clearly distinguish between document-based information and general knowledge
- Provide specific citations with document names and relevance scores
- Offer follow-up questions based on available document context
- Suggest additional analysis or documentation when gaps are identified
- Maintain professional, technical accuracy while being accessible

DOCUMENT CONTEXT INTEGRATION:
When document context is provided, structure your response as:
1. Direct answer using document information (with citations)
2. Additional insights from general renewable energy expertise
3. Specific recommendations based on the project context
4. Suggested follow-up questions or analysis

Always be thorough, accurate, and helpful while leveraging both your expertise and the user's specific project documentation.
"""
    
    def _register_tools(self):
        """Register tools for the enhanced agent."""
        
        @self.agent.tool
        async def search_project_documents(
            ctx: RunContext[EnhancedAgentDependencies],
            query: str,
            project_ids: Optional[List[str]] = None,
            limit: int = 5
        ) -> Dict[str, Any]:
            """
            Search through the user's project documents for relevant information.
            
            Args:
                query: Search query for finding relevant documents
                project_ids: Optional list of specific project IDs to search within
                limit: Maximum number of results to return
                
            Returns:
                Search results with document context and sources
            """
            try:
                results = await ctx.deps.rag_engine.query_documents(
                    user_id=ctx.deps.user_id,
                    query=query,
                    project_ids=project_ids,
                    limit=limit
                )
                
                return {
                    "success": True,
                    "context": results["context"],
                    "sources": results["sources"],
                    "results_count": results["results_count"]
                }
                
            except Exception as e:
                logger.error(f"Error searching documents: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "context": "",
                    "sources": [],
                    "results_count": 0
                }
        
        @self.agent.tool
        async def get_project_overview(
            ctx: RunContext[EnhancedAgentDependencies],
            project_id: str
        ) -> Dict[str, Any]:
            """
            Get a comprehensive overview of a specific project.
            
            Args:
                project_id: UUID of the project to analyze
                
            Returns:
                Project overview with statistics and document summary
            """
            try:
                project_data = await ctx.deps.project_service.get_project(
                    ctx.deps.user_id, project_id
                )
                
                # Get project summary using RAG
                summary_results = await ctx.deps.rag_engine.get_project_summary(
                    user_id=ctx.deps.user_id,
                    project_id=project_id
                )
                
                return {
                    "success": True,
                    "project": project_data,
                    "document_summary": summary_results
                }
                
            except Exception as e:
                logger.error(f"Error getting project overview: {str(e)}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.agent.tool
        async def compare_projects(
            ctx: RunContext[EnhancedAgentDependencies],
            project_ids: List[str],
            comparison_aspects: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """
            Compare multiple projects across various aspects.
            
            Args:
                project_ids: List of project UUIDs to compare
                comparison_aspects: Specific aspects to focus on (optional)
                
            Returns:
                Detailed project comparison analysis
            """
            try:
                comparison_data = await ctx.deps.project_service.compare_projects(
                    ctx.deps.user_id, project_ids
                )
                
                return {
                    "success": True,
                    "comparison": comparison_data
                }
                
            except Exception as e:
                logger.error(f"Error comparing projects: {str(e)}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.agent.tool
        async def search_across_markets(
            ctx: RunContext[EnhancedAgentDependencies],
            query: str,
            market_type: Optional[str] = None,
            location: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Search across all projects with optional market and location filters.
            
            Args:
                query: Search query
                market_type: Optional renewable energy market filter
                location: Optional location filter
                
            Returns:
                Cross-project search results
            """
            try:
                results = await ctx.deps.rag_engine.search_across_projects(
                    user_id=ctx.deps.user_id,
                    query=query,
                    market_filter=market_type,
                    location_filter=location,
                    limit=10
                )
                
                return {
                    "success": True,
                    "results": results
                }
                
            except Exception as e:
                logger.error(f"Error searching across markets: {str(e)}")
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def query_with_context(
        self,
        user_id: str,
        query: str,
        project_ids: Optional[List[str]] = None,
        use_rag: bool = True,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AgentResponse:
        """
        Process a query with enhanced context from RAG system.
        
        Args:
            user_id: User UUID
            query: User's question or request
            project_ids: Optional specific projects to focus on
            use_rag: Whether to use RAG for context
            conversation_history: Previous conversation messages
            
        Returns:
            Enhanced agent response with source attribution
        """
        try:
            # Create dependencies
            deps = EnhancedAgentDependencies(
                rag_engine=self.rag_engine,
                project_service=self.project_service,
                user_id=user_id
            )
            
            # Prepare the enhanced query with context
            enhanced_query = query
            
            if use_rag:
                # Get relevant document context
                rag_results = await self.rag_engine.query_documents(
                    user_id=user_id,
                    query=query,
                    project_ids=project_ids,
                    limit=5
                )
                
                if rag_results["results_count"] > 0:
                    # Enhance the query with document context
                    enhanced_query = f"""
USER QUERY: {query}

RELEVANT DOCUMENT CONTEXT:
{rag_results['context']}

Please provide a comprehensive response using the document context above. 
Include specific citations and source attributions in your response.
If the context doesn't fully address the query, supplement with your general expertise.
"""
            
            # Add conversation history if provided
            if conversation_history:
                history_text = "\n".join([
                    f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                    for msg in conversation_history[-5:]  # Last 5 messages
                ])
                enhanced_query = f"CONVERSATION HISTORY:\n{history_text}\n\n{enhanced_query}"
            
            # Run the agent
            result = await self.agent.run(enhanced_query, deps=deps)
            
            # Extract and enhance the response
            agent_response = result.data
            
            # Add RAG-specific enhancements if context was used
            if use_rag and rag_results["results_count"] > 0:
                agent_response.sources_used = rag_results["sources"]
                agent_response.response_type = "document_based"
                agent_response.context_relevance = self._calculate_context_relevance(
                    rag_results["sources"]
                )
                
                # Add suggestions based on available documents
                agent_response.suggestions.extend(
                    self._generate_follow_up_suggestions(rag_results["sources"])
                )
            
            # Log the interaction
            await self._log_interaction(user_id, query, agent_response, rag_results if use_rag else None)
            
            return agent_response
            
        except Exception as e:
            logger.error(f"Error processing enhanced query: {str(e)}")
            
            # Return a fallback response
            return AgentResponse(
                response=f"I apologize, but I encountered an error while processing your query: {str(e)}. Please try rephrasing your question or contact support if the issue persists.",
                response_type="error",
                confidence_score=0.0
            )
    
    def _calculate_context_relevance(self, sources: List[Dict[str, Any]]) -> float:
        """Calculate overall context relevance from sources."""
        if not sources:
            return 0.0
        
        # Average similarity scores from sources
        similarity_scores = [source.get("similarity_score", 0.0) for source in sources]
        return sum(similarity_scores) / len(similarity_scores)
    
    def _generate_follow_up_suggestions(self, sources: List[Dict[str, Any]]) -> List[str]:
        """Generate follow-up suggestions based on available sources."""
        suggestions = []
        
        # Get unique project markets and types
        markets = set()
        project_names = set()
        
        for source in sources:
            if source.get("project_market"):
                markets.add(source["project_market"])
            if source.get("project_name"):
                project_names.add(source["project_name"])
        
        # Generate market-specific suggestions
        for market in list(markets)[:2]:  # Limit to 2 markets
            suggestions.append(f"Tell me more about {market} energy considerations in this project")
        
        # Generate project-specific suggestions
        for project in list(project_names)[:2]:  # Limit to 2 projects
            suggestions.append(f"What are the key risks and opportunities for {project}?")
        
        # Add general follow-up suggestions
        suggestions.extend([
            "Can you provide a financial analysis based on the available documents?",
            "What are the main regulatory requirements for this project?",
            "Are there any environmental concerns mentioned in the documentation?"
        ])
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    async def _log_interaction(
        self,
        user_id: str,
        query: str,
        response: AgentResponse,
        rag_results: Optional[Dict[str, Any]] = None
    ):
        """Log the interaction for analytics and improvement."""
        try:
            # This could be expanded to store in a dedicated analytics table
            logger.info(f"Enhanced agent interaction - User: {user_id}, "
                       f"Query length: {len(query)}, "
                       f"Response type: {response.response_type}, "
                       f"Sources used: {len(response.sources_used)}, "
                       f"Context relevance: {response.context_relevance}")
            
        except Exception as e:
            logger.warning(f"Failed to log interaction: {str(e)}")
    
    async def get_project_insights(
        self,
        user_id: str,
        project_id: str,
        insight_type: str = "general"
    ) -> AgentResponse:
        """
        Get AI-generated insights about a specific project.
        
        Args:
            user_id: User UUID
            project_id: Project UUID
            insight_type: Type of insights to generate
            
        Returns:
            AI-generated project insights
        """
        try:
            # Define insight queries based on type
            insight_queries = {
                "general": "Provide a comprehensive analysis of this renewable energy project including key opportunities, risks, and recommendations",
                "financial": "Analyze the financial aspects, economics, and investment potential of this project",
                "technical": "Evaluate the technical feasibility, design considerations, and engineering aspects",
                "regulatory": "Assess regulatory compliance, permitting requirements, and policy implications",
                "environmental": "Analyze environmental impacts, mitigation measures, and sustainability aspects",
                "risk": "Identify and analyze key risks, challenges, and mitigation strategies"
            }
            
            query = insight_queries.get(insight_type, insight_queries["general"])
            
            # Get project-specific insights
            response = await self.query_with_context(
                user_id=user_id,
                query=query,
                project_ids=[project_id],
                use_rag=True
            )
            
            response.response_type = f"project_insights_{insight_type}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating project insights: {str(e)}")
            return AgentResponse(
                response=f"Unable to generate project insights: {str(e)}",
                response_type="error"
            )
    
    async def generate_project_summary(
        self,
        user_id: str,
        project_id: str,
        summary_type: str = "executive"
    ) -> AgentResponse:
        """
        Generate different types of project summaries.
        
        Args:
            user_id: User UUID
            project_id: Project UUID
            summary_type: Type of summary (executive, technical, financial)
            
        Returns:
            Generated project summary
        """
        try:
            summary_prompts = {
                "executive": "Create an executive summary of this renewable energy project suitable for stakeholders and decision-makers",
                "technical": "Provide a technical summary focusing on engineering aspects, specifications, and implementation details",
                "financial": "Generate a financial summary including economic analysis, costs, revenues, and investment metrics",
                "environmental": "Create an environmental summary covering impacts, assessments, and sustainability measures"
            }
            
            prompt = summary_prompts.get(summary_type, summary_prompts["executive"])
            
            response = await self.query_with_context(
                user_id=user_id,
                query=prompt,
                project_ids=[project_id],
                use_rag=True
            )
            
            response.response_type = f"project_summary_{summary_type}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating project summary: {str(e)}")
            return AgentResponse(
                response=f"Unable to generate project summary: {str(e)}",
                response_type="error"
            ) 