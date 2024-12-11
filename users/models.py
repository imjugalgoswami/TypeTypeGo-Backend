import enum
from db.basemodel import BaseModel
from sqlalchemy import JSON, Column, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class UserRole(enum.Enum):
    USER = "user" 
    ADMIN = "admin" 

class User(BaseModel):
    __tablename__ = "users"

    username = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole),default=UserRole.USER)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verify = Column(Boolean, default=False, nullable=False)
    avatar_url = Column(String, nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    notification_preferences = Column(JSON, nullable=True)



class OTP(BaseModel):
    __tablename__ = "otps"

    user_id = Column(String(12), index=True)
    code = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)