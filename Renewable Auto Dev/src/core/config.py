"""Configuration management for the renewable energy AI agent ecosystem."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_key: str = Field(..., description="Supabase anon key")
    supabase_service_key: str = Field(..., description="Supabase service key")
    database_url: Optional[str] = Field(None, description="Direct database URL")
    vector_db_url: Optional[str] = Field(None, description="Vector database URL")


class AIConfig(BaseSettings):
    """AI model configuration settings."""
    
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o-mini", description="Default OpenAI model")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="Embedding model name")
    max_tokens: int = Field(default=4000, description="Maximum tokens for responses")
    agent_timeout: int = Field(default=30, description="Agent timeout in seconds")
    max_context_length: int = Field(default=8000, description="Maximum context length")


class DropboxConfig(BaseSettings):
    """Dropbox integration configuration."""
    
    dropbox_access_token: str = Field(..., description="Dropbox access token")
    dropbox_app_key: Optional[str] = Field(None, description="Dropbox app key")
    dropbox_app_secret: Optional[str] = Field(None, description="Dropbox app secret")


class RAGConfig(BaseSettings):
    """RAG system configuration."""
    
    chunk_size: int = Field(default=1000, description="Text chunk size for RAG")
    chunk_overlap: int = Field(default=200, description="Chunk overlap size")
    similarity_threshold: float = Field(default=0.7, description="Similarity threshold for retrieval")
    max_retrieved_docs: int = Field(default=5, description="Maximum documents to retrieve")


class AppConfig(BaseSettings):
    """Main application configuration."""
    
    app_name: str = Field(default="Renewable Energy AI Agents", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Security
    jwt_secret_key: str = Field(..., description="JWT secret key")
    api_key: Optional[str] = Field(None, description="API authentication key")
    
    # External services
    weather_api_key: Optional[str] = Field(None, description="Weather API key")
    nrel_api_key: Optional[str] = Field(None, description="NREL API key")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class Settings(BaseSettings):
    """Combined settings for the entire application."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.database = DatabaseConfig()
        self.ai = AIConfig()
        self.dropbox = DropboxConfig()
        self.rag = RAGConfig()
        self.app = AppConfig()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings() 