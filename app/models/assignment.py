from sqlalchemy import Column, String, DateTime, ForeignKey, Date, Enum, Integer, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone, date
import uuid
import enum

from app.database import Base

class ShiftType(str, enum.Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"

class DailyAssignment(Base):
    __tablename__ = "daily_assignments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    driver_id = Column(String, ForeignKey("drivers.id"), unique=True, nullable=False)
    bus_id = Column(Integer, ForeignKey("buses.id"), unique=True, nullable=False)
    assignment_date = Column(Date, nullable=False, index=True)
    shift = Column(Enum(ShiftType), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint(
            'driver_id', 
            'assignment_date', 
            'shift',
            name='uq_driver_date_shift'
        ),
    )

    driver = relationship("Driver", back_populates="assignments")
    bus = relationship("Bus", back_populates="assignments")
