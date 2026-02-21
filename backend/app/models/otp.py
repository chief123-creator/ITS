from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
import uuid
from datetime import datetime, timedelta
from app.database import Base

class OTP(Base):
    __tablename__ = "otps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    otp_code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=10))
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)