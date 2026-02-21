from fastapi import APIRouter, UploadFile, File, HTTPException
import random
import string

router = APIRouter(prefix="/detect", tags=["Detection"])

@router.post("/plate")
async def detect_plate(image: UploadFile = File(...)):
    # In reality, you'd call your ML model here
    # For now, return a mock plate number
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Mock: generate a random Indian-like plate
    import random
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=4))
    plate = f"MH{letters}{numbers}"
    
    return {"plate": plate}