"""
Tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app
from agent.models import MathResponse


# Create test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert data["version"] == "1.0.0"
        assert "Renewable Energy Analyst Agent API" in data["message"]
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "renewable-energy-agent"
        assert "timestamp" in data


class TestChatEndpoint:
    """Test chat endpoint functionality"""
    
    @patch('main.renewable_agent.process_message')
    def test_chat_success(self, mock_process):
        """Test successful chat interaction"""
        # Mock the agent response
        mock_response = MathResponse(
            result=25.0,
            operation="addition",
            explanation="Added 15 and 10 to get 25",
            renewable_context="This could represent 25 MW of combined solar capacity",
            confidence=1.0,
            sources=["calculation"]
        )
        mock_process.return_value = mock_response
        
        # Test data
        test_message = {
            "message": "What is 15 + 10?",
            "user_id": "test_user"
        }
        
        response = client.post("/api/chat", json=test_message)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["error"] is None
        assert "data" in data
        
        # Check the nested response data
        response_data = data["data"]
        assert response_data["result"] == 25.0
        assert response_data["operation"] == "addition"
        assert "25 MW" in response_data["renewable_context"]
    
    def test_chat_invalid_message(self):
        """Test chat with invalid message format"""
        response = client.post("/api/chat", json={})
        assert response.status_code == 422  # Validation error
    
    def test_chat_missing_message(self):
        """Test chat with missing message field"""
        response = client.post("/api/chat", json={"user_id": "test"})
        assert response.status_code == 422
    
    @patch('main.renewable_agent.process_message')
    def test_chat_with_optional_fields(self, mock_process):
        """Test chat with optional fields"""
        mock_response = MathResponse(
            result=100.0,
            operation="multiplication",
            explanation="Multiplied 10 by 10 to get 100",
            confidence=1.0,
            sources=["calculation"]
        )
        mock_process.return_value = mock_response
        
        test_message = {
            "message": "What is 10 * 10?",
            "user_id": "user_456",
            "context": {"location": "California"}
        }
        
        response = client.post("/api/chat", json=test_message)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["result"] == 100.0


class TestUserRegistration:
    """Test user registration endpoint"""
    
    def test_register_user_success(self):
        """Test successful user registration"""
        user_data = {
            "name": "John Doe", 
            "email": "john.doe@example.com",
            "interests": ["solar", "wind"]
        }
        
        response = client.post("/api/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["error"] is None
        
        user_info = data["data"]
        assert user_info["name"] == "John Doe"
        assert user_info["email"] == "john.doe@example.com"
        assert user_info["interests"] == ["solar", "wind"]
        assert user_info["user_id"].startswith("user_")
        assert "registered_at" in user_info
    
    def test_register_user_minimal(self):
        """Test user registration with minimal data"""
        user_data = {
            "name": "Jane Smith",
            "email": "jane@example.com"
        }
        
        response = client.post("/api/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["interests"] == []  # Default empty list
    
    def test_register_user_invalid_name(self):
        """Test registration with invalid name"""
        user_data = {
            "name": "",  # Too short
            "email": "test@example.com"
        }
        
        response = client.post("/api/register", json=user_data)
        assert response.status_code == 422  # Validation error
    
    def test_register_user_invalid_email(self):
        """Test registration with invalid email"""
        user_data = {
            "name": "Test User",
            "email": "invalid-email"  # Invalid format
        }
        
        response = client.post("/api/register", json=user_data)
        assert response.status_code == 422  # Validation error
    
    def test_register_user_missing_fields(self):
        """Test registration with missing required fields"""
        response = client.post("/api/register", json={"name": "Test"})
        assert response.status_code == 422


class TestConversationHistory:
    """Test conversation history endpoints"""
    
    @patch('main.renewable_agent.get_conversation_history')
    @patch('main.renewable_agent.get_user_data')
    def test_get_conversation_history(self, mock_user_data, mock_history):
        """Test retrieving conversation history"""
        # Mock data
        mock_history.return_value = [
            {"role": "user", "content": "Hello", "user_id": "user_123"},
            {"role": "assistant", "content": {"result": 5.0, "operation": "test"}}
        ]
        mock_user_data.return_value = {"name": "Test User", "email": "test@example.com"}
        
        response = client.get("/api/conversation/user_123")
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == "user_123"
        assert "conversation_history" in data
        assert "user_data" in data
        assert data["total_messages"] >= 0
    
    def test_get_conversation_nonexistent_user(self):
        """Test getting conversation for non-existent user"""
        response = client.get("/api/conversation/nonexistent_user")
        assert response.status_code == 200  # Should return empty history


class TestUserPreferences:
    """Test user preference endpoints"""
    
    def test_set_user_preference(self):
        """Test setting user preference"""
        response = client.post(
            "/api/user/preferences", 
            params={"user_id": "user_123", "key": "theme", "value": "dark"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["user_id"] == "user_123"
        assert data["preference"]["theme"] == "dark"
    
    @patch('main.renewable_agent.get_user_preferences')
    def test_get_user_preferences(self, mock_prefs):
        """Test getting user preferences"""
        mock_prefs.return_value = {
            "user_123_theme": "dark",
            "user_123_units": "metric",
            "user_456_theme": "light"  # Different user
        }
        
        response = client.get("/api/user/preferences/user_123")
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == "user_123"
        assert data["preferences"]["theme"] == "dark"
        assert data["preferences"]["units"] == "metric"
        assert "user_456_theme" not in str(data)  # Shouldn't include other users


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_404_not_found(self):
        """Test 404 error handling"""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code == 404
        
        data = response.json()
        assert data["error"] == "Not Found"
        assert "nonexistent/endpoint" in data["path"]
    
    @patch('main.renewable_agent.process_message')
    def test_chat_internal_error(self, mock_process):
        """Test internal server error handling in chat"""
        # Mock an exception
        mock_process.side_effect = Exception("Database connection failed")
        
        response = client.post("/api/chat", json={"message": "test"})
        assert response.status_code == 500
    
    def test_invalid_json(self):
        """Test invalid JSON handling"""
        response = client.post(
            "/api/chat", 
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


class TestCurlCommands:
    """Test cases that simulate curl commands from PRD"""
    
    def test_prd_health_curl(self):
        """Test: curl -X GET "http://localhost:8000/api/health" """
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @patch('main.renewable_agent.process_message')
    def test_prd_chat_curl(self, mock_process):
        """Test: curl -X POST "http://localhost:8000/api/chat" -H "Content-Type: application/json" -d '{"message": "What is 15 + 25?"}'"""
        mock_response = MathResponse(
            result=40.0,
            operation="addition",
            explanation="Added 15 and 25 to get 40",
            confidence=1.0,
            sources=["calculation"]
        )
        mock_process.return_value = mock_response
        
        response = client.post(
            "/api/chat",
            json={"message": "What is 15 + 25?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["result"] == 40.0
    
    def test_prd_register_curl(self):
        """Test: curl -X POST "http://localhost:8000/api/register" -H "Content-Type: application/json" -d '{"name": "John Doe", "email": "john@example.com"}'"""
        response = client.post(
            "/api/register",
            json={"name": "John Doe", "email": "john@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "John Doe"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 