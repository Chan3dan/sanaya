"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated Sanaya runtime settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    sanaya_env: str = "development"
    sanaya_log_level: str = "INFO"
    sanaya_dashboard_port: int = 3000
    sanaya_api_port: int = 3001
    sanaya_core_port: int = 8000

    database_url: str = "sqlite+aiosqlite:///./data/sqlite/sanaya.db"
    redis_url: str = "redis://localhost:6379"
    chroma_path: Path = Path("./data/chroma")

    ollama_base_url: str = "http://localhost:11434"
    default_ai_provider: Literal["ollama", "openai", "gemini", "claude"] = "ollama"
    privacy_mode: bool = False
    embedding_model: str = "nomic-embed-text"
    ollama_chat_model: str = "mistral:7b-q4"

    whisper_model: str = "base"
    tts_provider: str = "coqui"
    wake_word_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    wake_word_model: Path = Path("./data/models/wake_word/hey_sanaya.onnx")

    jwt_secret: str = "change-this-to-a-random-64-char-string"
    jwt_expiry: str = "24h"
    memory_encryption: bool = True

    @field_validator("database_url")
    @classmethod
    def normalize_sqlite_async_url(cls, value: str) -> str:
        """Ensure SQLite URLs work with SQLAlchemy async engines."""
        if value.startswith("sqlite:///"):
            return value.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
        return value

    @property
    def data_dir(self) -> Path:
        """Return the root data directory."""
        return Path("./data")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton settings object."""
    return Settings()


config = get_settings()
