"""
Payment Methods Routes Module
Handles UPI and bank account management for withdrawals.
"""

from flask import request, jsonify
import sqlite3
import logging
import re

from payments import payments_bp
from payments.utils.db import get_db_connection


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_upi_id(upi_id: str) -> bool:
    """
    Validate UPI ID format.
    Format: username@bankname
    """
    pattern = r'^[\w\.\-]+@[\w]+$'
    return bool(re.match(pattern, upi_id))


def validate_account_number(account_number: str) -> bool:
    """
    Validate bank account number (9-18 digits).
    """
    pattern = r'^\d{9,18}$'
    return bool(re.match(pattern, account_number))


def validate_ifsc_code(ifsc_code: str) -> bool:
    """
    Validate IFSC code format.
    Format: 4 letters + 7 digits (e.g., SBIN0001234)
    """
    pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
    return bool(re.match(pattern, ifsc_code.upper()))


@payments_bp.route('/payment-methods', methods=['POST'])
def add_payment_method():
    """
    Add a new payment method (UPI or Bank Account).
    
    Request Body:
        {
            "user_id": int,
            "method_type": "UPI" | "BANK_ACCOUNT",
            "upi_id": str (for UPI),
            "account_holder_name": str (for Bank),
            "account_number": str (for Bank),
            "ifsc_code": str (for Bank),
            "bank_name": str (for Bank),
            "is_primary": bool (optional)
        }
    """
    conn = None
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'user_id' not in data or 'method_type' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'user_id and method_type are required'
            }), 400
        
        user_id = data['user_id']
        method_type = data['method_type'].upper()
        is_primary = data.get('is_primary', False)
        
        # Validate method type
        if method_type not in ['UPI', 'BANK_ACCOUNT']:
            return jsonify({
                'error': 'Bad Request',
                'message': 'method_type must be UPI or BANK_ACCOUNT'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # If UPI
        if method_type == 'UPI':
            upi_id = data.get('upi_id', '').strip()
            
            if not upi_id:
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'upi_id is required for UPI method'
                }), 400
            
            # Validate UPI ID format
            if not validate_upi_id(upi_id):
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'Invalid UPI ID format. Use: username@bankname'
                }), 400
            
            # Check if UPI already exists
            cursor.execute(
                "SELECT id FROM user_payment_methods WHERE user_id = ? AND upi_id = ?",
                (user_id, upi_id)
            )
            if cursor.fetchone():
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'This UPI ID is already added'
                }), 400
            
            # Insert UPI method
            cursor.execute(
                """
                INSERT INTO user_payment_methods 
                (user_id, method_type, upi_id, is_primary, is_verified)
                VALUES (?, ?, ?, ?, 0)
                """,
                (user_id, method_type, upi_id, 1 if is_primary else 0)
            )
        
        # If Bank Account
        elif method_type == 'BANK_ACCOUNT':
            account_holder_name = data.get('account_holder_name', '').strip()
            account_number = data.get('account_number', '').strip()
            ifsc_code = data.get('ifsc_code', '').strip().upper()
            bank_name = data.get('bank_name', '').strip()
            
            # Validate required fields
            if not all([account_holder_name, account_number, ifsc_code, bank_name]):
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'account_holder_name, account_number, ifsc_code, and bank_name are required'
                }), 400
            
            # Validate formats
            if not validate_account_number(account_number):
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'Invalid account number format'
                }), 400
            
            if not validate_ifsc_code(ifsc_code):
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'Invalid IFSC code format'
                }), 400
            
            # Check if account already exists
            cursor.execute(
                "SELECT id FROM user_payment_methods WHERE user_id = ? AND account_number = ?",
                (user_id, account_number)
            )
            if cursor.fetchone():
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'This bank account is already added'
                }), 400
            
            # Insert bank account method
            cursor.execute(
                """
                INSERT INTO user_payment_methods 
                (user_id, method_type, account_holder_name, account_number, ifsc_code, bank_name, is_primary, is_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (user_id, method_type, account_holder_name, account_number, ifsc_code, bank_name, 1 if is_primary else 0)
            )
        
        # If setting as primary, unset other primary methods
        if is_primary:
            method_id = cursor.lastrowid
            cursor.execute(
                "UPDATE user_payment_methods SET is_primary = 0 WHERE user_id = ? AND id != ?",
                (user_id, method_id)
            )
        
        conn.commit()
        method_id = cursor.lastrowid
        
        logger.info(f"✓ Payment method added - User: {user_id}, Type: {method_type}, ID: {method_id}")
        
        return jsonify({
            'message': 'Payment method added successfully',
            'method_id': method_id
        }), 200
    
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"✗ Database error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Database operation failed'
        }), 500
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"✗ Error adding payment method: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to add payment method'
        }), 500
    finally:
        if conn:
            conn.close()


@payments_bp.route('/payment-methods/user/<int:user_id>', methods=['GET'])
def get_user_payment_methods(user_id):
    """
    Get all payment methods for a user.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, method_type, upi_id, account_holder_name, account_number, 
                   ifsc_code, bank_name, is_primary, is_verified, created_at
            FROM user_payment_methods
            WHERE user_id = ?
            ORDER BY is_primary DESC, created_at DESC
            """,
            (user_id,)
        )
        
        methods = cursor.fetchall()
        conn.close()
        
        method_list = []
        for method in methods:
            method_data = {
                'id': method['id'],
                'method_type': method['method_type'],
                'is_primary': bool(method['is_primary']),
                'is_verified': bool(method['is_verified']),
                'created_at': method['created_at']
            }
            
            if method['method_type'] == 'UPI':
                method_data['upi_id'] = method['upi_id']
            elif method['method_type'] == 'BANK_ACCOUNT':
                method_data['account_holder_name'] = method['account_holder_name']
                method_data['account_number'] = '****' + method['account_number'][-4:]  # Mask account number
                method_data['ifsc_code'] = method['ifsc_code']
                method_data['bank_name'] = method['bank_name']
            
            method_list.append(method_data)
        
        return jsonify({
            'user_id': user_id,
            'payment_methods': method_list
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Error fetching payment methods: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to fetch payment methods'
        }), 500


@payments_bp.route('/payment-methods/<int:method_id>', methods=['DELETE'])
def delete_payment_method(method_id):
    """
    Delete a payment method.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if method exists
        cursor.execute(
            "SELECT id FROM user_payment_methods WHERE id = ?",
            (method_id,)
        )
        if not cursor.fetchone():
            return jsonify({
                'error': 'Not Found',
                'message': 'Payment method not found'
            }), 404
        
        # Delete method
        cursor.execute(
            "DELETE FROM user_payment_methods WHERE id = ?",
            (method_id,)
        )
        conn.commit()
        
        logger.info(f"✓ Payment method deleted - ID: {method_id}")
        
        return jsonify({
            'message': 'Payment method deleted successfully'
        }), 200
    
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"✗ Database error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Database operation failed'
        }), 500
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"✗ Error deleting payment method: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to delete payment method'
        }), 500
    finally:
        if conn:
            conn.close()


@payments_bp.route('/payment-methods/<int:method_id>/set-primary', methods=['POST'])
def set_primary_payment_method(method_id):
    """
    Set a payment method as primary.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if method exists
        cursor.execute(
            "SELECT user_id FROM user_payment_methods WHERE id = ?",
            (method_id,)
        )
        result = cursor.fetchone()
        if not result:
            return jsonify({
                'error': 'Not Found',
                'message': 'Payment method not found'
            }), 404
        
        user_id = result['user_id']
        
        # Unset all primary methods for this user
        cursor.execute(
            "UPDATE user_payment_methods SET is_primary = 0 WHERE user_id = ?",
            (user_id,)
        )
        
        # Set this method as primary
        cursor.execute(
            "UPDATE user_payment_methods SET is_primary = 1 WHERE id = ?",
            (method_id,)
        )
        
        conn.commit()
        
        logger.info(f"✓ Primary payment method set - ID: {method_id}")
        
        return jsonify({
            'message': 'Primary payment method updated successfully'
        }), 200
    
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"✗ Database error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Database operation failed'
        }), 500
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"✗ Error setting primary method: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to set primary method'
        }), 500
    finally:
        if conn:
            conn.close()
