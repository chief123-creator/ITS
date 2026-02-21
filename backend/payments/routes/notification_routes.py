"""
Notification Routes Module
Handles SMS notification endpoints
"""

from flask import request, jsonify
import logging

from payments import payments_bp
from payments.services.sms_service import get_sms_service
from payments.utils.db import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@payments_bp.route('/notifications/send-challan-sms', methods=['POST'])
def send_challan_sms():
    """
    Send challan notification SMS
    
    Request Body:
        {
            "challan_id": int,
            "phone": str (10 digits),
            "base_url": str (optional)
        }
    
    Response:
        {
            "success": bool,
            "message": str
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'challan_id' not in data or 'phone' not in data:
            return jsonify({
                'success': False,
                'error': 'challan_id and phone are required'
            }), 400
        
        challan_id = data['challan_id']
        phone = data['phone']
        base_url = data.get('base_url', 'trafficguard.com')
        
        # Fetch challan details
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, vehicle_no, fine_amount FROM challans WHERE id = ?",
            (challan_id,)
        )
        challan = cursor.fetchone()
        conn.close()
        
        if not challan:
            return jsonify({
                'success': False,
                'error': 'Challan not found'
            }), 404
        
        # Send SMS
        sms_service = get_sms_service()
        result = sms_service.send_challan_notification(
            phone=phone,
            challan_id=challan['id'],
            vehicle_no=challan['vehicle_no'],
            amount=challan['fine_amount'],
            base_url=base_url
        )
        
        if result['success']:
            logger.info(f"✓ Challan SMS sent - Challan: {challan_id}, Phone: {phone}")
            return jsonify({
                'success': True,
                'message': 'SMS sent successfully'
            }), 200
        else:
            logger.error(f"✗ SMS failed - Challan: {challan_id}, Error: {result.get('error')}")
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to send SMS')
            }), 500
    
    except Exception as e:
        logger.error(f"✗ Error sending challan SMS: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@payments_bp.route('/notifications/send-payment-success-sms', methods=['POST'])
def send_payment_success_sms():
    """
    Send payment success notification SMS
    
    Request Body:
        {
            "phone": str,
            "challan_id": int,
            "vehicle_no": str,
            "amount": int,
            "payment_id": str
        }
    
    Response:
        {
            "success": bool,
            "message": str
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['phone', 'challan_id', 'vehicle_no', 'amount', 'payment_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        # Send SMS
        sms_service = get_sms_service()
        result = sms_service.send_payment_success_notification(
            phone=data['phone'],
            challan_id=data['challan_id'],
            vehicle_no=data['vehicle_no'],
            amount=data['amount'],
            payment_id=data['payment_id']
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'SMS sent successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to send SMS')
            }), 500
    
    except Exception as e:
        logger.error(f"✗ Error sending payment success SMS: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@payments_bp.route('/notifications/send-reporter-reward-sms', methods=['POST'])
def send_reporter_reward_sms():
    """
    Send reward notification SMS to reporter
    
    Request Body:
        {
            "phone": str,
            "challan_id": int,
            "reward_amount": int
        }
    
    Response:
        {
            "success": bool,
            "message": str
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['phone', 'challan_id', 'reward_amount']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        # Send SMS
        sms_service = get_sms_service()
        result = sms_service.send_reporter_reward_notification(
            phone=data['phone'],
            challan_id=data['challan_id'],
            reward_amount=data['reward_amount']
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'SMS sent successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to send SMS')
            }), 500
    
    except Exception as e:
        logger.error(f"✗ Error sending reporter reward SMS: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@payments_bp.route('/notifications/send-withdrawal-status-sms', methods=['POST'])
def send_withdrawal_status_sms():
    """
    Send withdrawal status notification SMS
    
    Request Body:
        {
            "phone": str,
            "amount": int,
            "status": "approved" | "rejected",
            "upi_id": str (for approved),
            "reason": str (for rejected)
        }
    
    Response:
        {
            "success": bool,
            "message": str
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['phone', 'amount', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        status = data['status']
        sms_service = get_sms_service()
        
        if status == 'approved':
            if 'upi_id' not in data:
                return jsonify({
                    'success': False,
                    'error': 'upi_id is required for approved status'
                }), 400
            
            result = sms_service.send_withdrawal_approved_notification(
                phone=data['phone'],
                amount=data['amount'],
                upi_id=data['upi_id']
            )
        elif status == 'rejected':
            result = sms_service.send_withdrawal_rejected_notification(
                phone=data['phone'],
                amount=data['amount'],
                reason=data.get('reason', 'Verification failed')
            )
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid status. Must be "approved" or "rejected"'
            }), 400
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'SMS sent successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to send SMS')
            }), 500
    
    except Exception as e:
        logger.error(f"✗ Error sending withdrawal status SMS: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@payments_bp.route('/notifications/test-sms', methods=['POST'])
def test_sms():
    """
    Test SMS functionality
    
    Request Body:
        {
            "phone": str,
            "message": str
        }
    
    Response:
        {
            "success": bool,
            "message": str
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'phone' not in data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'phone and message are required'
            }), 400
        
        # Send test SMS
        sms_service = get_sms_service()
        result = sms_service.send_sms(
            phone=data['phone'],
            message=data['message']
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Test SMS sent successfully',
                'response': result.get('response')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to send SMS'),
                'response': result.get('response')
            }), 500
    
    except Exception as e:
        logger.error(f"✗ Error sending test SMS: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
