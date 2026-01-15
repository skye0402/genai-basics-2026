"""Application configuration using Pydantic Settings."""
from __future__ import annotations

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server Configuration
    port: int = 8000
    cors_origins: str = "http://localhost:5173"
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Service Mode Selection
    mock_mode: bool = True
    agentic_mode: bool = False  # Enable DeepAgent with MCP tools

    # LiteLLM Proxy (OpenAI-compatible)
    litellm_proxy_url: str = Field(default="", validation_alias=AliasChoices("LITELLM_PROXY_URL"))
    litellm_api_key: str = Field(default="", validation_alias=AliasChoices("LITELLM_API_KEY"))
    
    # LLM Models
    llm_model: str = "gpt-4.1"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000
    
    summarization_llm_model: str = "gpt-5-mini"  # Faster/cheaper model for title generation
    summarization_temperature: float = 0.3
    summarization_max_tokens: int = 50
    
    # Audio Transcription
    audio_model_name: str = Field(default="", validation_alias=AliasChoices("AUDIO_MODEL_NAME"))

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
