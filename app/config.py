from pydantic_settings import BaseSettings
from typing import List, Optional, ClassVar
import os

class Settings(BaseSettings):
    # Database
    ASYNC_DATABASE_URL: ClassVar[str] = os.getenv("DATABASE_URL", "postgresql+asyncpg:///./brtlive.db")
    DATABASE_URL = ASYNC_DATABASE_URL

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App
    APP_NAME: str = "BRTLive"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS - accept as string
    BACKEND_CORS_ORIGINS: str = "*"    
    @property
    def cors_origins(self) -> List[str]:
        """Convert CORS string to list"""
        if self.BACKEND_CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
