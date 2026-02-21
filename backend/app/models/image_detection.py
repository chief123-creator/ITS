from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.database import Base
import uuid

class ImageDetection(Base):
    __tablename__ = "image_detections"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    image_url = Column(String, nullable=False)
    plate = Column(String, nullable=True)
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)