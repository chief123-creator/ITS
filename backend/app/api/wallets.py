"""
Wallet Routes
Handles wallet-related API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.wallet import WalletResponse, TransactionResponse
from app.services.wallet_service import WalletService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/wallets", tags=["wallets"])


@router.get("/balance", response_model=WalletResponse)
async def get_wallet_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's wallet balance"""
    try:
        wallet_service = WalletService(db)
        wallet = wallet_service.get_or_create_wallet('REPORTER', current_user.id)
        
        return WalletResponse(
            balance=wallet.balance,
            owner_type=wallet.owner_type,
            owner_id=wallet.owner_id
        )
    
    except Exception as e:
        logger.error(f"✗ Error fetching wallet balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch wallet balance"
        )


@router.get("/transactions", response_model=list[TransactionResponse])
async def get_wallet_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's transaction history"""
    try:
        transactions = db.query(Transaction).filter(
            Transaction.receiver_type == 'REPORTER',
            Transaction.receiver_id == current_user.id
        ).order_by(Transaction.created_at.desc()).all()
        
        result = []
        for txn in transactions:
            result.append(TransactionResponse(
                id=txn.id,
                amount=txn.amount,
                receiver_type=txn.receiver_type,
                created_at=txn.created_at,
                description=f"Payment reward from complaint"
            ))
        
        return result
    
    except Exception as e:
        logger.error(f"✗ Error fetching transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch transactions"
        )
