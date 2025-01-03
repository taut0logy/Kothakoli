import os
from typing import Dict, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "StoryGen AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Server settings
    HOST: str
    PORT: int
    ENVIRONMENT: str
    
    PDF_STORAGE_PATH: str = "storage/pdfs"
    TEMP_STORAGE_PATH: str = "storage/temp"

    # Cache settings
    CACHE_TTL: int = 3600  # 1 hour
    
    # API settings
    API_PREFIX: str = "/api"
    ALLOWED_HOSTS: List[str] = ["*"]
    GOOGLE_API_KEY: str
    
    # Database settings
    MONGODB_URL: str
    
    # Redis settings
    REDIS_URL: str
    REDIS_TTL: int = 3600  # 1 hour
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".txt", ".jpg", ".jpeg", ".png", ".pdf"]
    
    # Email settings
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str = "noreply@storygen.ai"
    
    # JWT settings
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    # Model settings
    DEFAULT_MODEL: str = "gemini-2.0-flash-exp"
    VISION_MODEL: str = "gemini-2.0-flash-latest"
    VOICE_MODEL: str = "gemini-2.0-flash-exp"
    AVAILABLE_MODELS: List[str] = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
        "gemini-1.5-pro-vision",
        "gemini-1.5-flash-latest"
    ]
    
    AVAILABLE_VOICE_MODELS: List[str] = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
    ]
    
    AVAILABLE_VISION_MODELS: List[str] = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
        "gemini-1.5-pro-vision",
    ]
    
    MODEL_CONFIGS: Dict = {
        "gemini-1.5-pro": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 2048,
        },
        "gemini-1.5-pro-vision": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 2048,
        },
        "gemini-1.5-flash-latest": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 1024,
        },
        "gemini-2.0-flash-exp": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
    }
    
    # Security settings
    CORS_ORIGINS: List[str] = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    ENCRYPTION_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 