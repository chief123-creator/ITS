from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum
import uuid
from datetime import datetime
from app.database import Base
import enum

class VehicleType(str, enum.Enum):
    TWO_WHEELER = "two_wheeler"
    FOUR_WHEELER = "four_wheeler"
    TRUCK = "truck"

class ActionType(str, enum.Enum):
    DIRECT_CALL = "direct_call"
    OFFICIAL_ISSUE = "official_issue"

class ComplaintStatus(str, enum.Enum):
    PENDING = "pending"
    TIMER_RUNNING = "timer_running"
    RESOLVED = "resolved"
    FINE_APPLIED = "fine_applied"

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    video_url = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    recorded_at = Column(DateTime, nullable=False)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    action_type = Column(Enum(ActionType), nullable=False)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.PENDING)
    plate_number = Column(String, nullable=True)
    timer_end_time = Column(DateTime, nullable=True)
    fine_amount = Column(Float, default=0.0)
    proof_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)