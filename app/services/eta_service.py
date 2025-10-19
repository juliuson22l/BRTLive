from typing import Optional
from app.utils.distance import calculate_distance

class ETAService:
    AVERAGE_SPEED_KMH = 30  # Average city speed
    TRAFFIC_FACTOR = 1.3  # Traffic multiplier
    STOP_TIME_PER_TERMINAL = 3  # Minutes per stop
    
    def calculate_eta(
        self,
        bus_lat: float,
        bus_lon: float,
        dest_lat: float,
        dest_lon: float,
        current_speed: Optional[float] = None,
        stops_remaining: int = 0
    ) -> dict:
        """Calculate ETA from bus location to destination"""
        
        # Calculate distance
        distance_km = calculate_distance(bus_lat, bus_lon, dest_lat, dest_lon)
        
        # Use current speed if available, otherwise use average
        speed = current_speed if current_speed and current_speed > 0 else self.AVERAGE_SPEED_KMH
        
        # Calculate base travel time
        travel_time_hours = distance_km / speed
        travel_time_minutes = travel_time_hours * 60
        
        # Apply traffic factor
        adjusted_time = travel_time_minutes * self.TRAFFIC_FACTOR
        
        # Add stop time
        total_time = adjusted_time + (stops_remaining * self.STOP_TIME_PER_TERMINAL)
        
        return {
            "eta_minutes": round(total_time),
            "distance_km": round(distance_km, 2),
            "estimated_speed_kmh": round(speed, 1)
        }
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.services.tracking_service import TrackingService
from app.schemas.bus import BusResponse

router = APIRouter()

class LocationUpdate(BaseModel):
    phone_number: str
    latitude: float
    longitude: float

class NearestTerminalRequest(BaseModel):
    latitude: float
    longitude: float

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
    service = TrackingService(db)
    bus = await service.get_bus_by_phone(phone_number)
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