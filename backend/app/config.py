from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./tms.db"
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars-long!"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    UPLOAD_DIR: str = "uploads"
    FRONTEND_URL: str = "http://localhost:5173"
    SUPABASE_BUCKET: str = "complaints"
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None

    class Config:
        env_file = str(Path(__file__).resolve().parent.parent / ".env")

settings = Settings()

# expose commonly-used supabase values as module-level names for imports
SUPABASE_URL = settings.SUPABASE_URL
# some code expects SUPABASE_SERVICE_KEY; map it to the env var named SUPABASE_KEY
SUPABASE_SERVICE_KEY = settings.SUPABASE_KEY

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)