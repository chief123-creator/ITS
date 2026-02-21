from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random
import string
from app import models, schemas
from app.core import security
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=schemas.Token)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        (models.User.email == user_data.email) | (models.User.phone == user_data.phone)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email or phone already registered")
    
    aadhaar_exists = db.query(models.User).filter(models.User.aadhaar_number == user_data.aadhaar_number).first()
    if aadhaar_exists:
        raise HTTPException(status_code=400, detail="Aadhaar already registered")
    
    hashed_password = security.get_password_hash(user_data.password)
    user = models.User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        aadhaar_number=user_data.aadhaar_number,
        hashed_password=hashed_password,
        # aadhaar_status=models.AadhaarStatus.UNVERIFIED,
        # account_status=models.AccountStatus.ACTIVE
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    access_token = security.create_access_token(data={"sub": user.email})
    user_out = schemas.UserOut.from_orm(user)
    return {"access_token": access_token, "token_type": "bearer", "user": user_out}

@router.post("/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user or not security.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = security.create_access_token(data={"sub": user.email})
    user_out = schemas.UserOut.from_orm(user)
    return {"access_token": access_token, "token_type": "bearer", "user": user_out}

@router.post("/send-otp", status_code=200)
def send_otp(otp_req: schemas.OTPRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.aadhaar_number == otp_req.aadhaar_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="Aadhaar not registered")
    
    otp_code = ''.join(random.choices(string.digits, k=6))
    otp = models.OTP(user_id=user.id, otp_code=otp_code)
    db.add(otp)
    db.commit()
    
    # In production, send SMS/email; for testing we return OTP
    return {"message": "OTP sent successfully", "otp": otp_code}

@router.post("/verify-otp", response_model=schemas.UserOut)
def verify_otp(verify_data: schemas.OTPVerify, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.aadhaar_number == verify_data.aadhaar_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="Aadhaar not registered")
    
    otp = db.query(models.OTP).filter(
        models.OTP.user_id == user.id,
        models.OTP.otp_code == verify_data.otp,
        models.OTP.is_used == False,
        models.OTP.expires_at > datetime.utcnow()
    ).first()
    
    if not otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    db.query(models.OTP).filter(models.OTP.id == otp.id).update({models.OTP.is_used: True})
    db.query(models.User).filter(models.User.id == user.id).update({models.User.aadhaar_status: "VERIFIED"})
    db.commit()
    db.refresh(user)
    
    return schemas.UserOut.from_orm(user)