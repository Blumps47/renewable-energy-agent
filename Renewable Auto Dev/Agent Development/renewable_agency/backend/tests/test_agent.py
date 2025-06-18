"""
Tests for the Renewable Energy Analyst Agent
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock

from agent.renewable_agent import RenewableEnergyAgent, register_user
from agent.models import MathResponse, UserRegistration
from agent.tools import add_numbers, subtract_numbers, multiply_numbers, divide_numbers


class TestMathTools:
    """Test mathematical operation tools"""
    
    def test_add_numbers(self):
        """Test addition function"""
        result = add_numbers(10, 5)
        assert result["result"] == 15
        assert result["operation"] == "addition"
        assert "10" in result["explanation"]
        assert "5" in result["explanation"]
        assert "15" in result["explanation"]
    
    def test_subtract_numbers(self):
        """Test subtraction function"""
        result = subtract_numbers(10, 3)
        assert result["result"] == 7
        assert result["operation"] == "subtraction"
        assert "10" in result["explanation"]
        assert "3" in result["explanation"]
        assert "7" in result["explanation"]
    
    def test_multiply_numbers(self):
        """Test multiplication function"""
        result = multiply_numbers(4, 6)
        assert result["result"] == 24
        assert result["operation"] == "multiplication"
        assert "4" in result["explanation"]
        assert "6" in result["explanation"]
        assert "24" in result["explanation"]
    
    def test_divide_numbers(self):
        """Test division function"""
        result = divide_numbers(20, 4)
        assert result["result"] == 5
        assert result["operation"] == "division"
        assert "20" in result["explanation"]
        assert "4" in result["explanation"]
        assert "5" in result["explanation"]
    
    def test_divide_by_zero(self):
        """Test division by zero raises error"""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide_numbers(10, 0)


class TestUserRegistration:
    """Test user registration functionality"""
    
    def test_valid_user_registration(self):
        """Test valid user registration"""
        result = register_user("John Doe", "john@example.com")
        assert result["success"] is True
        assert "John Doe" in result["message"]
        assert "john@example.com" in result["message"]
        assert result["user_id"] is not None
        assert result["user_id"].startswith("user_")
    
    def test_user_registration_model(self):
        """Test UserRegistration Pydantic model"""
        user = UserRegistration(
            name="Jane Smith",
            email="jane@example.com",
            interests=["solar", "wind"]
        )
        assert user.name == "Jane Smith"
        assert user.email == "jane@example.com"
        assert user.interests == ["solar", "wind"]
    
    def test_invalid_user_registration(self):
        """Test invalid user registration"""
        with pytest.raises(Exception):
            UserRegistration(name="", email="invalid-email")


class TestMathResponse:
    """Test MathResponse Pydantic model"""
    
    def test_math_response_creation(self):
        """Test creating a MathResponse"""
        response = MathResponse(
            result=42.5,
            operation="multiplication",
            explanation="Multiplied 8.5 by 5 to get 42.5",
            renewable_context="This could represent 42.5 MW of solar capacity",
            units="MW",
            confidence=0.95,
            sources=["calculation", "user_input"]
        )
        
        assert response.result == 42.5
        assert response.operation == "multiplication"
        assert response.renewable_context == "This could represent 42.5 MW of solar capacity"
        assert response.units == "MW"
        assert response.confidence == 0.95
        assert response.sources == ["calculation", "user_input"]
    
    def test_math_response_defaults(self):
        """Test MathResponse with default values"""
        response = MathResponse(
            result=100.0,
            operation="addition",
            explanation="Simple addition"
        )
        
        assert response.result == 100.0
        assert response.confidence == 1.0
        assert response.sources == []
        assert response.renewable_context is None


class TestRenewableEnergyAgent:
    """Test the main agent class"""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing"""
        return RenewableEnergyAgent()
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.agent is not None
        assert agent.context is not None
        assert isinstance(agent.get_conversation_history(), list)
        assert isinstance(agent.get_user_data(), dict)
        assert isinstance(agent.get_user_preferences(), dict)
    
    @pytest.mark.asyncio
    async def test_process_message_basic(self, agent):
        """Test basic message processing"""
        # Mock the agent.run method to avoid OpenAI API calls
        with patch.object(agent.agent, 'run') as mock_run:
            mock_response = MagicMock()
            mock_response.data = MathResponse(
                result=25.0,
                operation="addition",
                explanation="Added 10 and 15 to get 25",
                confidence=1.0,
                sources=["test"]
            )
            mock_run.return_value = mock_response
            
            response = await agent.process_message("What is 10 + 15?")
            
            assert isinstance(response, MathResponse)
            assert response.result == 25.0
            assert response.operation == "addition"
            assert mock_run.called
    
    @pytest.mark.asyncio
    async def test_process_message_with_user_id(self, agent):
        """Test message processing with user ID"""
        with patch.object(agent.agent, 'run') as mock_run:
            mock_response = MagicMock()
            mock_response.data = MathResponse(
                result=50.0,
                operation="multiplication",
                explanation="Multiplied 10 by 5 to get 50",
                confidence=1.0,
                sources=["test"]
            )
            mock_run.return_value = mock_response
            
            response = await agent.process_message("What is 10 * 5?", "user_123")
            
            assert isinstance(response, MathResponse)
            assert response.result == 50.0
            
            # Check conversation history includes user_id
            history = agent.get_conversation_history()
            assert len(history) >= 1
            assert any(msg.get("user_id") == "user_123" for msg in history)
    
    @pytest.mark.asyncio
    async def test_process_message_error_handling(self, agent):
        """Test error handling in message processing"""
        with patch.object(agent.agent, 'run') as mock_run:
            mock_run.side_effect = Exception("Test error")
            
            response = await agent.process_message("This will cause an error")
            
            assert isinstance(response, MathResponse)
            assert response.operation == "error"
            assert "Test error" in response.explanation
            assert response.confidence == 0.0
    
    def test_user_preferences(self, agent):
        """Test user preference management"""
        # Set preferences
        agent.set_user_preference("theme", "dark")
        agent.set_user_preference("units", "metric")
        
        # Get preferences
        prefs = agent.get_user_preferences()
        assert prefs["theme"] == "dark"
        assert prefs["units"] == "metric"
    
    def test_conversation_history_tracking(self, agent):
        """Test conversation history tracking"""
        initial_count = len(agent.get_conversation_history())
        
        # Manually add to history to test tracking
        agent.context.conversation_history.append({
            "role": "user",
            "content": "Test message",
            "user_id": "test_user"
        })
        
        history = agent.get_conversation_history()
        assert len(history) == initial_count + 1
        assert history[-1]["content"] == "Test message"
        assert history[-1]["user_id"] == "test_user"


@pytest.mark.asyncio
async def test_integration_math_operations():
    """Integration test for mathematical operations"""
    agent = RenewableEnergyAgent()
    
    # Test cases for different operations
    test_cases = [
        ("What is 15 + 25?", "addition", 40.0),
        ("Calculate 50 - 20", "subtraction", 30.0),
        ("Multiply 6 by 8", "multiplication", 48.0),
        ("Divide 100 by 4", "division", 25.0)
    ]
    
    for message, expected_op, expected_result in test_cases:
        with patch.object(agent.agent, 'run') as mock_run:
            mock_response = MagicMock()
            mock_response.data = MathResponse(
                result=expected_result,
                operation=expected_op,
                explanation=f"Calculated {expected_result}",
                confidence=1.0,
                sources=["test"]
            )
            mock_run.return_value = mock_response
            
            response = await agent.process_message(message)
            
            assert response.result == expected_result
            assert response.operation == expected_op


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 