"""
Payment Methods Routes
Handles UPI and bank account management for withdrawals
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.payment_method import PaymentMethod
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/payment-methods", tags=["payment-methods"])


@router.post("/", response_model=PaymentMethodResponse)
async def add_payment_method(
    method: PaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new payment method (UPI or Bank Account)"""
    try:
        # Check for duplicate
        if method.method_type == 'UPI' and method.upi_id:
            existing = db.query(PaymentMethod).filter(
                PaymentMethod.user_id == current_user.id,
                PaymentMethod.upi_id == method.upi_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This UPI ID is already added"
                )
        
        elif method.method_type == 'BANK_ACCOUNT' and method.account_number:
            existing = db.query(PaymentMethod).filter(
                PaymentMethod.user_id == current_user.id,
                PaymentMethod.account_number == method.account_number
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This bank account is already added"
                )
        
        # Create payment method
        payment_method = PaymentMethod(
            user_id=current_user.id,
            method_type=method.method_type,
            upi_id=method.upi_id,
            account_holder_name=method.account_holder_name,
            account_number=method.account_number,
            ifsc_code=method.ifsc_code,
            bank_name=method.bank_name,
            is_primary=1 if method.is_primary else 0,
            is_verified=0
        )
        
        # If setting as primary, unset other primary methods
        if method.is_primary:
            db.query(PaymentMethod).filter(
                PaymentMethod.user_id == current_user.id
            ).update({'is_primary': 0})
        
        db.add(payment_method)
        db.commit()
        db.refresh(payment_method)
        
        logger.info(f"✓ Payment method added - User: {current_user.id}, Type: {method.method_type}")
        
        return PaymentMethodResponse(
            id=payment_method.id,
            method_type=payment_method.method_type,
            upi_id=payment_method.upi_id,
            account_holder_name=payment_method.account_holder_name,
            account_number='****' + payment_method.account_number[-4:] if payment_method.account_number else None,
            ifsc_code=payment_method.ifsc_code,
            bank_name=payment_method.bank_name,
            is_primary=bool(payment_method.is_primary),
            is_verified=bool(payment_method.is_verified),
            created_at=payment_method.created_at
        )
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error adding payment method: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add payment method"
        )


@router.get("/", response_model=list[PaymentMethodResponse])
async def get_payment_methods(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's payment methods"""
    try:
        methods = db.query(PaymentMethod).filter(
            PaymentMethod.user_id == current_user.id
        ).order_by(PaymentMethod.is_primary.desc(), PaymentMethod.created_at.desc()).all()
        
        result = []
        for method in methods:
            result.append(PaymentMethodResponse(
                id=method.id,
                method_type=method.method_type,
                upi_id=method.upi_id,
                account_holder_name=method.account_holder_name,
                account_number='****' + method.account_number[-4:] if method.account_number else None,
                ifsc_code=method.ifsc_code,
                bank_name=method.bank_name,
                is_primary=bool(method.is_primary),
                is_verified=bool(method.is_verified),
                created_at=method.created_at
            ))
        
        return result
    
    except Exception as e:
        logger.error(f"✗ Error fetching payment methods: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment methods"
        )


@router.delete("/{method_id}")
async def delete_payment_method(
    method_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a payment method"""
    try:
        method = db.query(PaymentMethod).filter(
            PaymentMethod.id == method_id,
            PaymentMethod.user_id == current_user.id
        ).first()
        
        if not method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        
        db.delete(method)
        db.commit()
        
        logger.info(f"✓ Payment method deleted - ID: {method_id}")
        
        return {"message": "Payment method deleted successfully"}
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error deleting payment method: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete payment method"
        )


@router.post("/{method_id}/set-primary")
async def set_primary_method(
    method_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set a payment method as primary"""
    try:
        method = db.query(PaymentMethod).filter(
            PaymentMethod.id == method_id,
            PaymentMethod.user_id == current_user.id
        ).first()
        
        if not method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
        
        # Unset all primary methods for this user
        db.query(PaymentMethod).filter(
            PaymentMethod.user_id == current_user.id
        ).update({'is_primary': 0})
        
        # Set this method as primary
        method.is_primary = 1
        db.commit()
        
        logger.info(f"✓ Primary payment method set - ID: {method_id}")
        
        return {"message": "Primary payment method updated successfully"}
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error setting primary method: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set primary method"
        )
