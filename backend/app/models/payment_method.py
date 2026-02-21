"""
Payment Method Model
Stores user payment methods (UPI and Bank Account)
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid


class PaymentMethod(Base):
    __tablename__ = "user_payment_methods"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    method_type = Column(String, nullable=False)  # UPI, BANK_ACCOUNT
    upi_id = Column(String, nullable=True)
    account_holder_name = Column(String, nullable=True)
    account_number = Column(String, nullable=True)
    ifsc_code = Column(String, nullable=True)
    bank_name = Column(String, nullable=True)
    is_primary = Column(Integer, default=0, nullable=False)
    is_verified = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        CheckConstraint("method_type IN ('UPI', 'BANK_ACCOUNT')", name='valid_method_type'),
    )
    
    # Relationships
    user = relationship("User", backref="payment_methods")
