from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
import uuid

from app.database import Base

class LocationHistory(Base):
    __tablename__ = "location_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, default=0.0)
    heading = Column(Float, nullable=True)  # Direction in degrees
    accuracy = Column(Float, nullable=True)  # GPS accuracy in meters
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    bus = relationship("Bus", backref="location_history")
