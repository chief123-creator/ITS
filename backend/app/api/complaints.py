import os
import shutil
import logging
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
from app.services.sms_service import SMSService

router = APIRouter(prefix="/complaints", tags=["Complaints"])

# Initialize SMS service and logger
logger = logging.getLogger(__name__)
sms_service = SMSService()

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
    complaint_data = schemas.ComplaintOut.model_validate(complaint).__dict__
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
        c_data = schemas.ComplaintOut.model_validate(c).__dict__
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
    c_data = schemas.ComplaintOut.model_validate(complaint).__dict__
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
        c_data = schemas.ComplaintOut.model_validate(c).__dict__
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
        complaint.plate_number = str(update_data.plate_number)
    if update_data.status is not None:
        complaint.status = update_data.status

    db.commit()
    db.refresh(complaint)
    c_data = schemas.ComplaintOut.model_validate(complaint).__dict__
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


# Admin endpoint to update complaint (apply fine, resolve, etc.)
@router.put("/{complaint_id}", response_model=schemas.ComplaintOut)
def admin_update_complaint(
    complaint_id: str,
    update_data: schemas.ComplaintStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_admin)
):
    """
    Admin endpoint to update complaint status and apply fine.
    When status is changed to 'fine_applied', SMS is automatically sent.
    """
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Update fields
    if update_data.plate_number is not None:
        complaint.plate_number = str(update_data.plate_number)
    
    if update_data.status is not None:
        old_status = complaint.status
        complaint.status = update_data.status
        
        # If fine is being applied, send SMS notification
        if update_data.status == ComplaintStatus.FINE_APPLIED and old_status != ComplaintStatus.FINE_APPLIED:
            # Get fine amount from update or use default
            fine_amount = update_data.fine_amount if update_data.fine_amount else 500
            complaint.fine_amount = fine_amount
            
            # Generate payment link
            payment_link = f"{settings.FRONTEND_URL}/payment?complaint_id={complaint_id}"
            
            # Send SMS notification
            vehicle_number = complaint.plate_number or "UNKNOWN"
            sms_result = sms_service.send_challan_notification(
                vehicle_number=vehicle_number,
                fine_amount=int(fine_amount),
                payment_link=payment_link,
                complaint_id=complaint_id
            )
            
            logger.info(f"SMS notification result: {sms_result}")

    db.commit()
    db.refresh(complaint)
    
    c_data = schemas.ComplaintOut.model_validate(complaint).__dict__
    c_data["video_url"] = f"/uploads/{complaint.video_url}"
    return schemas.ComplaintOut(**c_data)
