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
    assignments,
    websocket,
)
from app.api.v1.terminal_route import terminals_router, routes_router

# Create the main router
api_router = APIRouter()

# Add each API to the main router
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])                    # /auth/...
api_router.include_router(bus.router, prefix="/bus", tags=["bus"])                   # /buses/...
api_router.include_router(driver.router, prefix="/driver", tags=["driver"])                 # /drivers/...
api_router.include_router(terminals_router, prefix="/terminals_router", tags=["terminals_router"])               # /terminals/...
api_router.include_router(routes_router, prefix="/routes_router", tags=["routes_router"])                  # /routes/...
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
api_router.include_router(tracking.router, prefix="/tracking", tags=["tracking"])                # /tracking/...
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])               # /dashboard/...
api_router.include_router(websocket.router, prefix="/websocket", tags=["websocket"])
