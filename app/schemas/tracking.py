from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

# Location update from driver
class LocationUpdate(BaseModel):
    bus_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed: Optional[float] = Field(None, ge=0, le=200)
    heading: Optional[float] = Field(None, ge=0, le=360)

# Response (what API returns)
class TrackingResponse(BaseModel):
    id: int
    bus_id: int
    latitude: float
    longitude: float
    speed: Optional[float] = None
    heading: Optional[float] = None
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)
