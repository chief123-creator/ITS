"""
Database Connection Utility Module
Provides database connection management and query execution helpers.
"""

import sqlite3
import os
from typing import Optional, List, Tuple, Any
from contextlib import contextmanager


# Default database path - always use root directory
# __file__ is in backend/payments/utils/db.py
# Go up 3 levels: utils -> payments -> backend -> root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEFAULT_DB_PATH = os.path.join(ROOT_DIR, 'traffic_reward.db')


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Creates and returns a database connection with proper configuration.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        sqlite3.Connection: Database connection object
        
    Raises:
        sqlite3.Error: If connection fails
    """
    try:
        conn = sqlite3.connect(db_path)
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        # Return rows as dictionaries
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Failed to connect to database: {e}")


@contextmanager
def get_db_cursor(db_path: str = DEFAULT_DB_PATH):
    """
    Context manager for database operations with automatic connection handling.
    
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM table")
            results = cursor.fetchall()
    
    Args:
        db_path: Path to the SQLite database file
        
    Yields:
        sqlite3.Cursor: Database cursor object
    """
    conn = None
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def execute_query(
    query: str,
    params: Optional[Tuple] = None,
    db_path: str = DEFAULT_DB_PATH,
    fetch_one: bool = False,
    fetch_all: bool = False
) -> Optional[Any]:
    """
    Execute a database query with automatic connection management.
    
    Args:
        query: SQL query string
        params: Query parameters tuple
        db_path: Path to the SQLite database file
        fetch_one: If True, return single row
        fetch_all: If True, return all rows
        
    Returns:
        Query results based on fetch parameters, or lastrowid for INSERT
        
    Raises:
        sqlite3.Error: If query execution fails
    """
    conn = None
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        
        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        else:
            # Return lastrowid for INSERT operations
            return cursor.lastrowid
            
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise sqlite3.Error(f"Query execution failed: {e}")
    finally:
        if conn:
            conn.close()


def execute_many(
    query: str,
    params_list: List[Tuple],
    db_path: str = DEFAULT_DB_PATH
) -> bool:
    """
    Execute multiple queries with the same SQL statement.
    
    Args:
        query: SQL query string
        params_list: List of parameter tuples
        db_path: Path to the SQLite database file
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        sqlite3.Error: If query execution fails
    """
    conn = None
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        return True
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise sqlite3.Error(f"Batch query execution failed: {e}")
    finally:
        if conn:
            conn.close()


def dict_from_row(row: sqlite3.Row) -> dict:
    """
    Convert sqlite3.Row object to dictionary.
    
    Args:
        row: sqlite3.Row object
        
    Returns:
        Dictionary representation of the row
    """
    if row is None:
        return None
    return dict(zip(row.keys(), row))
