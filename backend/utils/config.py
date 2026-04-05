"""
Configuration settings for HR Agent System
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./hr_system.db")
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")

    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # Communication APIs
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    SENDGRID_API_KEY: Optional[str] = None

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Application settings
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # File storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # CORS - stored as comma-separated string, parsed at runtime
    BACKEND_CORS_ORIGINS: str = "http://localhost:5000"

    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = ""
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@hrsystem.com"
    EMAILS_FROM_NAME: str = "HR System"

    # Performance Settings
    PERFORMANCE_REVIEW_CYCLE_DAYS: int = 90
    GOAL_CHECKIN_REMINDER_DAYS: int = 7

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Auto-approval config
    AUTO_APPROVE_BUDGET_LIMIT: int = 100000
    AUTO_HIRE_MATCH_SCORE: int = 90
    REQUIRE_HUMAN_APPROVAL_FOR_FINAL_OFFER: bool = True

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# Create uploads directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
