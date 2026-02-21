from app.supabase_client import supabase

def create_video_request(data: dict):
    response = supabase.table("video_requests").insert(data).execute()
    return response.data