from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=schemas.UserOut)
def read_current_user(
    current_user: models.User = Depends(deps.get_current_verified_user)
):
    """Get current user profile."""
    return current_user

@router.put("/me", response_model=schemas.UserOut)
def update_current_user(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_verified_user)
):
    """Update current user profile."""
    # Update only provided fields
    if user_update.name is not None:
        current_user.name = user_update.name  # type: ignore
    if user_update.phone is not None:
        # Check if phone is already taken by another user
        existing = db.query(models.User).filter(
            models.User.phone == user_update.phone,
            models.User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Phone already registered")
        current_user.phone = user_update.phone  # type: ignore
    if user_update.email is not None:
        # Check if email is already taken by another user
        existing = db.query(models.User).filter(
            models.User.email == user_update.email,
            models.User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = user_update.email  # type: ignore

    db.commit()
    db.refresh(current_user)
    return current_user