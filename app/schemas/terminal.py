from pydantic import BaseModel, Field
from typing import Optional

# Base schema (shared fields)
class TerminalBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = Field(None, max_length=255)
    capacity: int = 20

# Create terminal
class TerminalCreate(TerminalBase):
    pass

# Update terminal
class TerminalUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    address: Optional[str] = Field(None, max_length=255)

# Response (what API returns)
class TerminalResponse(TerminalBase):
    id: str
    
    class Config:
        from_attributes = True

class TerminalDashboard(TerminalResponse):
    bus_count: int
    expected_wait_time: int  # in minutes
