from pydantic_settings import BaseSettings
from typing import List, Optional, ClassVar
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: ClassVar[str] = "postgresql://localhost/brtlive"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App
    APP_NAME: str = "BRTLive"
    DEBUG: bool = False
    
    # CORS - accept as string
    BACKEND_CORS_ORIGINS: str = "*"    
    @property
    def cors_origins(self) -> List[str]:
        """Convert CORS string to list"""
        if self.BACKEND_CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
    
    @property
    def db_url(self):
        """Convert postgres:// to postgresql+asyncpg://"""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
