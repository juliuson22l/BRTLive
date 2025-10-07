"""
This file connects all your API routes together.
It imports each API file and combines them into one router.
"""

from fastapi import APIRouter

# Import all your API route files
from app.api.v1 import (
    auth,
    bus,
    driver,
    tracking,
    dashboard,
)
from app.api.v1.terminal_route import terminals_router, routes_router

# Create the main router
api_router = APIRouter()

# Add each API to the main router
api_router.include_router(auth.router)                    # /auth/...
api_router.include_router(bus.router)                   # /buses/...
api_router.include_router(driver.router)                 # /drivers/...
api_router.include_router(terminals_router)               # /terminals/...
api_router.include_router(routes_router)                  # /routes/...
api_router.include_router(tracking.router)                # /tracking/...
api_router.include_router(dashboard.router)               # /dashboard/...
