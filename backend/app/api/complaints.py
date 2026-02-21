import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List, Optional
from datetime import datetime
from app import models, schemas
from app.api import deps
from app.database import get_db
from app.config import settings
from app.models.complaint import VehicleType, ActionType, ComplaintStatus
from app.models import vehicle

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.post("/", response_model=schemas.ComplaintOut)
async def create_complaint(
    video: UploadFile = File(...),
    vehicle_type: str = Form(...),
    action_type: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    recorded_at: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)  # Changed from get_current_verified_user
):
    # Validate enums
    try:
        v_type = VehicleType(vehicle_type)
        a_type = ActionType(action_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid vehicle type or action type")

    # Validate recorded_at
    try:
        rec_at = datetime.fromisoformat(recorded_at.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Invalid recorded_at format. Use ISO format.")

    # Validate file type
    if not video.content_type or not video.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    # Save video file
    if not video.filename:
        raise HTTPException(status_code=400, detail="File must have a filename")
    file_extension = os.path.splitext(video.filename)[1]
    filename = f"{uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
    finally:
        video.file.close()

    # Create complaint
    complaint = models.Complaint(
        user_id=current_user.id,
        video_url=filename,
        latitude=latitude,
        longitude=longitude,
        recorded_at=rec_at,
        vehicle_type=v_type,
        action_type=a_type,
        status=ComplaintStatus.PENDING
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    # Build full URL for response
    complaint_data = schemas.ComplaintOut.model_validate(complaint).model_dump()
    complaint_data["video_url"] = f"/uploads/{filename}"
    return schemas.ComplaintOut(**complaint_data)

@router.get("/", response_model=List[schemas.ComplaintOut])
def list_complaints(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)  # Changed
):
    query = db.query(models.Complaint).filter(models.Complaint.user_id == current_user.id)
    if status:
        try:
            status_enum = ComplaintStatus(status)
            query = query.filter(models.Complaint.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    complaints = query.order_by(models.Complaint.created_at.desc()).all()

    result = []
    for c in complaints:
        c_data = schemas.ComplaintOut.model_validate(c).model_dump()
        c_data["video_url"] = f"/uploads/{c.video_url}"
        result.append(schemas.ComplaintOut(**c_data))
    return result

@router.get("/{complaint_id}", response_model=schemas.ComplaintOut)
def get_complaint(
    complaint_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user)  # Changed
):
    complaint = db.query(models.Complaint).filter(
        models.Complaint.id == complaint_id,
        models.Complaint.user_id == current_user.id
    ).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    c_data = schemas.ComplaintOut.model_validate(complaint).model_dump()
    c_data["video_url"] = f"/uploads/{complaint.video_url}"
    return schemas.ComplaintOut(**c_data)

# Endpoint for ML to get pending complaints (no auth needed or could be open)
@router.get("/ml/pending", response_model=List[schemas.ComplaintOut])
def get_pending_complaints_for_ml(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    complaints = db.query(models.Complaint).filter(
        models.Complaint.status == ComplaintStatus.PENDING,
        models.Complaint.plate_number.is_(None)
    ).limit(limit).all()

    result = []
    for c in complaints:
        c_data = schemas.ComplaintOut.model_validate(c).model_dump()
        c_data["video_url"] = f"/uploads/{c.video_url}"
        result.append(schemas.ComplaintOut(**c_data))
    return result

# Endpoint for ML to update complaint with plate number (maybe no auth needed)
@router.patch("/{complaint_id}/ml-update", response_model=schemas.ComplaintOut)
def ml_update_complaint(
    complaint_id: str,
    update_data: schemas.ComplaintStatusUpdate,
    db: Session = Depends(get_db)
):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if update_data.plate_number is not None:
        setattr(complaint, 'plate_number', update_data.plate_number)
    if update_data.status is not None:
        try:
            setattr(complaint, 'status', ComplaintStatus(update_data.status))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")

    db.commit()
    db.refresh(complaint)
    c_data = schemas.ComplaintOut.model_validate(complaint).model_dump()
    c_data["video_url"] = f"/uploads/{complaint.video_url}"
    return schemas.ComplaintOut(**c_data)

# Endpoint to download video (for ML) – maybe no auth needed
@router.get("/{complaint_id}/video")
def download_video(
    complaint_id: str,
    db: Session = Depends(get_db)
):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    video_url = str(complaint.video_url)
    file_path = os.path.join(settings.UPLOAD_DIR, video_url)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    return FileResponse(file_path, media_type="video/mp4", filename=video_url)

@router.get("/owner", response_model=List[schemas.ComplaintOut])
def get_owner_complaints(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_verified_user)
):
    """Get all complaints where the current user is the vehicle owner."""
    # Note: owner_id field needs to be added to Complaint model if it doesn't exist
    complaints = db.query(models.Complaint).filter(
        models.Complaint.user_id == current_user.id
    ).order_by(models.Complaint.created_at.desc()).all()
    
    result = []
    for c in complaints:
        c_data = schemas.ComplaintOut.model_validate(c).model_dump()
        c_data["video_url"] = f"/uploads/{c.video_url}"
        proof_url_val = getattr(c, 'proof_url', None)
        if proof_url_val is not None:
            c_data["proof_url"] = f"/uploads/{proof_url_val}"
        result.append(schemas.ComplaintOut(**c_data))
    return result

@router.post("/{complaint_id}/owner-proof", response_model=schemas.ComplaintOut)
async def upload_owner_proof(
    complaint_id: str,
    proof: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_verified_user)
):
    """Owner uploads proof of vehicle removal. Resolves complaint and rewards reporter."""
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Verify that the current user is the reporter of this complaint
    # Using string comparison to avoid SQLAlchemy ColumnElement issues
    if str(complaint.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="You are not the reporter of this complaint")
    
    # Check if timer is still running (optional, you can allow upload even after timer expired but then fine might apply)
    # For simplicity, we allow upload regardless, and if timer expired, maybe still resolve? You decide.
    
    # Save proof file
    if not proof.filename:
        raise HTTPException(status_code=400, detail="Proof file must have a filename")
    
    file_extension = os.path.splitext(proof.filename)[1]
    filename = f"proof_{uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(proof.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save proof: {str(e)}")
    finally:
        proof.file.close()
    
    # Update complaint
    setattr(complaint, 'proof_url', filename)
    setattr(complaint, 'status', ComplaintStatus.RESOLVED)
    # Optionally clear fine if timer expired before upload? We'll just set resolved.
    
    # Reward the reporter (the user who filed the complaint)
    reporter = db.query(models.User).filter(models.User.id == complaint.user_id).first()
    if reporter:
        current_balance = reporter.wallet_balance if reporter.wallet_balance is not None else 0
        current_points = reporter.trust_points if reporter.trust_points is not None else 0
        setattr(reporter, 'wallet_balance', current_balance + 10)
        setattr(reporter, 'trust_points', current_points + 5)
        # You could also record transaction in a wallet_transactions table if needed
    
    db.commit()
    db.refresh(complaint)
    
    # Build response with full URLs
    c_data = schemas.ComplaintOut.model_validate(complaint).model_dump()
    c_data["video_url"] = f"/uploads/{complaint.video_url}"
    proof_url_val = getattr(complaint, 'proof_url', None)
    if proof_url_val is not None:
        c_data["proof_url"] = f"/uploads/{proof_url_val}"
    return schemas.ComplaintOut(**c_data)  