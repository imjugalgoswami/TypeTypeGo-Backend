from users.models import User
from fastapi.exceptions import HTTPException
from core.security import verify_password
from core.config import settings
from datetime import timedelta
from auth.responses import TokenResponse
from core.security import create_access_token, create_refresh_token, get_token_payload
from sqlalchemy.orm import Session

def get_token(data, db:Session):
    user = db.query(User).filter(User.username == data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Email is not registered with us.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Invalid Login Credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    _verify_user_access(user=user)
    
    return _get_user_token(user=user)

def get_refresh_token(token, db):   
    payload = get_token_payload(token=token)
    user_id = payload.get('id', None)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _get_user_token(user=user, refresh_token=token)

def _verify_user_access(user: User):
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Your account is inactive. Please contact support.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verify:
        raise HTTPException(
            status_code=400,
            detail="Your account is unverified. Please verify your account.",
            headers={"WWW-Authenticate": "Bearer"},
        )

def _get_user_token(user: User, refresh_token = None):
    payload = {"id": user.id,"role":user.role.value}
    
    access_token_expiry = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(payload, access_token_expiry)
    if not refresh_token:
        refresh_token = create_refresh_token(payload)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=access_token_expiry.seconds  # in seconds
    )