from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from app.dependencies import get_db, require_admin, get_current_active_user
from app.schemas.bus import BusCreate, BusUpdate, BusResponse
from app.models.bus import Bus
from app.models.user import User
from app.models.route import Route
from app.models.tracking import BusTracking as Tracking
from app.utils.helpers import calculate_eta_minutes

router = APIRouter()

@router.get("/", response_model=List[BusResponse])
async def get_buses(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all buses"""
    query = select(Bus)
    
    if is_active is not None:
        query = query.filter(Bus.is_active == is_active)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{bus_id}", response_model=BusResponse)
async def get_bus(
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get single bus"""
    result = await db.execute(select(Bus).filter(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    return bus

@router.post("/", response_model=BusResponse, status_code=status.HTTP_201_CREATED)
async def create_bus(
    bus_data: BusCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Create new bus"""
    
    # Check plate number exists
    result = await db.execute(
        select(Bus).filter(Bus.plate_number == bus_data.plate_number)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Plate number already exists")
    
    # Create bus
    new_bus = Bus(**bus_data.model_dump())
    db.add(new_bus)
    await db.commit()
    await db.refresh(new_bus)
    
    return new_bus

@router.put("/{bus_id}", response_model=BusResponse)
async def update_bus(
    bus_id: int,
    bus_data: BusUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update bus"""
    result = await db.execute(select(Bus).filter(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    # Update fields
    for field, value in bus_data.model_dump(exclude_unset=True).items():
        setattr(bus, field, value)
    
    await db.commit()
    await db.refresh(bus)
    
    return bus

@router.delete("/{bus_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bus(
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete bus"""
    result = await db.execute(select(Bus).filter(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    await db.delete(bus)
    await db.commit()

@router.patch("/{bus_id}/activate")
async def activate_bus(
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Turn bus on"""
    result = await db.execute(select(Bus).filter(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")

    bus.is_active
    await db.commit()
    
    return {"message": "Bus activated"}

@router.patch("/{bus_id}/deactivate")
async def deactivate_bus(
    bus_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Turn bus off"""
    result = await db.execute(select(Bus).filter(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")

    assert bus is not None
    await db.commit()
    
    return {"message": "Bus deactivated"}
@router.get("/terminal-status/{terminal_name}")
async def get_terminal_status(
    terminal_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Return buses en route to a terminal and their ETA."""
    
    # Step 1: Get all routes for that terminal
    route_query = select(Route).filter(Route.destination_terminal == terminal_name)
    routes_result = await db.execute(route_query)
    routes = routes_result.scalars().all()
    
    if not routes:
        raise HTTPException(status_code=404, detail="Terminal not found")

    # Step 2: Collect bus IDs for these routes
    route_ids = [r.id for r in routes]
    bus_query = select(Bus).filter(Bus.route_id.in_(route_ids))
    buses_result = await db.execute(bus_query)
    buses = buses_result.scalars().all()

    if not buses:
        return {"message": "No bus available on this route"}

    # Step 3: Check active tracking data (within last 10 mins)
    time_ago = datetime.now(timezone.utc) - timedelta(minutes=10)
    active_query = (
        select(Tracking)
        .filter(Tracking.bus_id.in_([b.id for b in buses]))
        .filter(Tracking.gps_timestamp >= time_ago)
        .order_by(Tracking.gps_timestamp.desc())
    )
    tracking_result = await db.execute(active_query)
    active_tracks = tracking_result.scalars().all()

    if not active_tracks:
        return {"message": "No bus available on this route"}

    # Step 4: Calculate ETA for each bus (using your existing logic)
    response_data = []
    for track in active_tracks:
        eta = await calculate_eta_minutes(track.latitude, track.longitude, terminal_name)
        response_data.append({
            "bus_id": track.bus_id,
            "latitude": track.latitude,
            "longitude": track.longitude,
            "eta": eta,
            "timestamp": track.gps_timestamp.isoformat()
        })

    return response_data