from fastapi import APIRouter, UploadFile, File, HTTPException
import random
import string

router = APIRouter(prefix="/detect", tags=["Detection"])

@router.post("/plate")
async def detect_plate(image: UploadFile = File(...)):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Mock detection – replace with actual ML later
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=4))
    plate = f"MH{letters}{numbers}"
    
    return {"plate": plate}