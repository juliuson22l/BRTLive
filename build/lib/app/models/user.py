from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime, timezone
import uuid
import enum

from app.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DRIVER = "driver"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    drivers = relationship("Driver", back_populates="user")