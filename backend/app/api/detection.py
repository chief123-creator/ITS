import uuid
from typing import Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.supabase_client import get_supabase
from app.config import settings

router = APIRouter(prefix="/detect", tags=["Detection"])

@router.post("/plate")
async def detect_plate(image: UploadFile = File(...)):
    # basic validation
    content_type = image.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Generate unique filename (keep original extension if available)
    original_name = (image.filename or "").strip()
    if "." in original_name:
        ext = original_name.split('.')[-1]
    else:
        # default to jpg
        ext = "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"

    # Read image bytes
    try:
        image_bytes = await image.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read uploaded file: {e}")

    # Upload to Supabase Storage
    supabase = get_supabase()
    try:
        storage = supabase.storage
        # supabase-py storage API may return different shapes; call upload and then get a public URL
        upload_resp = storage.from_(settings.SUPABASE_BUCKET).upload(f"uploads/{filename}", image_bytes)

        # Attempt to obtain a public URL for the uploaded file
        public = storage.from_(settings.SUPABASE_BUCKET).get_public_url(f"uploads/{filename}")
        # get_public_url may return a dict or a string depending on client version
        if isinstance(public, dict):
            # common keys from various clients
            image_url = public.get('publicURL') or public.get('publicUrl') or public.get('public_url')
            # fallback to stringified dict
            if not image_url:
                image_url = str(public)
        else:
            image_url = str(public)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase upload failed: {str(e)}")

    # --- Call your ML service here (optional) ---
    # For now, return a mock plate
    import random
    import string
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=4))
    plate = f"MH{letters}{numbers}"

    return {"plate": plate, "image_url": image_url}