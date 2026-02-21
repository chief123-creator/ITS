"""
Transaction Model
Logs all wallet transactions for audit trail
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    payment_id = Column(String(36), ForeignKey("payments.id"), nullable=False)
    receiver_type = Column(String, nullable=False)  # GOVT, REPORTER, PLATFORM
    receiver_id = Column(String(36), nullable=False)
    amount = Column(Integer, nullable=False)  # Amount in paisa
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    payment = relationship("Payment", back_populates="transactions")
