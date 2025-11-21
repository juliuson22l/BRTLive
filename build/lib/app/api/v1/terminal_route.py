from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.terminal import Terminal
from app.schemas.terminal import TerminalCreate, TerminalResponse
from app.dependencies import get_current_admin_user, get_current_active_user, get_pagination_params
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[TerminalResponse])
async def get_all_terminals(
    pagination: dict = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all terminals with pagination"""
    query = select(Terminal).offset(pagination["skip"]).limit(pagination["limit"])
    result = await db.execute(query)
    terminals = result.scalars().all()
    return terminals

@router.get("/{terminal_id}", response_model=TerminalResponse)
async def get_terminal_by_id(
    terminal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific terminal by ID"""
    query = select(Terminal).where(Terminal.id == terminal_id)
    result = await db.execute(query)
    terminal = result.scalar_one_or_none()
    
    if not terminal:
        raise HTTPException(status_code=404, detail="Terminal not found")
    
    return terminal

@router.post("/", response_model=TerminalResponse, status_code=status.HTTP_201_CREATED)
async def create_terminal(
    terminal_data: TerminalCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Create a new terminal (Admin only)"""
    terminal = Terminal(
        name=terminal_data.name,
        address=terminal_data.address,
        latitude=terminal_data.latitude,
        longitude=terminal_data.longitude,
        capacity=terminal_data.capacity
    )
    
    db.add(terminal)
    await db.commit()
    await db.refresh(terminal)
    
    return terminal

@router.put("/{terminal_id}", response_model=TerminalResponse)
async def update_terminal(
    terminal_id: str,
    terminal_data: TerminalCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Update a terminal (Admin only)"""
    query = select(Terminal).where(Terminal.id == terminal_id)
    result = await db.execute(query)
    terminal = result.scalar_one_or_none()
    
    if not terminal:
        raise HTTPException(status_code=404, detail="Terminal not found")

    setattr(terminal, "name", terminal_data.name)
    setattr(terminal, "address", terminal_data.address)
    setattr(terminal, "latitude", terminal_data.latitude)
    setattr(terminal, "longitude", terminal_data.longitude)
    setattr(terminal, "capacity", terminal_data.capacity)

    await db.commit()
    await db.refresh(terminal)
    
    return terminal

@router.delete("/{terminal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_terminal(
    terminal_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Delete a terminal (Admin only)"""
    query = select(Terminal).where(Terminal.id == terminal_id)
    result = await db.execute(query)
    terminal = result.scalar_one_or_none()
    
    if not terminal:
        raise HTTPException(status_code=404, detail="Terminal not found")
    
    # Check if any buses are at this terminal
    from app.models.bus import Bus
    bus_query = select(Bus).where(Bus.current_terminal_id == terminal_id)
    bus_result = await db.execute(bus_query)
    if bus_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete terminal with buses. Relocate buses first."
        )
    
    await db.delete(terminal)
    await db.commit()
    
    return None
