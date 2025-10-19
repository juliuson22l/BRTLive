from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from app.database import init_db, close_db
from app.core.Logging import setup_logging
from app.core.exceptions import (
    BRTException,
    ValidationException,
    DatabaseException,
    brt_exception_handler,
    validation_exception_handler,
    database_exception_handler
)
from app.api.v1.router import api_router

# Setup logging
setup_logging(level="INFO")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Run on startup and shutdown"""
    # Startup
    await init_db()
    print("✅ Database connected")
    
    yield
    
    # Shutdown
    await close_db()
    print("❌ Database disconnected")

# Create app
app = FastAPI(
    title="BRT Live API",
    version="1.0.0",
    description="Real-time bus tracking system",
    lifespan=lifespan
)

# CORS (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["http://localhost:3000"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(BRTException, brt_exception_handler)
app.add_exception_handler(ValidationException, validation_exception_handler)
app.add_exception_handler(DatabaseException, database_exception_handler)

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
