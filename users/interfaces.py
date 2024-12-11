from sqlalchemy.orm import Session
from . import models, schemas
from core.security import get_password_hash, verify_password
from fastapi import HTTPException
from datetime import datetime, timedelta
import random
from twilio.rest import Client
from core.config import settings
from .models import UserRole



twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)



def validate_user_role(role: str) -> UserRole:
    """
    Validates and returns the correct UserRole enum.
    Raises an HTTPException if the role is invalid.
    """
    try:
        # If role is already a UserRole enum, return it
        if isinstance(role, UserRole):
            return role
        
        # If it's a string, convert to lowercase and try to match
        role_lower = role.lower()
        return next(r for r in UserRole if r.value == role_lower)
    except (StopIteration, AttributeError):
        # If no matching role is found or if role is neither string nor UserRole, raise an HTTPException
        valid_roles = ", ".join([r.value for r in UserRole])
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {valid_roles}"
        )

def create_user(db: Session, user: schemas.UserCreate):
    fetched_user = db.query(models.User).filter(models.User.username == user.username).first()
    

    if fetched_user:
        raise HTTPException(status_code=400,detail="username already registered")

    validated_role = validate_user_role(user.role)
    db_user = models.User(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_number = user.phone_number,
        password_hash=get_password_hash(user.password),
        role=validated_role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Generate and send OTP
    otp = generate_otp(db, db_user.id,user.phone_number)
    if not db_user.phone_number.startswith("+91"):
        db_user.phone_number = "+91"+db_user.phone_number
    # send_otp_sms(db_user.phone_number, otp)


    
    
    return db_user




# def generate_otp(db: Session, user_id: str):
#     otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
#     expires_at = datetime.utcnow() + timedelta(minutes=10)
#     db_otp = models.OTP(user_id=user_id, code=otp, expires_at=expires_at)
#     db.add(db_otp)
#     db.commit()
#     return otp

def generate_otp(db:Session, user_id:str, phone_number: str):
    otp = phone_number[-4:]
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    db_otp = models.OTP(user_id=user_id, code=otp, expires_at=expires_at)
    db.add(db_otp)
    db.commit()
    return otp


def send_otp_sms(phone_number: str, otp: str):
    try:
        message = twilio_client.messages.create(
            body=f"Your OTP is: {otp}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"SMS sent: {message.sid}")
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")

  

def verify_otp(db: Session, phone_number: str, otp: str):
    # Try to find the user with the given phone number
    user = db.query(models.User).filter(models.User.phone_number == phone_number).first()
    
    # If not found and the number doesn't start with "+91", try adding it
    if not user and not phone_number.startswith("+91"):
        user = db.query(models.User).filter(models.User.phone_number == f"+91{phone_number}").first()
    
    # If still not found and the number starts with "+91", try without it
    if not user and phone_number.startswith("+91"):
        user = db.query(models.User).filter(models.User.phone_number == phone_number[3:]).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_otp = db.query(models.OTP).filter(
        models.OTP.user_id == user.id,
        models.OTP.code == otp,
        models.OTP.is_used == False,
        models.OTP.expires_at > datetime.utcnow()
    ).first()
    
    if not db_otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP. Please request a new OTP if needed.")
    
    db_otp.is_used = True
    user.is_verify = True
    
    db.commit()

    return user


def resend_otp(db: Session, phone_number: str):
    # Find the user
    user = db.query(models.User).filter(models.User.phone_number == phone_number).first()
    
    if not user and not phone_number.startswith("+91"):
        user = db.query(models.User).filter(models.User.phone_number == f"+91{phone_number}").first()
    
    if not user and phone_number.startswith("+91"):
        user = db.query(models.User).filter(models.User.phone_number == phone_number[3:]).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find the most recent OTP for this user
    existing_otp = db.query(models.OTP).filter(
        models.OTP.user_id == user.id,
        models.OTP.is_used == False
    ).order_by(models.OTP.expires_at.desc()).first()
    
    # Generate a new OTP code
    new_otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    if existing_otp:
        # Update the existing OTP record
        existing_otp.code = new_otp_code
        existing_otp.expires_at = datetime.utcnow() + timedelta(minutes=10)
        db.commit()
    else:
        # If no existing OTP, create a new one
        new_otp = models.OTP(
            user_id=user.id,
            code=new_otp_code,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.add(new_otp)
        db.commit()
    
    # Send the new OTP
    send_otp_sms("+91"+user.phone_number, new_otp_code)
    
    return {"message": "New OTP sent successfully"}