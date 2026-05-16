"""
MockPilot AI — Centralized Settings
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "MockPilot AI"
    APP_VERSION: str = "1.0.0"

    # Groq
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # JWT — MUST be set in production via environment variable
    JWT_SECRET_KEY: str = "mockpilot-dev-secret-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # DB
    DATABASE_URL: str = "sqlite:///./mockpilot.db"

    # Whisper
    WHISPER_MODEL: str = "base"

    # Files
    UPLOAD_DIR: str = "uploads"
    REPORTS_DIR: str = "reports"
    MAX_UPLOAD_SIZE_MB: int = 10

    # Backend
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = ""  # Set in Render for CORS

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def jwt_key_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(
                "JWT_SECRET_KEY must be set! "
                "Add it to Render → Environment Variables."
            )
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
