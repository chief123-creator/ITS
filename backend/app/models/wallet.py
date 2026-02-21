"""
Wallet Model
Manages wallet balances for Government, Reporters, and Platform
"""
from sqlalchemy import Column, String, Integer, DateTime, CheckConstraint, UniqueConstraint
from app.database import Base
from datetime import datetime
import uuid


class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_type = Column(String, nullable=False)  # GOVT, REPORTER, PLATFORM
    owner_id = Column(String(36), nullable=False)
    balance = Column(Integer, default=0, nullable=False)  # Balance in paisa
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('owner_type', 'owner_id', name='unique_wallet'),
        CheckConstraint('balance >= 0', name='positive_balance'),
        CheckConstraint("owner_type IN ('GOVT', 'REPORTER', 'PLATFORM')", name='valid_owner_type'),
    )
