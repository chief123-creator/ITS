"""
Wallet Service
Manages wallet operations for Government, Reporters, and Platform
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.wallet import Wallet
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class WalletService:
    """Service for wallet management operations"""
    
    OWNER_TYPES = ['GOVT', 'REPORTER', 'PLATFORM']
    GOVT_ID = 'GOVT_1'
    PLATFORM_ID = 'PLATFORM_1'
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_wallet(self, owner_type: str, owner_id: str) -> Wallet:
        """Get or create wallet for an entity"""
        if owner_type not in self.OWNER_TYPES:
            raise ValueError(f"Invalid owner_type. Must be one of: {self.OWNER_TYPES}")
        
        try:
            wallet = self.db.query(Wallet).filter(
                Wallet.owner_type == owner_type,
                Wallet.owner_id == owner_id
            ).first()
            
            if wallet:
                return wallet
            
            # Create new wallet
            wallet = Wallet(
                owner_type=owner_type,
                owner_id=owner_id,
                balance=0
            )
            self.db.add(wallet)
            self.db.commit()
            self.db.refresh(wallet)
            
            logger.info(f"✓ Created new wallet - Type: {owner_type}, ID: {owner_id}")
            return wallet
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"✗ Database error in get_or_create_wallet: {e}")
            raise
    
    def credit_wallet(self, owner_type: str, owner_id: str, amount: int) -> bool:
        """Credit amount to wallet"""
        if amount <= 0:
            raise ValueError("Credit amount must be positive")
        
        try:
            wallet = self.get_or_create_wallet(owner_type, owner_id)
            wallet.balance += amount
            self.db.commit()
            
            logger.info(
                f"✓ Credited wallet - Type: {owner_type}, ID: {owner_id}, "
                f"Amount: ₹{amount/100:.2f}"
            )
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"✗ Database error in credit_wallet: {e}")
            raise
    
    def debit_wallet(self, owner_type: str, owner_id: str, amount: int) -> bool:
        """Debit amount from wallet if sufficient balance exists"""
        if amount <= 0:
            raise ValueError("Debit amount must be positive")
        
        try:
            wallet = self.get_or_create_wallet(owner_type, owner_id)
            
            if wallet.balance < amount:
                logger.warning(
                    f"✗ Insufficient balance - Type: {owner_type}, ID: {owner_id}, "
                    f"Required: ₹{amount/100:.2f}, Available: ₹{wallet.balance/100:.2f}"
                )
                return False
            
            wallet.balance -= amount
            self.db.commit()
            
            logger.info(
                f"✓ Debited wallet - Type: {owner_type}, ID: {owner_id}, "
                f"Amount: ₹{amount/100:.2f}"
            )
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"✗ Database error in debit_wallet: {e}")
            raise
    
    def get_balance(self, owner_type: str, owner_id: str) -> int:
        """Get current wallet balance"""
        wallet = self.get_or_create_wallet(owner_type, owner_id)
        return wallet.balance
    
    def get_wallet_details(self, owner_type: str, owner_id: str) -> Dict:
        """Get complete wallet details"""
        wallet = self.get_or_create_wallet(owner_type, owner_id)
        return {
            'id': wallet.id,
            'owner_type': wallet.owner_type,
            'owner_id': wallet.owner_id,
            'balance': wallet.balance
        }
