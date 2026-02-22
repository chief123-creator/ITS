from fastapi import APIRouter, HTTPException
from app.supabase_client import get_supabase
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/ml", tags=["ML"])

class MLDataOut(BaseModel):
    id: str
    complaint_id: Optional[str]
    username: str
    email: str
    location: str
    vehicle_number: str
    status: str
    video_url: str
    created_at: str

@router.get("/pending", response_model=List[MLDataOut])
def get_pending_ml_data():
    supabase = get_supabase()
    response = supabase.table("ml_data").select("*").eq("status", "pending").execute()
    return response.data

@router.patch("/{record_id}")
def update_ml_data(record_id: str, plate: str):
    supabase = get_supabase()
    response = supabase.table("ml_data").update({
        "vehicle_number": plate,
        "status": "completed"
    }).eq("id", record_id).execute()
    if not response.data:
        raise HTTPException(404, "Record not found")
    return {"status": "updated"}