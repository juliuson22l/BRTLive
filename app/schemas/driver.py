from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

# Base schema (shared fields)
class DriverBase(BaseModel):
    user_id: int
    license_number: str = Field(..., min_length=5, max_length=50)
    experience_years: int = Field(..., ge=0, le=50)

# Create driver
class DriverCreate(DriverBase):
    pass

# Update driver
class DriverUpdate(BaseModel):
    license_number: Optional[str] = Field(None, min_length=5, max_length=50)
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    is_available: Optional[bool] = None
    current_bus_id: Optional[int] = None

# Response (what API returns)
class DriverResponse(DriverBase):
    id: int
    is_available: bool
    current_bus_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)