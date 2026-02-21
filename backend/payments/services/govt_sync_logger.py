"""
Government Sync Logger Service Module
Logs government revenue for audit purposes (simulation).
"""

import sqlite3
from typing import Optional
from datetime import datetime
import logging

from payments.utils.db import get_db_connection


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GovtSyncLogger:
    """
    Service class for logging government revenue synchronization.
    Simulates govt revenue tracking for audit purposes.
    """
    
    def __init__(self, db_path: str = 'traffic_reward.db'):
        """
        Initialize govt sync logger.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
    
    def log_govt_sync(self, challan_id: int, amount: int) -> Optional[int]:
        """
        Log government revenue sync.
        
        This method is designed to not block payment processing if logging fails.
        Errors are logged but not raised.
        
        Args:
            challan_id: Challan ID
            amount: Government share amount in paisa
            
        Returns:
            Sync log record ID if successful, None if failed
        """
        # Validate parameters
        if challan_id <= 0:
            logger.warning(f"✗ Invalid challan_id for govt sync: {challan_id}")
            return None
        
        if amount <= 0:
            logger.warning(f"✗ Invalid amount for govt sync: {amount}")
            return None
        
        conn = None
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            # Insert govt sync log
            cursor.execute(
                """
                INSERT INTO govt_sync_logs (challan_id, amount, status)
                VALUES (?, ?, 'SYNCED')
                """,
                (challan_id, amount)
            )
            
            sync_id = cursor.lastrowid
            conn.commit()
            
            logger.info(
                f"✓ Govt sync logged - ID: {sync_id}, "
                f"Challan: {challan_id}, "
                f"Amount: ₹{amount/100:.2f}"
            )
            
            return sync_id
        
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            # Log error but don't raise - govt sync should not block payment processing
            logger.error(
                f"✗ Govt sync logging failed (non-blocking) - "
                f"Challan: {challan_id}, Error: {e}"
            )
            return None
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"✗ Unexpected error in govt sync logging: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def get_sync_logs_by_challan(self, challan_id: int) -> list:
        """
        Get all sync logs for a specific challan.
        
        Args:
            challan_id: Challan ID
            
        Returns:
            List of sync log dictionaries
        """
        conn = None
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT id, challan_id, amount, status, synced_at
                FROM govt_sync_logs
                WHERE challan_id = ?
                ORDER BY synced_at DESC
                """,
                (challan_id,)
            )
            
            rows = cursor.fetchall()
            
            logs = []
            for row in rows:
                logs.append({
                    'id': row['id'],
                    'challan_id': row['challan_id'],
                    'amount': row['amount'],
                    'status': row['status'],
                    'synced_at': row['synced_at']
                })
            
            return logs
        
        except sqlite3.Error as e:
            logger.error(f"✗ Database error in get_sync_logs_by_challan: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_total_govt_revenue(self) -> int:
        """
        Get total government revenue from all sync logs.
        
        Returns:
            Total government revenue in paisa
        """
        conn = None
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT COALESCE(SUM(amount), 0) as total
                FROM govt_sync_logs
                WHERE status = 'SYNCED'
                """
            )
            
            result = cursor.fetchone()
            total = result['total'] if result else 0
            
            return total
        
        except sqlite3.Error as e:
            logger.error(f"✗ Database error in get_total_govt_revenue: {e}")
            return 0
        finally:
            if conn:
                conn.close()
    
    def get_all_sync_logs(self, limit: Optional[int] = None) -> list:
        """
        Get all govt sync logs.
        
        Args:
            limit: Optional limit on number of records
            
        Returns:
            List of sync log dictionaries
        """
        conn = None
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT id, challan_id, amount, status, synced_at
                FROM govt_sync_logs
                ORDER BY synced_at DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            logs = []
            for row in rows:
                logs.append({
                    'id': row['id'],
                    'challan_id': row['challan_id'],
                    'amount': row['amount'],
                    'status': row['status'],
                    'synced_at': row['synced_at']
                })
            
            return logs
        
        except sqlite3.Error as e:
            logger.error(f"✗ Database error in get_all_sync_logs: {e}")
            return []
        finally:
            if conn:
                conn.close()
