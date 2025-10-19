from app.database import Base
from datetime import datetime, timezone
from sqlalchemy import Column, Boolean, String, Integer,Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship


class Eta(Base):
    __tablename__ = "etas"
    id = Column(Integer, primary_key= True , index= True)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)   
    estimated_arrival_time = Column(DateTime, nullable=False)
    estimated_minutes_away = Column(Integer, nullable=False)
    confidence_level = Column(Float, default=0.8)
    user_id = Column(Integer, ForeignKey('users.id'))
    prediction_method = Column(String(50), default="real_time")
    calculated_from_phone_location = Column(Boolean, default=True)
    last_phone_update_used = Column(DateTime, nullable=True)
    calculated_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_updated = Column(DateTime, default=datetime.now(timezone.utc),onupdate=datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="etas")
    bus = relationship("Bus", backref="buses_eta")
    route = relationship("Route", backref="route_etas")
    