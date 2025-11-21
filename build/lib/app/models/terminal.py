from app.database import Base
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import uuid

class Terminal(Base):
    __tablename__ = "terminals"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique= True, nullable= False)
    address = Column(String, nullable=True)
    longitude = Column(Float, nullable= False)
    latitude = Column( Float, nullable= False)
    capacity = Column(Integer, default=20)
    created_at = Column(DateTime, default =lambda: datetime.now(timezone.utc))

    buses = relationship("Bus",foreign_keys="[Bus.terminal_id]", back_populates="terminal")
