from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.bus import Bus
from app.schemas.bus import BusCreate, BusUpdate, BusResponse
from app.dependencies import get_current_admin_user, get_current_active_user, get_pagination_params
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[BusResponse])
async def get_all_buses(
    pagination: dict = Depends(get_pagination_params),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all buses with pagination"""
    query = select(Bus).offset(pagination["skip"]).limit(pagination["limit"])
    result = await db.execute(query)
    buses = result.scalars().all()
    return buses

@router.get("/{bus_id}", response_model=BusResponse)
async def get_bus_by_id(
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific bus by ID"""
    query = select(Bus).where(Bus.id == bus_id)
    result = await db.execute(query)
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    return bus

@router.post("/", response_model=BusResponse, status_code=status.HTTP_201_CREATED)
async def create_bus(
    bus_data: BusCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Create a new bus (Admin only)"""
    # Check if plate number already exists
    query = select(Bus).where(Bus.plate_number == bus_data.plate_number)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bus with this plate number already exists"
        )
    
    bus = Bus(
        plate_number=bus_data.plate_number,
        capacity=bus_data.capacity
    )
    
    db.add(bus)
    await db.commit()
    await db.refresh(bus)
    
    return bus

@router.put("/{bus_id}", response_model=BusResponse)
async def update_bus(
    bus_id: int,
    bus_data: BusUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Update a bus (Admin only)"""
    query = select(Bus).where(Bus.id == bus_id)
    result = await db.execute(query)
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    # Update only provided fields
    if bus_data.latitude is not None:
        setattr(bus, "latitude", bus_data.latitude)
    if bus_data.longitude is not None:
        setattr(bus, "longitude", bus_data.longitude)
    if bus_data.speed is not None:
        setattr(bus, "speed", bus_data.speed)
    if bus_data.current_terminal_id is not None:
        setattr(bus, "current_terminal_id", bus_data.current_terminal_id)
    if bus_data.is_active is not None:
        setattr(bus, "is_active", bus_data.is_active)

    await db.commit()
    await db.refresh(bus)
    
    return bus

@router.delete("/{bus_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bus(
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Delete a bus (Admin only)"""
    query = select(Bus).where(Bus.id == bus_id)
    result = await db.execute(query)
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    await db.delete(bus)
    await db.commit()
    
    return None

@router.patch("/{bus_id}/activate", response_model=BusResponse)
async def activate_bus(
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Activate a bus (Admin only)"""
    query = select(Bus).where(Bus.id == bus_id)
    result = await db.execute(query)
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    bus.is_active = True
    await db.commit()
    await db.refresh(bus)
    
    return bus

@router.patch("/{bus_id}/deactivate", response_model=BusResponse)
async def deactivate_bus(
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Deactivate a bus (Admin only)"""
    query = select(Bus).where(Bus.id == bus_id)
    result = await db.execute(query)
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")

    bus.is_active = False
    await db.commit()
    await db.refresh(bus)
    
    return bus

@router.get("/terminal-status/{terminal_name}")
async def get_terminal_status(
    terminal_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get buses at a specific terminal"""
    from app.models.terminal import Terminal
    from sqlalchemy import func
    
    # Find terminal by name
    terminal_query = select(Terminal).where(Terminal.name.ilike(f"%{terminal_name}%"))
    terminal_result = await db.execute(terminal_query)
    terminal = terminal_result.scalar_one_or_none()
    
    if not terminal:
        raise HTTPException(status_code=404, detail="Terminal not found")
    
    # Count buses at terminal
    bus_query = select(func.count(Bus.id)).where(
        Bus.current_terminal_id == terminal.id,
        Bus.is_active == True
    )
    count_result = await db.execute(bus_query)
    bus_count = count_result.scalar()
    
    return {
        "terminal_id": terminal.id,
        "terminal_name": terminal.name,
        "bus_count": bus_count,
        "capacity": terminal.capacity,
        "available_space": terminal.capacity - bus_count
    }