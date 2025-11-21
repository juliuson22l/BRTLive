from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class LocationBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class LocationUpdate(LocationBase):
    phone_number: str = Field(..., description="Driver's phone number")
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+2348012345678",
                "latitude": 6.5244,
                "longitude": 3.3792
            }
        }


class NearestTerminalRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 6.5244,
                "longitude": 3.3792
            }
        }


class NearestTerminalResponse(BaseModel):
    terminal_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    distance: float
    bus_count: int
    average_wait_time: int

class LocationResponse(LocationBase):
    bus_id: int
    recorded_at: datetime