from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from app.models.assignment import ShiftType

class AssignmentBase(BaseModel):
    bus_id: str
    driver_id: str
    shift: ShiftType
    planned_shift_duration: int=8
    assignment_date: date

class AssignmentCreate(AssignmentBase):
    start_time: datetime

class AssignmentEnd(BaseModel):
    end_time: datetime

class AssignmentResponse(AssignmentBase):
    id: str
    start_time: datetime
    end_time: Optional[datetime]
    created_at: datetime

    class Config:
        form_attributes = True
    
class DailyAssignmentSummary(BaseModel):
    assignment_date: date
    total_assignments: int | None
    active_buses: int | None
    available_drivers: int | None




