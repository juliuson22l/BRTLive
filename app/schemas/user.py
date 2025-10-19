from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import Column

class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    DRIVER = "driver"
    VIEWER = "viewer"

# Base schema (shared fields)
class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole = Field(default=UserRole.VIEWER, alias="user_role")

    @field_validator('phone')
    def validate_phone(cls, v):
        # Remove any non-digit characters
        digits = ''.join(filter(str.isdigit, v))
        if len(digits) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        return v

# Create user (signup)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

# Update user
class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = Field(None, alias="user_role")
    is_active: Optional[bool] = None

# Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Response (what API returns)
class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Token response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[dict] = None
   