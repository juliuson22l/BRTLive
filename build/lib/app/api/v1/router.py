"""
This file connects all your API routes together.
It imports each API file and combines them into one router.
"""

from fastapi import APIRouter
from app.api.v1 import auth, bus, driver, terminal_route, dashboard, tracking, assignments, websocket

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(bus.router, prefix="/bus", tags=["bus"])
api_router.include_router(driver.router, prefix="/driver", tags=["driver"])
api_router.include_router(terminal_route.router, prefix="/terminal_route", tags=["terminals_router"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(tracking.router, prefix="/tracking", tags=["tracking"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])

