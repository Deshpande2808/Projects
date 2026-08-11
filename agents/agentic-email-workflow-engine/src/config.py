"""
Configuration management for the Agentic Email Workflow Engine.

Uses pydantic-settings to load and validate environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    llm_provider: str = "anthropic"
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@localhost:5432/agentic_email_engine"
    database_echo: bool = False

    # Vector Store Configuration
    vector_store_type: str = "pgvector"
    embedding_model: str = "openai"
    embedding_dimension: int = 1536

    # Email Ingestion (IMAP)
    imap_host: str = "mock"
    imap_port: int = 993
    imap_email: str = "test@example.com"
    imap_password: str = "mock_password"
    imap_poll_interval_seconds: int = 300

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Environment
    env: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
