from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # App
    APP_NAME: str = "BRTLive"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Access the credentials
    DB_USER: str = str(os.getenv("POSTGRES_USER"))
    DB_PASS: str = str(os.getenv("POSTGRES_PASSWORD"))
    DB_HOST: str = str(os.getenv("POSTGRES_HOST"))
    DB_PORT: int = 5432
    DB_NAME: str = str(os.getenv("POSTGRES_DB"))


    # Database (sync for Alembic migrations)
    DATABASE_URL: str = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    
    # Async Database (for FastAPI endpoints)
    ASYNC_DATABASE_URL: str = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Fix Heroku's postgres:// to postgresql://
    @property
    def db_url(self):
        url = self.DATABASE_URL
        if url and url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql://", 1)
        return url
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))  # 30 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
