from pydantic import BaseModel
from typing import Optional

class TerminalBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    capacity: int = 20

class TerminalCreate(TerminalBase):
    pass

class TerminalResponse(TerminalBase):
    id: str
    
    class Config:
        from_attributes = True

class TerminalDashboard(TerminalResponse):
    bus_count: int
    expected_wait_time: int  # in minutes
