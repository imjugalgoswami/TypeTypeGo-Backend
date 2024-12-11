from fastapi import APIRouter, Depends,status,Request
from sqlalchemy.orm import Session
from . import interfaces, schemas
from db.session import get_db
from core.security import oauth2_scheme


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)]
)

@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = interfaces.create_user(db, user)
    return db_user

@router.post("/verify-otp", response_model=schemas.UserResponse)
def verify_otp(otp_data: schemas.OTPVerify, db: Session = Depends(get_db)):
    user = interfaces.verify_otp(db, otp_data.phone_number, otp_data.otp)
    return user

@user_router.get('/me', status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
def get_user_detail(request: Request):
    return request.user

@router.post("/resend-otp")
def resend_otp(phone_number: str, db: Session = Depends(get_db)):
    return interfaces.resend_otp(db, phone_number)


