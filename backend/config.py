"""
MockPilot AI — Centralized Settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "MockPilot AI"
    APP_VERSION: str = "1.0.0"

    # Groq
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # JWT
    JWT_SECRET_KEY: str = "mockpilot-change-in-prod"
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

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
