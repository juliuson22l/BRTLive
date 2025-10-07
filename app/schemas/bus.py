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

# Create bus
class BusCreate(BusBase):
    pass

# Update bus
class BusUpdate(BaseModel):
    plate_number: Optional[str] = Field(None, min_length=3, max_length=20)
    capacity: Optional[int] = Field(None, ge=10, le=100)
    model: Optional[str] = Field(None, min_length=2, max_length=100)
    year: Optional[int] = Field(None, ge=2000, le=2030)
    current_route_id: Optional[int] = None
    is_active: Optional[bool] = None

# Response (what API returns)
class BusResponse(BusBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)