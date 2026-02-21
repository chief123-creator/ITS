"""
Withdrawal Routes
Handles withdrawal request API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.withdrawal import WithdrawalRequest
from app.schemas.withdrawal import WithdrawalCreate, WithdrawalResponse, WithdrawalListResponse
from app.services.wallet_service import WalletService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/withdrawals", tags=["withdrawals"])


@router.post("/", response_model=WithdrawalResponse)
async def create_withdrawal_request(
    request: WithdrawalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a withdrawal request"""
    try:
        # Check wallet balance
        wallet_service = WalletService(db)
        current_balance = wallet_service.get_balance('REPORTER', current_user.id)
        
        if current_balance < request.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Available: ₹{current_balance/100:.2f}, Requested: ₹{request.amount/100:.2f}"
            )
        
        # Create withdrawal request
        withdrawal = WithdrawalRequest(
            user_id=current_user.id,
            amount=request.amount,
            status='PENDING'
        )
        db.add(withdrawal)
        db.flush()
        
        # Debit amount from wallet
        success = wallet_service.debit_wallet('REPORTER', current_user.id, request.amount)
        
        if not success:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to deduct amount from wallet"
            )
        
        db.commit()
        db.refresh(withdrawal)
        
        logger.info(
            f"✓ Withdrawal request created - ID: {withdrawal.id}, "
            f"User: {current_user.id}, Amount: ₹{request.amount/100:.2f}"
        )
        
        return WithdrawalResponse(
            id=withdrawal.id,
            user_id=withdrawal.user_id,
            amount=withdrawal.amount,
            status=withdrawal.status,
            created_at=withdrawal.created_at
        )
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error creating withdrawal request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create withdrawal request"
        )


@router.get("/", response_model=WithdrawalListResponse)
async def get_user_withdrawals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's withdrawal requests"""
    try:
        withdrawals = db.query(WithdrawalRequest).filter(
            WithdrawalRequest.user_id == current_user.id
        ).order_by(WithdrawalRequest.created_at.desc()).all()
        
        withdrawal_list = [
            WithdrawalResponse(
                id=w.id,
                user_id=w.user_id,
                amount=w.amount,
                status=w.status,
                created_at=w.created_at
            )
            for w in withdrawals
        ]
        
        return WithdrawalListResponse(
            user_id=current_user.id,
            withdrawals=withdrawal_list
        )
    
    except Exception as e:
        logger.error(f"✗ Error fetching withdrawal requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch withdrawal requests"
        )


@router.post("/{withdrawal_id}/approve", response_model=WithdrawalResponse)
async def approve_withdrawal(
    withdrawal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a withdrawal request (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        withdrawal = db.query(WithdrawalRequest).filter(
            WithdrawalRequest.id == withdrawal_id
        ).first()
        
        if not withdrawal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Withdrawal request not found"
            )
        
        if withdrawal.status != 'PENDING':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Withdrawal request already {withdrawal.status}"
            )
        
        withdrawal.status = 'APPROVED'
        db.commit()
        db.refresh(withdrawal)
        
        logger.info(
            f"✓ Withdrawal request approved - ID: {withdrawal_id}, "
            f"User: {withdrawal.user_id}, Amount: ₹{withdrawal.amount/100:.2f}"
        )
        
        return WithdrawalResponse(
            id=withdrawal.id,
            user_id=withdrawal.user_id,
            amount=withdrawal.amount,
            status=withdrawal.status,
            created_at=withdrawal.created_at
        )
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error approving withdrawal request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve withdrawal request"
        )


@router.post("/{withdrawal_id}/reject", response_model=WithdrawalResponse)
async def reject_withdrawal(
    withdrawal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject a withdrawal request (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        withdrawal = db.query(WithdrawalRequest).filter(
            WithdrawalRequest.id == withdrawal_id
        ).first()
        
        if not withdrawal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Withdrawal request not found"
            )
        
        if withdrawal.status != 'PENDING':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Withdrawal request already {withdrawal.status}"
            )
        
        withdrawal.status = 'REJECTED'
        db.commit()
        
        # Refund amount back to wallet
        wallet_service = WalletService(db)
        wallet_service.credit_wallet('REPORTER', withdrawal.user_id, withdrawal.amount)
        
        db.refresh(withdrawal)
        
        logger.info(
            f"✓ Withdrawal request rejected - ID: {withdrawal_id}, "
            f"User: {withdrawal.user_id}, Amount refunded: ₹{withdrawal.amount/100:.2f}"
        )
        
        return WithdrawalResponse(
            id=withdrawal.id,
            user_id=withdrawal.user_id,
            amount=withdrawal.amount,
            status=withdrawal.status,
            created_at=withdrawal.created_at
        )
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error rejecting withdrawal request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject withdrawal request"
        )
