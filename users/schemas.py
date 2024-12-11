from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from .models import UserRole

class UserCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15, pattern=r'^\+?1?\d{9,15}$')
    password: str
    role: UserRole = UserRole.USER

class UserUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15, pattern=r'^\+?1?\d{9,15}$')
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    avatar_url: Optional[str] = None
    notification_preferences: Optional[dict] = None

class UserInDB(BaseModel):
    id: str
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str]
    role: UserRole
    is_active: bool
    is_verify: bool
    created_at: datetime
    updated_at: datetime
    avatar_url: Optional[str]
    last_login_at: Optional[datetime]
    notification_preferences: Optional[dict]

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: str
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str]
    role: UserRole
    is_active: bool
    is_verify: bool
    created_at: datetime
    updated_at: datetime
    avatar_url: Optional[str]
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True

class OTPVerify(BaseModel):
    phone_number: str
    otp: str