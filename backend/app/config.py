from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./tms.db"
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars-long!"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    UPLOAD_DIR: str = "uploads"
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Razorpay Configuration
    razorpay_key_id: str = "your_razorpay_key_id_here"
    razorpay_key_secret: str = "your_razorpay_key_secret_here"
    
    # SMS Configuration (MSG91)
    msg91_api_key: str = ""
    msg91_sender_id: str = "TRAFIC"
    demo_phone_numbers: str = ""
    support_phone: str = "8989563650"

    class Config:
        env_file = ".env"

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)