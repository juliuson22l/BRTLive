from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

# Base schema (shared fields)
class BusBase(BaseModel):
    plate_number: str = Field(..., min_length=3, max_length=20)
    capacity: int = Field(..., ge=10, le=100)
    model: str = Field(..., min_length=2, max_length=100)
    year: Optional[int] = Field(None, ge=2000, le=2030)
    current_route_id: Optional[int] = None
    current_terminal_id: Optional[str]
    driver_id: Optional[str]
    is_active: bool
    latitude: Optional[float]
    longitude: Optional[float]
    speed: Optional[float]
    status: Optional[str] = None

# Create bus
class BusCreate(BusBase):
    pass

# Update bus
class BusUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    speed: Optional[float] = None
    current_terminal_id: Optional[str] = None
    is_active: Optional[bool] = None

# Response (what API returns)
class BusResponse(BusBase):
    pass

    class Config:
        from_attributes = True
    
class BusWithETA(BusResponse):
    eta_minutes: Optional[int]
    distance_km: Optional[float]