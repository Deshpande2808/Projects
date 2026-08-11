"""
Configuration management for the Agentic Email Workflow Engine.

Uses pydantic-settings to load and validate environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    # llm_model is the LiteLLM model string every agent uses by default
    # (overridable per-call). Swap per environment: cheap model for dev,
    # stronger model for prod. Each provider needs its own API key below;
    # LiteLLM reads them from the environment directly by convention
    # (ANTHROPIC_API_KEY, OPENAI_API_KEY, DEEPSEEK_API_KEY, MOONSHOT_API_KEY),
    # so they don't need dedicated Settings fields to be usable.
    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-5"
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    moonshot_api_key: Optional[str] = None

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

# LiteLLM reads provider API keys straight from os.environ (it doesn't know
# about our Settings object) — propagate any keys pydantic-settings loaded
# from .env so litellm.acompletion() can find them by its own convention.
_PROVIDER_ENV_KEYS = {
    "anthropic_api_key": "ANTHROPIC_API_KEY",
    "openai_api_key": "OPENAI_API_KEY",
    "deepseek_api_key": "DEEPSEEK_API_KEY",
    "moonshot_api_key": "MOONSHOT_API_KEY",
}
for _field, _env_var in _PROVIDER_ENV_KEYS.items():
    _value = getattr(settings, _field)
    if _value and not _value.startswith("your_"):
        os.environ[_env_var] = _value
