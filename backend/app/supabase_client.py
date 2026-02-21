from typing import Optional
from supabase import create_client, Client
from app.config import settings

_supabase: Optional[Client] = None

def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        if settings.SUPABASE_URL is None or settings.SUPABASE_KEY is None:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in settings")
        _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _supabase  # type: ignore