"""
Wallet Manager Service Module
Manages wallet balances and transactions for Government, Reporters, and Platform.
"""

import sqlite3
from typing import Optional, Dict
from datetime import datetime
import logging

from payments.utils.db import get_db_connection, execute_query


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WalletManager:
    """
    Service class for wallet management.
    Handles wallet creation, credit, debit, and balance queries.
    """
    
    # Valid owner types
    OWNER_TYPES = ['GOVT', 'REPORTER', 'PLATFORM']
    
    # Special IDs for system entities
    GOVT_ID = 1
    PLATFORM_ID = 1
    
    def __init__(self, db_path: str = 'traffic_reward.db'):
        """
        Initialize wallet manager.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
    
    def get_or_create_wallet(self, owner_type: str, owner_id: int) -> Dict:
        """
        Retrieve or create a wallet for an entity.
        
        Args:
            owner_type: GOVT, REPORTER, or PLATFORM
            owner_id: Entity identifier
            
        Returns:
            Dictionary with wallet details:
            {
                "id": int,
                "owner_type": str,
                "owner_id": int,
                "balance": int
            }
            
        Raises:
            ValueError: If owner_type is invalid
            sqlite3.Error: If database operation fails
        """
        # Validate owner type
        if owner_type not in self.OWNER_TYPES:
            raise ValueError(f"Invalid owner_type. Must be one of: {self.OWNER_TYPES}")
        
        conn = None
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            # Try to fetch existing wallet
            cursor.execute(
                "SELECT id, owner_type, owner_id, balance FROM wallets WHERE owner_type = ? AND owner_id = ?",
                (owner_type, owner_id)
            )
            wallet = cursor.fetchone()
            
            if wallet:
                # Wallet exists
                return {
                    'id': wallet['id'],
                    'owner_type': wallet['owner_type'],
                    'owner_id': wallet['owner_id'],
                    'balance': wallet['balance']
                }
            else:
                # Create new wallet
                cursor.execute(
                    "INSERT INTO wallets (owner_type, owner_id, balance) VALUES (?, ?, 0)",
                    (owner_type, owner_id)
                )
                wallet_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"✓ Created new wallet - Type: {owner_type}, ID: {owner_id}")
                
                return {
                    'id': wallet_id,
                    'owner_type': owner_type,
                    'owner_id': owner_id,
                    'balance': 0
                }
        
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"✗ Database error in get_or_create_wallet: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def credit_wallet(self, owner_type: str, owner_id: int, amount: int) -> bool:
        """
        Credit amount to wallet atomically.
        
        Args:
            owner_type: GOVT, REPORTER, or PLATFORM
            owner_id: Entity identifier
            amount: Amount to credit in paisa
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If amount is not positive
            sqlite3.Error: If database operation fails
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("Credit amount must be positive")
        
        conn = None
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            # Ensure wallet exists
            self.get_or_create_wallet(owner_type, owner_id)
            
            # Update balance atomically
            cursor.execute(
                """
                UPDATE wallets 
                SET balance = balance + ?, 
                    updated_at = CURRENT_TIMESTAMP 
                WHERE owner_type = ? AND owner_id = ?
                """,
                (amount, owner_type, owner_id)
            )
            
            conn.commit()
            
            logger.info(
                f"✓ Credited wallet - Type: {owner_type}, ID: {owner_id}, "
                f"Amount: ₹{amount/100:.2f}"
            )
            
            return True
        
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"✗ Database error in credit_wallet: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def debit_wallet(self, owner_type: str, owner_id: int, amount: int) -> bool:
        """
        Debit amount from wallet if sufficient balance exists.
        
        Args:
            owner_type: GOVT, REPORTER, or PLATFORM
            owner_id: Entity identifier
            amount: Amount to debit in paisa
            
        Returns:
            True if successful, False if insufficient balance
            
        Raises:
            ValueError: If amount is not positive
            sqlite3.Error: If database operation fails
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("Debit amount must be positive")
        
        conn = None
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            # Check current balance
            current_balance = self.get_balance(owner_type, owner_id)
            
            if current_balance < amount:
                logger.warning(
                    f"✗ Insufficient balance - Type: {owner_type}, ID: {owner_id}, "
                    f"Required: ₹{amount/100:.2f}, Available: ₹{current_balance/100:.2f}"
                )
                return False
            
            # Update balance atomically
            cursor.execute(
                """
                UPDATE wallets 
                SET balance = balance - ?, 
                    updated_at = CURRENT_TIMESTAMP 
                WHERE owner_type = ? AND owner_id = ? AND balance >= ?
                """,
                (amount, owner_type, owner_id, amount)
            )
            
            # Check if update was successful
            if cursor.rowcount == 0:
                conn.rollback()
                logger.warning(f"✗ Debit failed - concurrent modification detected")
                return False
            
            conn.commit()
            
            logger.info(
                f"✓ Debited wallet - Type: {owner_type}, ID: {owner_id}, "
                f"Amount: ₹{amount/100:.2f}"
            )
            
            return True
        
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"✗ Database error in debit_wallet: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def get_balance(self, owner_type: str, owner_id: int) -> int:
        """
        Get current wallet balance.
        
        Args:
            owner_type: GOVT, REPORTER, or PLATFORM
            owner_id: Entity identifier
            
        Returns:
            Current balance in paisa
        """
        wallet = self.get_or_create_wallet(owner_type, owner_id)
        return wallet['balance']
    
    def get_wallet_details(self, owner_type: str, owner_id: int) -> Dict:
        """
        Get complete wallet details.
        
        Args:
            owner_type: GOVT, REPORTER, or PLATFORM
            owner_id: Entity identifier
            
        Returns:
            Dictionary with wallet details
        """
        return self.get_or_create_wallet(owner_type, owner_id)
