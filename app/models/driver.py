from app.database import Base
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid

class Driver(Base):
    __tablename__ = "drivers"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employees_id = Column(String(20), unique=True , nullable=False)
    first_name = Column(String(50), nullable= False)
    last_name = Column (String(50), nullable= False)
    license_id = Column(String(50), unique= True, nullable= False)
    phone_number = Column(String(15), unique= True , nullable= False, index=True)
    is_active = Column(Boolean, default= True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_on_duty = Column(Boolean, default= False)
    is_available: Mapped[bool] = mapped_column(Boolean, default= True)
    current_bus_id = Column(Integer, nullable= True)
    experience_years = Column(Integer, default=0)
    tracking_id = Column(Boolean, ForeignKey("trackings.id") ,default=False)
    updated_at = Column(DateTime, default= datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    bus = relationship("Bus", back_populates= "driver", uselist=False)
    tracking_records = relationship("BusTracking", foreign_keys="[BusTracking.driver_id]", back_populates="driver", order_by="desc(BusTracking.gps_timestamp)")
    assignment = relationship("DailyAssignment", back_populates="driver")
    user = relationship("User",foreign_keys=[user_id], back_populates="drivers")

