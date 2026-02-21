"""
Withdrawal Routes Module
Handles withdrawal request API endpoints.
"""

from flask import request, jsonify
import sqlite3
import logging

from payments import payments_bp
from payments.utils.db import get_db_connection
from payments.services.wallet_manager import WalletManager


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@payments_bp.route('/withdraw', methods=['POST'])
def create_withdrawal_request():
    """
    Create a withdrawal request for a reporter.
    
    Request Body:
        {
            "user_id": int,
            "amount": int
        }
    
    Response:
        {
            "message": str,
            "request_id": int,
            "status": str
        }
    """
    conn = None
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        if not data or 'user_id' not in data or 'amount' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'user_id and amount are required'
            }), 400
        
        user_id = data['user_id']
        amount = data['amount']
        
        # Validate inputs
        if not isinstance(user_id, int) or user_id <= 0:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Invalid user_id'
            }), 400
        
        if not isinstance(amount, int) or amount <= 0:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Amount must be positive'
            }), 400
        
        # Check wallet balance
        wallet_manager = WalletManager()
        current_balance = wallet_manager.get_balance('REPORTER', user_id)
        
        if current_balance < amount:
            return jsonify({
                'error': 'Bad Request',
                'message': f'Insufficient balance. Available: ₹{current_balance/100:.2f}, Requested: ₹{amount/100:.2f}'
            }), 400
        
        # Start database transaction
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create withdrawal request
        cursor.execute(
            """
            INSERT INTO withdraw_requests (user_id, amount, status)
            VALUES (?, ?, 'PENDING')
            """,
            (user_id, amount)
        )
        request_id = cursor.lastrowid
        
        conn.commit()
        
        # Deduct amount from wallet
        success = wallet_manager.debit_wallet('REPORTER', user_id, amount)
        
        if not success:
            # Rollback withdrawal request if debit fails
            cursor.execute(
                "DELETE FROM withdraw_requests WHERE id = ?",
                (request_id,)
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                'error': 'Bad Request',
                'message': 'Failed to deduct amount from wallet'
            }), 400
        
        conn.close()
        
        logger.info(
            f"✓ Withdrawal request created - ID: {request_id}, "
            f"User: {user_id}, Amount: ₹{amount/100:.2f}"
        )
        
        return jsonify({
            'message': 'Withdrawal request created successfully',
            'request_id': request_id,
            'status': 'PENDING'
        }), 200
    
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
            conn.close()
        logger.error(f"✗ Database error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Database operation failed'
        }), 500
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        logger.error(f"✗ Error creating withdrawal request: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to create withdrawal request'
        }), 500
    finally:
        if conn:
            conn.close()


@payments_bp.route('/withdraw/<int:request_id>', methods=['GET'])
def get_withdrawal_request(request_id):
    """
    Get details of a specific withdrawal request.
    
    Response:
        {
            "id": int,
            "user_id": int,
            "amount": int,
            "status": str,
            "created_at": str
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, user_id, amount, status, created_at
            FROM withdraw_requests
            WHERE id = ?
            """,
            (request_id,)
        )
        
        withdrawal = cursor.fetchone()
        conn.close()
        
        if not withdrawal:
            return jsonify({
                'error': 'Not Found',
                'message': 'Withdrawal request not found'
            }), 404
        
        return jsonify({
            'id': withdrawal['id'],
            'user_id': withdrawal['user_id'],
            'amount': withdrawal['amount'],
            'status': withdrawal['status'],
            'created_at': withdrawal['created_at']
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Error fetching withdrawal request: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to fetch withdrawal request'
        }), 500


@payments_bp.route('/withdraw/user/<int:user_id>', methods=['GET'])
def get_user_withdrawal_requests(user_id):
    """
    Get all withdrawal requests for a specific user.
    
    Response:
        {
            "user_id": int,
            "withdrawals": [...]
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, user_id, amount, status, created_at
            FROM withdraw_requests
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        )
        
        withdrawals = cursor.fetchall()
        conn.close()
        
        withdrawal_list = []
        for withdrawal in withdrawals:
            withdrawal_list.append({
                'id': withdrawal['id'],
                'user_id': withdrawal['user_id'],
                'amount': withdrawal['amount'],
                'status': withdrawal['status'],
                'created_at': withdrawal['created_at']
            })
        
        return jsonify({
            'user_id': user_id,
            'withdrawals': withdrawal_list
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Error fetching user withdrawal requests: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to fetch withdrawal requests'
        }), 500


@payments_bp.route('/withdraw/<int:request_id>/approve', methods=['POST'])
def approve_withdrawal_request(request_id):
    """
    Approve a withdrawal request (Admin only).
    
    Response:
        {
            "message": str,
            "request_id": int,
            "status": str
        }
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if withdrawal request exists
        cursor.execute(
            "SELECT id, user_id, amount, status FROM withdraw_requests WHERE id = ?",
            (request_id,)
        )
        withdrawal = cursor.fetchone()
        
        if not withdrawal:
            conn.close()
            return jsonify({
                'error': 'Not Found',
                'message': 'Withdrawal request not found'
            }), 404
        
        # Check if already processed
        if withdrawal['status'] != 'PENDING':
            conn.close()
            return jsonify({
                'error': 'Bad Request',
                'message': f'Withdrawal request already {withdrawal["status"]}'
            }), 400
        
        # Update status to APPROVED
        cursor.execute(
            "UPDATE withdraw_requests SET status = 'APPROVED' WHERE id = ?",
            (request_id,)
        )
        conn.commit()
        conn.close()
        
        logger.info(
            f"✓ Withdrawal request approved - ID: {request_id}, "
            f"User: {withdrawal['user_id']}, Amount: ₹{withdrawal['amount']/100:.2f}"
        )
        
        return jsonify({
            'message': 'Withdrawal request approved successfully',
            'request_id': request_id,
            'status': 'APPROVED'
        }), 200
    
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
            conn.close()
        logger.error(f"✗ Database error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Database operation failed'
        }), 500
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        logger.error(f"✗ Error approving withdrawal request: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to approve withdrawal request'
        }), 500


@payments_bp.route('/withdraw/<int:request_id>/reject', methods=['POST'])
def reject_withdrawal_request(request_id):
    """
    Reject a withdrawal request and refund amount to wallet (Admin only).
    
    Response:
        {
            "message": str,
            "request_id": int,
            "status": str
        }
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if withdrawal request exists
        cursor.execute(
            "SELECT id, user_id, amount, status FROM withdraw_requests WHERE id = ?",
            (request_id,)
        )
        withdrawal = cursor.fetchone()
        
        if not withdrawal:
            conn.close()
            return jsonify({
                'error': 'Not Found',
                'message': 'Withdrawal request not found'
            }), 404
        
        # Check if already processed
        if withdrawal['status'] != 'PENDING':
            conn.close()
            return jsonify({
                'error': 'Bad Request',
                'message': f'Withdrawal request already {withdrawal["status"]}'
            }), 400
        
        # Update status to REJECTED
        cursor.execute(
            "UPDATE withdraw_requests SET status = 'REJECTED' WHERE id = ?",
            (request_id,)
        )
        conn.commit()
        conn.close()
        
        # Refund amount back to wallet
        wallet_manager = WalletManager()
        wallet_manager.credit_wallet('REPORTER', withdrawal['user_id'], withdrawal['amount'])
        
        logger.info(
            f"✓ Withdrawal request rejected - ID: {request_id}, "
            f"User: {withdrawal['user_id']}, Amount refunded: ₹{withdrawal['amount']/100:.2f}"
        )
        
        return jsonify({
            'message': 'Withdrawal request rejected and amount refunded',
            'request_id': request_id,
            'status': 'REJECTED'
        }), 200
    
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
            conn.close()
        logger.error(f"✗ Database error: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Database operation failed'
        }), 500
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        logger.error(f"✗ Error rejecting withdrawal request: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to reject withdrawal request'
        }), 500


@payments_bp.route('/withdraw/all', methods=['GET'])
def get_all_withdrawal_requests():
    """
    Get all withdrawal requests (Admin only).
    Supports filtering by status.
    
    Query Parameters:
        status: PENDING, APPROVED, REJECTED (optional)
    
    Response:
        {
            "withdrawals": [...]
        }
    """
    try:
        # Get status filter from query params
        status_filter = request.args.get('status', None)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if status_filter:
            cursor.execute(
                """
                SELECT id, user_id, amount, status, created_at
                FROM withdraw_requests
                WHERE status = ?
                ORDER BY created_at DESC
                """,
                (status_filter.upper(),)
            )
        else:
            cursor.execute(
                """
                SELECT id, user_id, amount, status, created_at
                FROM withdraw_requests
                ORDER BY created_at DESC
                """
            )
        
        withdrawals = cursor.fetchall()
        conn.close()
        
        withdrawal_list = []
        for withdrawal in withdrawals:
            withdrawal_list.append({
                'id': withdrawal['id'],
                'user_id': withdrawal['user_id'],
                'amount': withdrawal['amount'],
                'status': withdrawal['status'],
                'created_at': withdrawal['created_at']
            })
        
        return jsonify({
            'withdrawals': withdrawal_list,
            'count': len(withdrawal_list)
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Error fetching all withdrawal requests: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to fetch withdrawal requests'
        }), 500
