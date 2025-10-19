from enum import Enum
from datetime import datetime, timezone
from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.sql import func
import uuid

class BusStatus(Enum):
    IN_TRANSIT = "in_transit"
    AT_TERMINAL = "at_terminal"
    OUT_OF_SERVICE = "out_of_service"
    MAINTENANCE = "maintenance"

class Bus(Base):
    __tablename__ = "buses"

    id = Column(String, primary_key= True , default=lambda: str(uuid.uuid4()))
    plate_number = Column(String(25),unique= True , nullable= False)
    capacity = Column(Integer, default= 50)
    terminal_id = Column(String, ForeignKey("terminals.id"))
    current_passenger_count = Column( Integer, default=0)
    driver_id = Column(String, ForeignKey("drivers.id"), nullable=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    status = Column(ENUM(BusStatus, name="bus_status"), default=BusStatus.IN_TRANSIT, nullable=False)
    is_active = Column(Boolean, default= True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    speed = Column(Float, default=0.0)  # km/h
    current_route_id = Column(Integer, ForeignKey("routes.id"), nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    route = relationship("Route", foreign_keys=[route_id], back_populates="buses_at_route")
    terminal = relationship("Terminal", foreign_keys=[terminal_id], back_populates="buses")
    tracking_history = relationship("BusTracking", foreign_keys="[BusTracking.bus_id]", back_populates="tracking_bus", order_by="desc(BusTracking.gps_timestamp)")
    driver = relationship("Driver", foreign_keys=[driver_id], back_populates="bus")
