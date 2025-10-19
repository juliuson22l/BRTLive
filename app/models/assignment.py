from app.database import Base
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone, date
from sqlalchemy.dialects.postgresql import ENUM
import uuid


class ShiftType(Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"

class DailyAssignment(Base):
    __tablename__ = "assignments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    shift = Column(ENUM(ShiftType), nullable= False)
    start_time = Column(DateTime, nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(nullable=True)    
    is_active = Column(Boolean, default= True)
    assignment_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    driver = relationship("Driver",foreign_keys=[driver_id], back_populates="assignment")
    bus = relationship("Bus",foreign_keys=[bus_id], backref="assignment")
    