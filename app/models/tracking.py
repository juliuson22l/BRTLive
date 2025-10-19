from app.database import Base
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class BusTracking (Base):
    __tablename__ = "trackings"
    id = Column(Integer, primary_key= True , index = True)
    bus_id = Column(Integer , ForeignKey("buses.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"))
    longitude = Column(Float , nullable= False)
    latitude = Column(Float , nullable= False)
    speed_km = Column(Float, default= 0.0)
    heading = Column(Float, nullable= False)
    last_updated = Column(DateTime, default= datetime.now(timezone.utc), onupdate= datetime.now(timezone.utc))
    gps_timestamp = Column(DateTime, default= datetime.now(timezone.utc), nullable=False, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable= True)
    terminal_name = Column(String, ForeignKey("terminal.name"))

    tracking_bus = relationship("Bus", foreign_keys=[bus_id], back_populates= "tracking_history")
    driver = relationship("Driver",foreign_keys=[driver_id] , back_populates="tracking_records")

