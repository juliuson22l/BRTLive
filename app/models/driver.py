from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
import uuid

from app.database import Base

class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=True)  # Link to User
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False, index=True)
    license_number = Column(String, unique=True, nullable=True)  # Driver's license number
    is_active = Column(Boolean, default=True)
    created_at: Mapped[datetime] = (mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)))
    
    user = relationship("User", back_populates="drivers")  # Relationship to User
    bus = relationship("Bus", back_populates="driver", uselist=False)
    assignments = relationship("DailyAssignment", back_populates="driver")

