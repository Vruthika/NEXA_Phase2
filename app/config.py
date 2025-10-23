from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # ============================================
    # DATABASE CONFIGURATION
    # ============================================
    DATABASE_URL: str
    MONGODB_URL: Optional[str] = None  # Optional for CMS
    
    # ============================================
    # JWT AUTHENTICATION
    # ============================================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ============================================
    # APPLICATION SETTINGS
    # ============================================
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    APP_NAME: str = "NEXA Mobile Recharge System"
    APP_VERSION: str = "1.0.0"
    
    # ============================================
    # ADMIN DEFAULT CREDENTIALS
    # ============================================
    ADMIN_DEFAULT_NAME: str = "Super Admin"
    ADMIN_DEFAULT_PHONE: str = "9090909090"
    ADMIN_DEFAULT_EMAIL: str = "admin@nexa.com"
    ADMIN_DEFAULT_PASSWORD: str = "admin123"
    
    # ============================================
    # API SETTINGS
    # ============================================
    API_V1_PREFIX: str = "/api/v1"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/admin/redoc"
    
    # ============================================
    # CORS SETTINGS
    # ============================================
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore any extra variables

settings = Settings()