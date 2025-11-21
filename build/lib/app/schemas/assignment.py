from pickletools import int4
from pydantic import BaseModel, field_validator
from datetime import datetime, date
from typing import Optional
from app.models.assignment import ShiftType

class AssignmentBase(BaseModel):
    driver_id: str
    bus_id: int
    assignment_date: date
    shift: ShiftType

class AssignmentCreate(AssignmentBase):
    start_time: datetime
    # driver_phone_number: str

    @field_validator('start_time')
    @classmethod
    def ensure_naive_datetime(cls, v):
        """Ensure datetime is timezone-naive"""
        if v and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v
    
class AssignmentCreateWithPhone(BaseModel):
    """Create assignment using driver's phone number instead of ID"""
    driver_phone_number: str
    bus_id: int
    assignment_date: date
    shift: ShiftType
    start_time: datetime
    
    @field_validator('start_time')
    @classmethod
    def ensure_naive_datetime(cls, v):
        """Ensure datetime is timezone-naive"""
        if v and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v

class AssignmentEnd(BaseModel):
    end_time: datetime

    @field_validator('end_time')
    @classmethod
    def ensure_naive_datetime(cls, v):
        """Ensure datetime is timezone-naive"""
        if v and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v

class AssignmentResponse(AssignmentBase):
    id: str
    start_time: datetime
    end_time: Optional[datetime]
    created_at: datetime
    driver_id: str
    
    class Config:
        from_attributes = True

class AssignmentResponseWithDetails(BaseModel):
    """Assignment response with driver and bus details"""
    assignment_id: str
    driver: dict
    bus: dict
    shift: str
    assignment_date: date
    start_time: datetime
    end_time: Optional[datetime]
    tracking_url: str
    message: str

class DailyAssignmentSummary(BaseModel):
    assignment_date: date
    total_assignments: int
    active_buses: int
    available_drivers: int

