from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.location import LocationUpdate, NearestTerminalRequest
from app.services.tracking_service import TrackingService
from app.schemas.bus import BusResponse

router = APIRouter()


@router.post("/location")
async def update_bus_location(
    data: LocationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update bus location using driver's phone number"""
    service = TrackingService(db)
    result = await service.update_bus_location(
        data.phone_number, data.latitude, data.longitude
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    return {"status": "success", "message": "Location updated"}


@router.get("/bus/{phone_number}", response_model=BusResponse)
async def track_bus_by_phone(
    phone_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Track bus using driver's phone number"""
    tracking_service = TrackingService(db)
    bus = await tracking_service.get_bus_by_phone(phone_number)
    
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    return bus


@router.post("/nearest-terminal")
async def find_nearest_terminal(
    data: NearestTerminalRequest,
    db: AsyncSession = Depends(get_db)
):
    """Find nearest terminal to user's location"""
    service = TrackingService(db)
    return await service.find_nearest_terminal(data.latitude, data.longitude)