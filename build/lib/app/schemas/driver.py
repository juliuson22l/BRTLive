from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DriverBase(BaseModel):
    name: str
    phone_number: str
    license_number: Optional[str] = None

class DriverCreate(DriverBase):
    user_id: Optional[str] = None  # Optional link to User

class DriverUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    license_number: Optional[str] = None
    is_active: Optional[bool] = None

class DriverResponse(DriverBase):
    id: str
    user_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class DriverWithBus(DriverResponse):
    bus_id: Optional[str] = None
    bus_plate_number: Optional[str] = None

class DriverWithUser(DriverResponse):
    """Driver info with linked user account details"""
    username: Optional[str] = None
    email: Optional[str] = None
    has_user_account: bool = False