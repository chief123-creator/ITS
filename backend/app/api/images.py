import uuid
from typing import Any, Dict

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.supabase_client import get_supabase
from app.config import settings
# ImageDetection model import deferred inside the route to avoid import errors if
# the model is not yet implemented.

router = APIRouter(prefix="/images", tags=["Images"])


@router.post("/upload")
async def upload_image(image: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload an image to Supabase and return a generated id and public URL.

    This endpoint does not depend on a database model. If you need to persist
    detection records, implement that in a separate service and DB model.
    """
    content_type = image.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    original_name = (image.filename or "").strip()
    if "." in original_name:
        ext = original_name.split('.')[-1]
    else:
        ext = "jpg"

    filename = f"{uuid.uuid4().hex}.{ext}"

    try:
        image_bytes = await image.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read uploaded file: {e}")

    supabase = get_supabase()
    try:
        storage = supabase.storage
        storage.from_(settings.SUPABASE_BUCKET).upload(f"uploads/{filename}", image_bytes)
        public = storage.from_(settings.SUPABASE_BUCKET).get_public_url(f"uploads/{filename}")
        if isinstance(public, dict):
            image_url = public.get('publicURL') or public.get('publicUrl') or public.get('public_url') or str(public)
        else:
            image_url = str(public)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase upload failed: {e}")

    generated_id = uuid.uuid4().hex
    return {"id": generated_id, "image_url": image_url}


@router.get("/{image_id}")
def get_detection(image_id: str):
    raise HTTPException(status_code=501, detail="Image detection lookup not implemented. Persist detection records to enable this endpoint.")


@router.patch("/{image_id}")
class PlateUpdate(BaseModel):
    plate: str


def update_detection(image_id: str, update: PlateUpdate, db: Session = Depends(get_db)):
    try:
        from app.models.image_detection import ImageDetection
    except Exception:
        # If the model isn't implemented, return 501 to indicate the feature
        # isn't available yet rather than raising an import error.
        raise HTTPException(status_code=501, detail="ImageDetection model not implemented")

    detection = db.query(ImageDetection).filter(ImageDetection.id == image_id).first()
    if not detection:
        raise HTTPException(status_code=404, detail="Not found")
    detection.plate = update.plate
    detection.status = 'completed'
    db.commit()
    return {"status": "updated"}