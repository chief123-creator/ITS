"""
Payment Model
Handles payment records for challan payments through Razorpay
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id = Column(String(36), ForeignKey("complaints.id"), nullable=False)
    razorpay_payment_id = Column(String, unique=True, nullable=False, index=True)
    razorpay_order_id = Column(String, nullable=False, index=True)
    amount = Column(Integer, nullable=False)  # Amount in paisa
    status = Column(String, default="SUCCESS", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    complaint = relationship("Complaint", backref="payments")
    transactions = relationship("Transaction", back_populates="payment", cascade="all, delete-orphan")
