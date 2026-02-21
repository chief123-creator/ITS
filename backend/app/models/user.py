from sqlalchemy import Column, String, Boolean, Integer, DateTime, Float, Enum
import uuid
from datetime import datetime
from app.database import Base
import enum

class AadhaarStatus(str, enum.Enum):
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    WARNED = "warned"
    SUSPENDED = "suspended"
    BANNED = "banned"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True, unique=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    aadhaar_number = Column(String, unique=True, nullable=False)
    aadhaar_status = Column(Enum(AadhaarStatus), default=AadhaarStatus.UNVERIFIED)
    account_status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    hashed_password = Column(String, nullable=False)
    trust_points = Column(Integer, default=100)
    wallet_balance = Column(Float, default=0.0)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)