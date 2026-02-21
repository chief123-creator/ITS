from fastapi import APIRouter
from app.services.video_service import create_video_request

router = APIRouter()

@router.post("/create-request")
async def create_request(data: dict):
    return create_video_request(data)