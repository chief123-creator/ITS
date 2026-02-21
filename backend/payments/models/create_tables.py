"""
Database Schema Creation Module
Creates all required tables for the Payment Module with proper constraints and relationships.
"""

import sqlite3
from typing import Optional


def create_tables(db_path: str = 'traffic_reward.db') -> bool:
    """
    Creates all database tables for the Payment Module.
    Tables are created with IF NOT EXISTS clause for idempotency.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Challans table (managed by main system, read-only for payment module)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS challans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                violation_report_id TEXT,
                vehicle_no TEXT NOT NULL,
                fine_amount INTEGER NOT NULL,
                reporter_id INTEGER NOT NULL,
                violation_type TEXT DEFAULT 'Traffic Violation',
                status TEXT NOT NULL DEFAULT 'UNPAID',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (status IN ('UNPAID', 'PAID'))
            )
        """)
        
        # 2. Payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challan_id INTEGER NOT NULL,
                razorpay_payment_id TEXT NOT NULL UNIQUE,
                razorpay_order_id TEXT NOT NULL,
                amount INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'SUCCESS',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (challan_id) REFERENCES challans(id)
            )
        """)
        
        # 3. Wallets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_type TEXT NOT NULL,
                owner_id INTEGER NOT NULL,
                balance INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(owner_type, owner_id),
                CHECK (owner_type IN ('GOVT', 'REPORTER', 'PLATFORM')),
                CHECK (balance >= 0)
            )
        """)
        
        # 4. Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payment_id INTEGER NOT NULL,
                receiver_type TEXT NOT NULL,
                receiver_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (payment_id) REFERENCES payments(id),
                CHECK (receiver_type IN ('GOVT', 'REPORTER', 'PLATFORM'))
            )
        """)
        
        # 5. Withdraw requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS withdraw_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED'))
            )
        """)
        
        # 6. Government sync logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS govt_sync_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challan_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'SYNCED',
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (challan_id) REFERENCES challans(id)
            )
        """)
        
        # 7. User payment methods table (UPI, Bank Account, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_payment_methods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                method_type TEXT NOT NULL,
                upi_id TEXT,
                account_holder_name TEXT,
                account_number TEXT,
                ifsc_code TEXT,
                bank_name TEXT,
                is_primary INTEGER DEFAULT 0,
                is_verified INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (method_type IN ('UPI', 'BANK_ACCOUNT', 'WALLET'))
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("✓ All database tables created successfully")
        return True
        
    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def initialize_database(db_path: str = 'traffic_reward.db') -> bool:
    """
    Initialize the database by creating all required tables.
    This function is idempotent and can be called multiple times safely.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        True if initialization successful, False otherwise
    """
    return create_tables(db_path)


if __name__ == '__main__':
    # Run table creation when executed directly
    initialize_database()
