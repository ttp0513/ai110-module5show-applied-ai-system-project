"""Validated application configuration."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables or a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="VYBE_",
        extra="ignore",
    )

    app_name: str = "VYBE"
    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    demo_mode: bool = True
    ai_provider: str = "demo"
    ai_model: str = ""
    ai_api_key: str = ""
    retrieval_candidate_count: int = Field(default=15, ge=5, le=100)
    recommendation_count: int = Field(default=5, ge=1, le=20)
    request_timeout_seconds: int = Field(default=30, ge=1, le=120)
    max_prompt_length: int = Field(default=1000, ge=1, le=5000)
    private_database_path: Path = Path("data/vybe.db")
    session_cookie_max_age_days: int = Field(default=3650, ge=1, le=3650)


@lru_cache
def get_settings() -> Settings:
    """Return one validated settings instance per process."""

    return Settings()
