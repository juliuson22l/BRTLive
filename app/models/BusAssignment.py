from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class BusAssignment(Base):
    __tablename__ = "bus_assignments"
    id = Column(Integer, primary_key= True , index= True)
    bus_id = Column(Integer, ForeignKey("buses.id"))
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    start_shift = Column(DateTime, nullable= False)
    end_shift = Column(DateTime, nullable=True)
    planned_shift_duration_hours = Column(Integer, default=8)
    tracking_started_at = Column(DateTime, nullable=True)
    tracking_ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default= True)
    assignment_status = Column(String(20), default="assigned")
    created_at = Column(DateTime, default= datetime.now(timezone.utc))

    driver = relationship("Driver", back_populates="bus_assignment")
    bus = relationship("Bus", back_populates="bus_assignment")
    