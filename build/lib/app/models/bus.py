from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
import uuid

from app.database import Base

class Bus(Base):
    __tablename__ = "buses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plate_number = Column(String, unique=True, nullable=False)
    capacity = Column(Integer, default=40)
    current_terminal_id = Column(String, ForeignKey("terminals.id"), nullable=True)
    driver_id = Column(String, ForeignKey("drivers.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    speed = Column(Float, default=0.0)  # km/h
    last_updated: Mapped[datetime] = (mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)))
    created_at: Mapped[datetime] = (mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)))

    terminal = relationship("Terminal", back_populates="buses")
    driver = relationship("Driver", back_populates="bus")
    assignments = relationship("DailyAssignment", back_populates="bus")
