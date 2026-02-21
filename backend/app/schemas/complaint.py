from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.complaint import VehicleType, ActionType, ComplaintStatus

class ComplaintBase(BaseModel):
    vehicle_type: VehicleType
    action_type: ActionType
    latitude: float
    longitude: float
    recorded_at: datetime

class ComplaintCreate(ComplaintBase):
    pass

class ComplaintOut(ComplaintBase):
    id: UUID
    user_id: UUID
    video_url: str  # will be the full URL
    status: ComplaintStatus
    plate_number: Optional[str] = None
    timer_end_time: Optional[datetime] = None
    fine_amount: float
    proof_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ComplaintStatusUpdate(BaseModel):
    status: Optional[ComplaintStatus] = None
    plate_number: Optional[str] = None
    fine_amount: Optional[float] = None