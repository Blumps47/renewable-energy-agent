"""Main renewable energy agent implementation."""

from typing import List, Dict, Any
import re

from .base_agent import BaseRenewableEnergyAgent, AgentContext, AgentResponse
from ..database.models import AgentType
from ..core.logging import get_logger

logger = get_logger(__name__)


class RenewableEnergyAgent(BaseRenewableEnergyAgent):
    """Main renewable energy domain expert agent."""
    
    def __init__(self):
        """Initialize the renewable energy agent."""
        super().__init__(
            name="Renewable Energy Expert",
            agent_type=AgentType.GENERAL,
            description="General renewable energy domain expert with comprehensive knowledge",
            capabilities=[
                "renewable energy fundamentals",
                "solar energy systems",
                "wind energy systems",
                "energy storage solutions",
                "grid integration",
                "project planning",
                "regulatory compliance",
                "financial analysis",
                "environmental impact assessment",
                "technology recommendations",
                "market analysis",
                "policy guidance"
            ]
        )
    
    def _get_specialized_prompt(self) -> str:
        """Get specialized prompt for renewable energy expertise."""
        return """
As a Renewable Energy Expert, you have comprehensive knowledge in:

TECHNICAL EXPERTISE:
- Solar PV systems, inverters, mounting systems, and MPPT controllers
- Wind turbines, blade aerodynamics, power curves, and wind resource assessment
- Energy storage technologies (batteries, pumped hydro, compressed air)
- Grid integration, power electronics, and smart grid technologies
- Energy efficiency and demand response systems

PROJECT DEVELOPMENT:
- Site assessment and resource evaluation
- Feasibility studies and project economics
- Permitting processes and regulatory requirements
- Construction planning and project management
- Operations and maintenance strategies

FINANCIAL ANALYSIS:
- LCOE (Levelized Cost of Energy) calculations
- NPV, IRR, and payback period analysis
- Financing structures and incentive programs
- Risk assessment and mitigation strategies
- Market pricing and power purchase agreements

REGULATORY & POLICY:
- Local, state, and federal renewable energy policies
- Net metering and interconnection standards
- Environmental regulations and impact assessments
- Utility regulations and tariff structures
- Tax incentives and subsidy programs

Always provide:
1. Technically accurate information
2. Current market data and trends
3. Practical implementation guidance
4. Cost-benefit analysis when relevant
5. Regulatory compliance considerations
6. Environmental impact information
7. Safety and risk factors
"""
    
    async def can_handle_query(self, query: str) -> float:
        """Determine if this agent can handle the query."""
        # Keywords that indicate renewable energy topics
        renewable_keywords = [
            'solar', 'wind', 'renewable', 'clean energy', 'green energy',
            'photovoltaic', 'pv', 'turbine', 'battery', 'storage',
            'grid', 'power', 'electricity', 'energy', 'sustainable',
            'carbon', 'emissions', 'climate', 'environmental',
            'inverter', 'panel', 'module', 'generator', 'kwh', 'mw',
            'lcoe', 'payback', 'roi', 'financing', 'incentive',
            'permit', 'regulation', 'policy', 'interconnection',
            'net metering', 'feed-in tariff', 'power purchase',
            'hydro', 'geothermal', 'biomass', 'biofuel'
        ]
        
        query_lower = query.lower()
        matches = sum(1 for keyword in renewable_keywords if keyword in query_lower)
        
        # Calculate confidence based on keyword matches
        if matches >= 3:
            return 0.9
        elif matches >= 2:
            return 0.7
        elif matches >= 1:
            return 0.5
        else:
            # Check for general energy-related terms
            general_energy_keywords = ['energy', 'power', 'electricity', 'utility']
            general_matches = sum(1 for keyword in general_energy_keywords if keyword in query_lower)
            return 0.3 if general_matches > 0 else 0.1
    
    async def process_query(self, context: AgentContext) -> AgentResponse:
        """Process query with renewable energy expertise."""
        # First check if we can handle this query
        confidence = await self.can_handle_query(context.user_query)
        
        if confidence < 0.3:
            return AgentResponse(
                content="I specialize in renewable energy topics. Your query seems to be outside my area of expertise. Could you please rephrase your question to focus on renewable energy aspects?",
                confidence=0.1,
                sources=[],
                metadata={
                    "agent_name": self.name,
                    "agent_type": self.agent_type.value,
                    "reason": "Query outside domain expertise"
                }
            )
        
        # Process the query with specialized context
        enhanced_context = self._enhance_context(context)
        return await super().process_query(enhanced_context)
    
    def _enhance_context(self, context: AgentContext) -> AgentContext:
        """Enhance context with renewable energy specific information."""
        # Add renewable energy specific context prompts
        enhanced_query = f"""
{context.user_query}

Please consider the following aspects in your response:
1. Technical feasibility and best practices
2. Economic considerations and cost analysis
3. Regulatory and permitting requirements
4. Environmental impact and sustainability
5. Implementation timeline and key milestones
6. Risk factors and mitigation strategies
7. Available incentives and financing options
"""
        
        # Create enhanced context
        enhanced_context = context.model_copy()
        enhanced_context.user_query = enhanced_query
        
        return enhanced_context
    
    async def analyze_project_feasibility(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze renewable energy project feasibility."""
        try:
            # Create context for feasibility analysis
            feasibility_query = f"""
Analyze the feasibility of this renewable energy project:

Project Details:
- Type: {project_data.get('type', 'Unknown')}
- Location: {project_data.get('location', 'Not specified')}
- Capacity: {project_data.get('capacity', 'Not specified')}
- Budget: {project_data.get('budget', 'Not specified')}
- Timeline: {project_data.get('timeline', 'Not specified')}

Please provide:
1. Technical feasibility assessment
2. Economic viability analysis
3. Regulatory considerations
4. Risk assessment
5. Recommendations for next steps
"""
            
            context = AgentContext(
                user_query=feasibility_query,
                session_id=f"feasibility_{project_data.get('id', 'unknown')}",
                project_context=project_data
            )
            
            response = await self.process_query(context)
            
            return {
                "feasible": response.confidence > 0.6,
                "analysis": response.content,
                "confidence": response.confidence,
                "recommendations": self._extract_recommendations(response.content),
                "risks": self._extract_risks(response.content)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze project feasibility: {e}")
            return {
                "feasible": False,
                "analysis": f"Error analyzing project: {str(e)}",
                "confidence": 0.0,
                "recommendations": [],
                "risks": ["Analysis failed due to technical error"]
            }
    
    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract recommendations from response content."""
        # Simple regex to find recommendation-like sentences
        recommendations = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if (line.startswith('-') or line.startswith('•') or 
                'recommend' in line.lower() or 'suggest' in line.lower() or
                'should' in line.lower()):
                recommendations.append(line.lstrip('-•').strip())
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _extract_risks(self, content: str) -> List[str]:
        """Extract risks from response content."""
        # Simple regex to find risk-related sentences
        risks = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if ('risk' in line.lower() or 'challenge' in line.lower() or 
                'concern' in line.lower() or 'issue' in line.lower()):
                risks.append(line.lstrip('-•').strip())
        
        return risks[:5]  # Limit to top 5 risks 