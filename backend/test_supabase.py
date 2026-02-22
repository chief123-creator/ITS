from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
supabase = create_client(url, key)
try:
    data = supabase.table("ml_data").select("*").limit(1).execute()
    print("Connection OK:", data)
except Exception as e:
    print("Error:", e)