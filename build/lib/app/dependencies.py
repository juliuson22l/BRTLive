from typing import Optional
from fastapi import Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User, UserRole
from app.core.security import get_current_user

# Get current active user
async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.is_active is False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Get admin user only
async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if current_user.role is not UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Get driver user only
async def get_current_driver_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if current_user.role is not UserRole.DRIVER:
        raise HTTPException(status_code=403, detail="Driver access required")
    return current_user

# Pagination helper
def get_pagination_params(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> dict:
    return {"skip": skip, "limit": limit}

# Get bus or 404 error
async def get_bus_or_404(bus_id: str, db: AsyncSession = Depends(get_db)):
    from app.models.bus import Bus
    query = select(Bus).where(Bus.id == bus_id)
    result = await db.execute(query)
    bus = result.scalar_one_or_none()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    return bus

# Get driver or 404 error
async def get_driver_or_404(driver_id: str, db: AsyncSession = Depends(get_db)):
    from app.models.driver import Driver
    query = select(Driver).where(Driver.id == driver_id)
    result = await db.execute(query)
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver

# Get terminal or 404 error
async def get_terminal_or_404(terminal_id: str, db: AsyncSession = Depends(get_db)):
    from app.models.terminal import Terminal
    query = select(Terminal).where(Terminal.id == terminal_id)
    result = await db.execute(query)
    terminal = result.scalar_one_or_none()
    if not terminal:
        raise HTTPException(status_code=404, detail="Terminal not found")
    return terminal