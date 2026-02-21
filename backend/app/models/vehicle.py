from sqlalchemy import Column, String
from app.database import Base
import uuid

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plate_number = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(String(36), nullable=False)  # this is user_id