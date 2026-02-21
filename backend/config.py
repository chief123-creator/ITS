import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ===== Supabase Config =====
SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_BUCKET: str = os.getenv("SUPABASE_BUCKET", "complaint-videos")

# ===== Validation (Fail Fast) =====
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is not set in .env")

if not SUPABASE_SERVICE_KEY:
    raise ValueError("SUPABASE_SERVICE_KEY is not set in .env")