from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from app.database import init_db, close_db
from app.core.Logging import setup_logging
from app.background_tasks.scheduler import start_scheduler, shutdown_scheduler
from app.api.v1.router import api_router
from app.config import settings

# Setup logging
setup_logging(level="INFO")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Run on startup and shutdown"""
    # Startup
    await init_db()
    start_scheduler()
    print("✅ Database connected")
    print("✅ Scheduler started")
    
    yield
    
    # Shutdown
    await close_db()
    shutdown_scheduler()
    print("❌ Database disconnected")

# Create app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Real-time bus tracking system",
    lifespan=lifespan
)

# CORS (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # Change to ["http://localhost:3000"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return "Welcome to the BRTLive app, have a wonderful experience"

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
