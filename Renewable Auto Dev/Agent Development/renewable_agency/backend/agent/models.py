"""
Pydantic models for the Renewable Energy Agent
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class MathResponse(BaseModel):
    """
    Structured response model for mathematical operations
    """
    result: float = Field(description="The calculated result")
    operation: str = Field(description="The mathematical operation performed")
    explanation: str = Field(description="Clear explanation of the calculation")
    renewable_context: str = Field(description="How this relates to renewable energy")
    units: Optional[str] = Field(default="", description="Units of measurement")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in the result")
    sources: List[str] = Field(default_factory=list, description="Data sources used")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="When the calculation was performed")

class UserRegistration(BaseModel):
    """
    User registration model
    """
    name: str = Field(min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(description="User's email address")
    interests: Optional[List[str]] = Field(default_factory=list, description="User interests")
    preferences: Optional[dict] = Field(default_factory=dict, description="User preferences")
    registration_date: Optional[datetime] = Field(default_factory=datetime.now, description="Registration timestamp")

class ChatMessage(BaseModel):
    """
    Chat message model
    """
    message: str = Field(min_length=1, description="User's message")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Message timestamp")

class ConversationHistory(BaseModel):
    """
    Conversation history model
    """
    user_id: str = Field(description="User identifier")
    messages: List[dict] = Field(default_factory=list, description="List of conversation messages")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Conversation start time")

class UserPreferences(BaseModel):
    """
    User preferences model
    """
    user_id: str = Field(description="User identifier")
    preferences: dict = Field(description="User preference settings")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="Last update time")

class AgentResponse(BaseModel):
    """
    Standard API response wrapper
    """
    success: bool = Field(description="Whether the operation was successful")
    data: Optional[dict] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if any")
    message: str = Field(description="Human-readable response message")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Response timestamp") 