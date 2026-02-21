New_updates
from typing import Optional
from supabase import create_client, Client
from app.config import settings

supabase: Optional[Client] = None

def get_supabase() -> Client:
    global supabase
    if supabase is None:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return supabase  # type: ignore
from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_KEY
)
main
