"""
Configuration settings for HR Agent System
"""
import os
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
from typing import List, Optional, Dict, Any, Union
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    # Application settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    PROJECT_NAME: str = "HR Agent System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # Default Next.js dev server
        "http://localhost:8000",  # Default FastAPI dev server
    ]
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/hrsystem"
    )
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "hrsystem")
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = ""
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@hrsystem.com"
    EMAILS_FROM_NAME: str = "HR System"
    
    # AI/ML Services
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Performance Settings
    PERFORMANCE_REVIEW_CYCLE_DAYS: int = 90  # Default to quarterly reviews
    GOAL_CHECKIN_REMINDER_DAYS: int = 7  # Remind to check in on goals weekly
    
    # File Storage
    UPLOAD_FOLDER: str = "./uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB max upload size
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Auto-approval and auto-hiring config
    AUTO_APPROVE_DEPARTMENTS: list = ["Engineering", "Product"]
    AUTO_APPROVE_BUDGET_LIMIT: int = 100000
    AUTO_HIRE_MATCH_SCORE: int = 90
    REQUIRE_HUMAN_APPROVAL_FOR_FINAL_OFFER: bool = True
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

# Initialize settings
settings = Settings()

# Create uploads directory if it doesn't exist
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)