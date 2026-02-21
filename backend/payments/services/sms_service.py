"""
SMS Service Module
Handles SMS notifications using Fast2SMS API
"""

import requests
import logging
import os
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS notifications via Fast2SMS"""
    
    def __init__(self):
        """Initialize SMS service with API credentials"""
        self.api_key = os.getenv('FAST2SMS_API_KEY', '')
        self.base_url = "https://www.fast2sms.com/dev/bulkV2"
        
        if not self.api_key:
            logger.warning("⚠️  Fast2SMS API key not configured")
    
    def send_sms(self, phone: str, message: str) -> Dict:
        """
        Send SMS to a phone number
        
        Args:
            phone: Phone number (10 digits, without +91)
            message: SMS message content
            
        Returns:
            Dict with success status and response
        """
        try:
            # Validate phone number
            phone = str(phone).strip()
            if phone.startswith('+91'):
                phone = phone[3:]
            if phone.startswith('91'):
                phone = phone[2:]
            
            if len(phone) != 10 or not phone.isdigit():
                return {
                    'success': False,
                    'error': 'Invalid phone number format'
                }
            
            # Prepare payload
            payload = {
                'authorization': self.api_key,
                'route': 'q',  # Quick SMS route
                'message': message,
                'language': 'english',
                'flash': 0,
                'numbers': phone
            }
            
            # Send SMS
            logger.info(f"📱 Sending SMS to {phone}")
            response = requests.post(self.base_url, data=payload, timeout=10)
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('return'):
                logger.info(f"✓ SMS sent successfully to {phone}")
                return {
                    'success': True,
                    'message': 'SMS sent successfully',
                    'response': response_data
                }
            else:
                logger.error(f"✗ SMS failed: {response_data}")
                return {
                    'success': False,
                    'error': response_data.get('message', 'Failed to send SMS'),
                    'response': response_data
                }
        
        except requests.exceptions.Timeout:
            logger.error("✗ SMS request timeout")
            return {
                'success': False,
                'error': 'SMS service timeout'
            }
        except Exception as e:
            logger.error(f"✗ SMS error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_challan_notification(
        self, 
        phone: str, 
        challan_id: int, 
        vehicle_no: str, 
        amount: int,
        base_url: str = "trafficguard.com"
    ) -> Dict:
        """
        Send challan payment notification SMS
        
        Args:
            phone: Phone number
            challan_id: Challan ID
            vehicle_no: Vehicle number
            amount: Fine amount in paisa
            base_url: Base URL for payment link
            
        Returns:
            Dict with success status
        """
        amount_rupees = amount / 100
        
        message = (
            f"Traffic Challan Alert!\n"
            f"Challan ID: {challan_id}\n"
            f"Vehicle: {vehicle_no}\n"
            f"Fine: Rs.{amount_rupees:.2f}\n"
            f"Pay: {base_url}/payment/{challan_id}\n"
            f"- TrafficGuard"
        )
        
        return self.send_sms(phone, message)
    
    def send_payment_success_notification(
        self,
        phone: str,
        challan_id: int,
        vehicle_no: str,
        amount: int,
        payment_id: str
    ) -> Dict:
        """
        Send payment success confirmation SMS
        
        Args:
            phone: Phone number
            challan_id: Challan ID
            vehicle_no: Vehicle number
            amount: Amount paid in paisa
            payment_id: Razorpay payment ID
            
        Returns:
            Dict with success status
        """
        amount_rupees = amount / 100
        
        message = (
            f"Payment Successful!\n"
            f"Challan: {challan_id}\n"
            f"Vehicle: {vehicle_no}\n"
            f"Amount: Rs.{amount_rupees:.2f}\n"
            f"Payment ID: {payment_id[:20]}\n"
            f"Thank you - TrafficGuard"
        )
        
        return self.send_sms(phone, message)
    
    def send_reporter_reward_notification(
        self,
        phone: str,
        challan_id: int,
        reward_amount: int
    ) -> Dict:
        """
        Send reward notification to reporter
        
        Args:
            phone: Reporter's phone number
            challan_id: Challan ID
            reward_amount: Reward amount in paisa
            
        Returns:
            Dict with success status
        """
        reward_rupees = reward_amount / 100
        
        message = (
            f"Reward Earned!\n"
            f"Challan #{challan_id} paid\n"
            f"Your Reward: Rs.{reward_rupees:.2f}\n"
            f"Check wallet for details\n"
            f"- TrafficGuard"
        )
        
        return self.send_sms(phone, message)
    
    def send_withdrawal_approved_notification(
        self,
        phone: str,
        amount: int,
        upi_id: str
    ) -> Dict:
        """
        Send withdrawal approval notification
        
        Args:
            phone: Reporter's phone number
            amount: Withdrawal amount in paisa
            upi_id: UPI ID for transfer
            
        Returns:
            Dict with success status
        """
        amount_rupees = amount / 100
        
        message = (
            f"Withdrawal Approved!\n"
            f"Amount: Rs.{amount_rupees:.2f}\n"
            f"UPI: {upi_id}\n"
            f"Processing within 24 hours\n"
            f"- TrafficGuard"
        )
        
        return self.send_sms(phone, message)
    
    def send_withdrawal_rejected_notification(
        self,
        phone: str,
        amount: int,
        reason: str = "Verification failed"
    ) -> Dict:
        """
        Send withdrawal rejection notification
        
        Args:
            phone: Reporter's phone number
            amount: Withdrawal amount in paisa
            reason: Rejection reason
            
        Returns:
            Dict with success status
        """
        amount_rupees = amount / 100
        
        message = (
            f"Withdrawal Rejected\n"
            f"Amount: Rs.{amount_rupees:.2f}\n"
            f"Reason: {reason}\n"
            f"Amount refunded to wallet\n"
            f"- TrafficGuard"
        )
        
        return self.send_sms(phone, message)


# Singleton instance
_sms_service = None

def get_sms_service() -> SMSService:
    """Get SMS service singleton instance"""
    global _sms_service
    if _sms_service is None:
        _sms_service = SMSService()
    return _sms_service
