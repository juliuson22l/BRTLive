from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BusBase(BaseModel):
    plate_number: str
    capacity: int = 40

class BusCreate(BusBase):
    current_terminal_id: Optional[str] = None

class BusUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    speed: Optional[float] = None
    current_terminal_id: Optional[str] = None
    is_active: Optional[bool] = None

class BusResponse(BusBase):
    id: int
    current_terminal_id: Optional[str]
    driver_id: Optional[str]
    is_active: bool
    latitude: Optional[float]
    longitude: Optional[float]
    speed: Optional[float]
    last_updated: datetime
    
    class Config:
        from_attributes = True

class BusWithETA(BusResponse):
    eta_minutes: Optional[int]
    distance_km: Optional[float]
