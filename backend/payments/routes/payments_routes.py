"""
Payment Routes Module
Handles all payment-related API endpoints.
"""

from flask import request, jsonify
import sqlite3
import logging

from payments import payments_bp
from payments.utils.db import get_db_connection
from payments.utils.razorpay_config import get_razorpay_config
from payments.services.razorpay_service import RazorpayService
from payments.services.signature_service import SignatureVerifier
from payments.services.split_engine import SplitEngine
from payments.services.wallet_manager import WalletManager
from payments.services.transaction_logger import TransactionLogger
from payments.services.govt_sync_logger import GovtSyncLogger


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@payments_bp.route('/create-order', methods=['POST'])
def create_order():
    """
    Create a Razorpay order for challan payment.
    
    Request Body:
        {
            "challan_id": int
        }
    
    Response:
        {
            "order_id": str,
            "amount": int,
            "currency": str
        }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'challan_id' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'challan_id is required'
            }), 400
        
        challan_id = data['challan_id']
        
        # Validate challan_id
        if not isinstance(challan_id, int) or challan_id <= 0:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Invalid challan_id'
            }), 400
        
        # Fetch challan from database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, fine_amount, status FROM challans WHERE id = ?",
            (challan_id,)
        )
        challan = cursor.fetchone()
        conn.close()
        
        if not challan:
            return jsonify({
                'error': 'Not Found',
                'message': 'Challan not found'
            }), 404
        
        # Check if challan is already paid
        if challan['status'] == 'PAID':
            return jsonify({
                'error': 'Bad Request',
                'message': 'Challan is already paid'
            }), 400
        
        # Get fine amount (already in paisa from database)
        amount = challan['fine_amount']
        
        # Initialize Razorpay service
        config = get_razorpay_config()
        razorpay_service = RazorpayService(
            config.get_key_id(),
            config.get_key_secret()
        )
        
        # Create Razorpay order
        receipt = f"challan_{challan_id}"
        order = razorpay_service.create_order(
            amount=amount,
            currency='INR',
            receipt=receipt
        )
        
        logger.info(f"✓ Order created - Challan: {challan_id}, Order ID: {order['id']}")
        
        return jsonify({
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency']
        }), 200
    
    except ValueError as e:
        logger.error(f"✗ Validation error: {e}")
        return jsonify({
            'error': 'Bad Request',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"✗ Error creating order: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to create order'
        }), 500


@payments_bp.route('/payment-success', methods=['POST'])
def payment_success():
    """
    Handle successful payment callback from Razorpay.
    
    Request Body:
        {
            "razorpay_order_id": str,
            "razorpay_payment_id": str,
            "razorpay_signature": str,
            "challan_id": int,
            "reporter_id": int,
            "amount": int
        }
    
    Response:
        {
            "message": str,
            "payment_id": int
        }
    """
    conn = None
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'razorpay_order_id', 'razorpay_payment_id',
            'razorpay_signature', 'challan_id', 'amount'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': 'Bad Request',
                    'message': f'{field} is required'
                }), 400
        
        order_id = data['razorpay_order_id']
        payment_id = data['razorpay_payment_id']
        signature = data['razorpay_signature']
        challan_id = data['challan_id']
        amount = data['amount']
        
        # Fetch reporter_id from challan (auto-fetch)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT reporter_id FROM challans WHERE id = ?",
            (challan_id,)
        )
        challan_data = cursor.fetchone()
        
        if not challan_data:
            conn.close()
            return jsonify({
                'error': 'Not Found',
                'message': 'Challan not found'
            }), 404
        
        reporter_id = challan_data['reporter_id']
        conn.close()
        
        # Verify signature
        config = get_razorpay_config()
        is_valid = SignatureVerifier.verify_payment_signature(
            order_id=order_id,
            payment_id=payment_id,
            signature=signature,
            secret=config.get_key_secret()
        )
        
        if not is_valid:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Invalid signature'
            }), 400
        
        # Start database transaction
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check for duplicate payment
        cursor.execute(
            "SELECT id FROM payments WHERE razorpay_payment_id = ?",
            (payment_id,)
        )
        existing_payment = cursor.fetchone()
        
        if existing_payment:
            conn.close()
            return jsonify({
                'error': 'Bad Request',
                'message': 'Payment already processed'
            }), 400
        
        # Create payment record
        cursor.execute(
            """
            INSERT INTO payments (challan_id, razorpay_payment_id, razorpay_order_id, amount, status)
            VALUES (?, ?, ?, ?, 'SUCCESS')
            """,
            (challan_id, payment_id, order_id, amount)
        )
        payment_record_id = cursor.lastrowid
        
        # Update challan status to PAID
        cursor.execute(
            "UPDATE challans SET status = 'PAID' WHERE id = ?",
            (challan_id,)
        )
        
        conn.commit()
        
        logger.info(f"✓ Payment recorded - ID: {payment_record_id}, Challan: {challan_id}")
        
        # Calculate splits
        split_engine = SplitEngine()
        splits = split_engine.calculate_splits(amount)
        
        # Credit wallets
        wallet_manager = WalletManager()
        wallet_manager.credit_wallet('GOVT', WalletManager.GOVT_ID, splits['govt'])
        wallet_manager.credit_wallet('REPORTER', reporter_id, splits['reporter'])
        wallet_manager.credit_wallet('PLATFORM', WalletManager.PLATFORM_ID, splits['platform'])
        
        # Log transactions
        transaction_logger = TransactionLogger()
        transaction_logger.log_transaction(payment_record_id, 'GOVT', WalletManager.GOVT_ID, splits['govt'])
        transaction_logger.log_transaction(payment_record_id, 'REPORTER', reporter_id, splits['reporter'])
        transaction_logger.log_transaction(payment_record_id, 'PLATFORM', WalletManager.PLATFORM_ID, splits['platform'])
        
        # Log govt sync (non-blocking)
        govt_sync_logger = GovtSyncLogger()
        govt_sync_logger.log_govt_sync(challan_id, splits['govt'])
        
        logger.info(f"✓ Payment processing complete - Payment ID: {payment_record_id}")
        
        return jsonify({
            'message': 'Payment processed successfully',
            'payment_id': payment_record_id
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
        logger.error(f"✗ Error processing payment: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to process payment'
        }), 500
    finally:
        if conn:
            conn.close()


@payments_bp.route('/challan/payments/<int:challan_id>', methods=['GET'])
def get_challan_payment_history(challan_id):
    """
    Get payment history for a specific challan.
    
    Response:
        {
            "challan_id": int,
            "status": str,
            "payment": {...},
            "splits": {...}
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get challan
        cursor.execute(
            "SELECT id, vehicle_no, fine_amount, status FROM challans WHERE id = ?",
            (challan_id,)
        )
        challan = cursor.fetchone()
        
        if not challan:
            conn.close()
            return jsonify({
                'error': 'Not Found',
                'message': 'Challan not found'
            }), 404
        
        # Get payment if exists
        cursor.execute(
            """
            SELECT id, razorpay_payment_id, razorpay_order_id, amount, status, created_at
            FROM payments
            WHERE challan_id = ?
            """,
            (challan_id,)
        )
        payment = cursor.fetchone()
        
        response = {
            'challan_id': challan['id'],
            'vehicle_no': challan['vehicle_no'],
            'fine_amount': challan['fine_amount'],
            'status': challan['status']
        }
        
        if payment:
            # Calculate splits
            split_engine = SplitEngine()
            splits = split_engine.calculate_splits(payment['amount'])
            
            response['payment'] = {
                'id': payment['id'],
                'razorpay_payment_id': payment['razorpay_payment_id'],
                'razorpay_order_id': payment['razorpay_order_id'],
                'amount': payment['amount'],
                'status': payment['status'],
                'created_at': payment['created_at']
            }
            response['splits'] = splits
        else:
            response['payment'] = None
            response['splits'] = None
        
        conn.close()
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"✗ Error fetching challan payment history: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to fetch payment history'
        }), 500


@payments_bp.route('/reporter/payments/<int:reporter_id>', methods=['GET'])
def get_reporter_payment_history(reporter_id):
    """
    Get payment history for a specific reporter.
    
    Response:
        {
            "reporter_id": int,
            "total_earnings": int,
            "wallet_balance": int,
            "payments": [...],
            "withdrawals": [...]
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all payments for reporter
        cursor.execute(
            """
            SELECT p.id, p.challan_id, p.amount, p.created_at, c.vehicle_no
            FROM payments p
            JOIN challans c ON p.challan_id = c.id
            WHERE c.reporter_id = ?
            ORDER BY p.created_at DESC
            """,
            (reporter_id,)
        )
        payments = cursor.fetchall()
        
        # Calculate total earnings (5% of each payment)
        total_earnings = 0
        payment_list = []
        
        for payment in payments:
            reporter_share = int(payment['amount'] * 0.05)
            total_earnings += reporter_share
            
            payment_list.append({
                'payment_id': payment['id'],
                'challan_id': payment['challan_id'],
                'vehicle_no': payment['vehicle_no'],
                'total_amount': payment['amount'],
                'reporter_share': reporter_share,
                'created_at': payment['created_at']
            })
        
        # Get wallet balance
        wallet_manager = WalletManager()
        wallet_balance = wallet_manager.get_balance('REPORTER', reporter_id)
        
        # Get withdrawal history
        cursor.execute(
            """
            SELECT id, amount, status, created_at
            FROM withdraw_requests
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (reporter_id,)
        )
        withdrawals = cursor.fetchall()
        
        withdrawal_list = []
        for withdrawal in withdrawals:
            withdrawal_list.append({
                'id': withdrawal['id'],
                'amount': withdrawal['amount'],
                'status': withdrawal['status'],
                'created_at': withdrawal['created_at']
            })
        
        conn.close()
        
        return jsonify({
            'reporter_id': reporter_id,
            'total_earnings': total_earnings,
            'wallet_balance': wallet_balance,
            'payments': payment_list,
            'withdrawals': withdrawal_list
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Error fetching reporter payment history: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to fetch payment history'
        }), 500


@payments_bp.route('/admin/revenue', methods=['GET'])
def get_admin_revenue():
    """
    Get admin revenue statistics.
    
    Response:
        {
            "total_fines": int,
            "govt_revenue": int,
            "platform_earnings": int,
            "reporter_rewards": int
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total fines from payments
        cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE status = 'SUCCESS'"
        )
        result = cursor.fetchone()
        total_fines = result['total']
        
        # Get govt revenue from sync logs
        govt_sync_logger = GovtSyncLogger()
        govt_revenue = govt_sync_logger.get_total_govt_revenue()
        
        # Get platform earnings from wallet
        wallet_manager = WalletManager()
        platform_earnings = wallet_manager.get_balance('PLATFORM', WalletManager.PLATFORM_ID)
        
        # Calculate reporter rewards (5% of total fines)
        reporter_rewards = int(total_fines * 0.05)
        
        conn.close()
        
        return jsonify({
            'total_fines': total_fines,
            'govt_revenue': govt_revenue,
            'platform_earnings': platform_earnings,
            'reporter_rewards': reporter_rewards
        }), 200
    
    except Exception as e:
        logger.error(f"✗ Error fetching admin revenue: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to fetch revenue data'
        }), 500
