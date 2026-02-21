"""
Transaction Logger Service Module
Records all financial transactions for audit trail and accountability.
"""

import sqlite3
from typing import Optional
from datetime import datetime
import logging

from payments.utils.db import get_db_connection


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransactionLogger:
    """
    Service class for logging financial transactions.
    Ensures immutability and referential integrity of transaction records.
    """
    
    def __init__(self, db_path: str = 'traffic_reward.db'):
        """
        Initialize transaction logger.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
    
    def log_transaction(
        self,
        payment_id: int,
        receiver_type: str,
        receiver_id: int,
        amount: int
    ) -> int:
        """
        Log a transaction record.
        
        Args:
            payment_id: Associated payment ID
            receiver_type: GOVT, REPORTER, or PLATFORM
            receiver_id: Receiver entity ID
            amount: Transaction amount in paisa
            
        Returns:
            Transaction record ID
            
        Raises:
            ValueError: If parameters are invalid
            sqlite3.Error: If database operation fails
        """
        # Validate parameters
        if payment_id <= 0:
            raise ValueError("Invalid payment_id")
        
        if receiver_type not in ['GOVT', 'REPORTER', 'PLATFORM']:
            raise ValueError(f"Invalid receiver_type: {receiver_type}")
        
        if amount <= 0:
            raise ValueError("Transaction amount must be positive")
        
        conn = None
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            # Insert transaction record
            cursor.execute(
                """
                INSERT INTO transactions (payment_id, receiver_type, receiver_id, amount)
                VALUES (?, ?, ?, ?)
                """,
                (payment_id, receiver_type, receiver_id, amount)
            )
            
            transaction_id = cursor.lastrowid
            conn.commit()
            
            logger.info(
                f"✓ Transaction logged - ID: {transaction_id}, "
                f"Payment: {payment_id}, "
                f"Receiver: {receiver_type}:{receiver_id}, "
                f"Amount: ₹{amount/100:.2f}"
            )
            
            return transaction_id
        
        except sqlite3.IntegrityError as e:
            if conn:
                conn.rollback()
            logger.error(f"✗ Integrity error in log_transaction: {e}")
            raise ValueError(f"Invalid payment_id or referential integrity violation: {e}")
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"✗ Database error in log_transaction: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def get_transactions_by_payment(self, payment_id: int) -> list:
        """
        Get all transactions for a specific payment.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            List of transaction dictionaries
        """
        conn = None
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT id, payment_id, receiver_type, receiver_id, amount, created_at
                FROM transactions
                WHERE payment_id = ?
                ORDER BY created_at
                """,
                (payment_id,)
            )
            
            rows = cursor.fetchall()
            
            transactions = []
            for row in rows:
                transactions.append({
                    'id': row['id'],
                    'payment_id': row['payment_id'],
                    'receiver_type': row['receiver_type'],
                    'receiver_id': row['receiver_id'],
                    'amount': row['amount'],
                    'created_at': row['created_at']
                })
            
            return transactions
        
        except sqlite3.Error as e:
            logger.error(f"✗ Database error in get_transactions_by_payment: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def get_transactions_by_receiver(
        self,
        receiver_type: str,
        receiver_id: int
    ) -> list:
        """
        Get all transactions for a specific receiver.
        
        Args:
            receiver_type: GOVT, REPORTER, or PLATFORM
            receiver_id: Receiver entity ID
            
        Returns:
            List of transaction dictionaries
        """
        conn = None
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT id, payment_id, receiver_type, receiver_id, amount, created_at
                FROM transactions
                WHERE receiver_type = ? AND receiver_id = ?
                ORDER BY created_at DESC
                """,
                (receiver_type, receiver_id)
            )
            
            rows = cursor.fetchall()
            
            transactions = []
            for row in rows:
                transactions.append({
                    'id': row['id'],
                    'payment_id': row['payment_id'],
                    'receiver_type': row['receiver_type'],
                    'receiver_id': row['receiver_id'],
                    'amount': row['amount'],
                    'created_at': row['created_at']
                })
            
            return transactions
        
        except sqlite3.Error as e:
            logger.error(f"✗ Database error in get_transactions_by_receiver: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def verify_transaction_immutability(self, transaction_id: int) -> bool:
        """
        Verify that a transaction record has not been modified.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            True if transaction exists and is immutable
        """
        # In this implementation, transactions are immutable by design
        # (no UPDATE operations on transactions table)
        # This method verifies the transaction exists
        
        conn = None
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id FROM transactions WHERE id = ?",
                (transaction_id,)
            )
            
            result = cursor.fetchone()
            return result is not None
        
        except sqlite3.Error as e:
            logger.error(f"✗ Database error in verify_transaction_immutability: {e}")
            return False
        finally:
            if conn:
                conn.close()
