from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # App
    APP_NAME: str = "BRT Live API"
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

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
