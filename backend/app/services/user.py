from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.user import AadhaarStatus, AccountStatus

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    aadhaar_number: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: UUID
    aadhaar_status: AadhaarStatus
    account_status: AccountStatus
    trust_points: int
    wallet_balance: float
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserOut] = None  # optional, can return user data

class OTPRequest(BaseModel):
    aadhaar_number: str

class OTPVerify(BaseModel):
    aadhaar_number: str
    otp: str