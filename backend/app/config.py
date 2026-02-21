from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

class Settings(BaseSettings):
    # ... existing settings (DATABASE_URL, JWT_SECRET_KEY, etc.)
    DATABASE_URL: str = ""
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    UPLOAD_DIR: str = "uploads"
    New_updates
    
    # Add these two new lines
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_BUCKET: str = "complaint-videos"  # Optional default

    class Config:
        env_file = ".env"
        case_sensitive = False

    settings = Settings()
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
 main
