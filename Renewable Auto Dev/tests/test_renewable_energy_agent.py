"""Tests for the renewable energy agent."""

import pytest
import asyncio
from unittest.mock import Mock, patch
from src.agents.renewable_energy_agent import RenewableEnergyAgent
from src.agents.base_agent import AgentContext


class TestRenewableEnergyAgent:
    """Test cases for the renewable energy agent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent instance."""
        with patch('src.database.supabase_client.db_client'):
            return RenewableEnergyAgent()
    
    @pytest.mark.asyncio
    async def test_can_handle_renewable_queries(self, agent):
        """Test that agent can identify renewable energy queries."""
        # High confidence queries
        high_confidence_queries = [
            "What are the benefits of solar panels?",
            "How do wind turbines work?",
            "What is the LCOE for renewable energy projects?",
            "Solar panel installation requirements"
        ]
        
        for query in high_confidence_queries:
            confidence = await agent.can_handle_query(query)
            assert confidence >= 0.5, f"Query '{query}' should have high confidence"
    
    @pytest.mark.asyncio
    async def test_cannot_handle_unrelated_queries(self, agent):
        """Test that agent correctly identifies unrelated queries."""
        # Low confidence queries
        low_confidence_queries = [
            "What's the weather like today?",
            "How do I bake a cake?",
            "What is machine learning?",
            "Tell me about ancient history"
        ]
        
        for query in low_confidence_queries:
            confidence = await agent.can_handle_query(query)
            assert confidence <= 0.3, f"Query '{query}' should have low confidence"
    
    @pytest.mark.asyncio
    async def test_process_query_structure(self, agent):
        """Test that processed queries return proper structure."""
        context = AgentContext(
            user_query="What are the key considerations for solar panel installation?",
            session_id="test_session"
        )
        
        with patch.object(agent.pydantic_agent, 'run') as mock_run:
            # Mock the Pydantic AI response
            mock_response = Mock()
            mock_response.content = "Solar panel installation requires proper site assessment..."
            mock_response.confidence = 0.85
            mock_response.sources = []
            mock_response.metadata = {}
            mock_run.return_value = mock_response
            
            response = await agent.process_query(context)
            
            assert hasattr(response, 'content')
            assert hasattr(response, 'confidence')
            assert hasattr(response, 'metadata')
            assert response.metadata['agent_name'] == agent.name
    
    @pytest.mark.asyncio
    async def test_project_feasibility_analysis(self, agent):
        """Test project feasibility analysis functionality."""
        project_data = {
            "id": "test_project",
            "type": "solar",
            "location": "California, USA",
            "capacity": "100MW",
            "budget": "$100M",
            "timeline": "18 months"
        }
        
        with patch.object(agent, 'process_query') as mock_process:
            # Mock the process_query response
            mock_response = Mock()
            mock_response.content = "This solar project shows good feasibility..."
            mock_response.confidence = 0.8
            mock_process.return_value = mock_response
            
            result = await agent.analyze_project_feasibility(project_data)
            
            assert isinstance(result, dict)
            assert 'feasible' in result
            assert 'analysis' in result
            assert 'confidence' in result
            assert 'recommendations' in result
            assert 'risks' in result
    
    def test_extract_recommendations(self, agent):
        """Test recommendation extraction from response content."""
        content = """
        Based on the analysis, I recommend the following:
        - Consider using high-efficiency solar panels
        - Evaluate the local grid connection requirements
        - You should obtain proper permits before construction
        • Implement a robust monitoring system
        """
        
        recommendations = agent._extract_recommendations(content)
        
        assert len(recommendations) > 0
        assert any("high-efficiency solar panels" in rec for rec in recommendations)
        assert any("permits" in rec for rec in recommendations)
    
    def test_extract_risks(self, agent):
        """Test risk extraction from response content."""
        content = """
        Several risks need to be considered:
        - Weather risk may impact construction timeline
        - Regulatory changes could affect project viability
        - Grid interconnection challenges might arise
        There are concerns about material costs increasing
        """
        
        risks = agent._extract_risks(content)
        
        assert len(risks) > 0
        assert any("weather risk" in risk.lower() for risk in risks)
        assert any("regulatory" in risk.lower() for risk in risks)


if __name__ == "__main__":
    pytest.main([__file__]) 