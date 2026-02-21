"""
Withdrawal Request Model
Manages withdrawal requests from reporters
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid


class WithdrawalRequest(Base):
    __tablename__ = "withdraw_requests"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # Amount in paisa
    status = Column(String, default="PENDING", nullable=False)  # PENDING, APPROVED, REJECTED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        CheckConstraint("status IN ('PENDING', 'APPROVED', 'REJECTED')", name='valid_withdrawal_status'),
    )
    
    # Relationships
    user = relationship("User", backref="withdrawal_requests")
