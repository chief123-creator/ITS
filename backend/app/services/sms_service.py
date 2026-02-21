"""
SMS Service
Handles SMS notifications using MSG91
"""
import requests
import logging
import os
import random

logger = logging.getLogger(__name__)


class SMSService:
    """SMS service for sending notifications"""
    
    def __init__(self):
        self.api_key = os.getenv("msg91_api_key")
        self.sender_id = os.getenv("msg91_sender_id", "TRAFIC")
        self.base_url = "https://api.msg91.com/api/v5/flow/"
        
        # Demo phone numbers for hackathon
        demo_numbers = os.getenv("demo_phone_numbers", "")
        self.demo_phones = [n.strip() for n in demo_numbers.split(",") if n.strip()]
        self.support_phone = os.getenv("support_phone", "8989563650")
        
    def get_random_demo_phone(self) -> str:
        """Get a random phone number from demo list"""
        if not self.demo_phones:
            logger.warning("No demo phone numbers configured")
            return None
        return random.choice(self.demo_phones)
    
    def send_challan_notification(
        self, 
        vehicle_number: str, 
        fine_amount: int,
        payment_link: str,
        complaint_id: str
    ) -> dict:
        """
        Send challan notification SMS to random demo number
        
        Args:
            vehicle_number: Vehicle registration number
            fine_amount: Fine amount in rupees
            payment_link: Payment link URL
            complaint_id: Complaint ID
            
        Returns:
            dict: {success: bool, phone: str, message: str}
        """
        try:
            # Get random phone number
            phone = self.get_random_demo_phone()
            
            if not phone:
                logger.error("No demo phone numbers available")
                return {"success": False, "phone": None, "message": "No phone configured"}
            
            # SMS message with 10 minute timer and support contact
            message = (
                f"🚨 TrafficGuard Alert!\n"
                f"Challan issued for vehicle {vehicle_number}\n"
                f"Fine Amount: Rs.{fine_amount}\n"
                f"\n"
                f"⏰ You have 10 MINUTES to:\n"
                f"1. Move your vehicle & submit proof\n"
                f"2. OR Pay the fine\n"
                f"\n"
                f"Pay now: {payment_link}\n"
                f"\n"
                f"📞 Customer Support: {self.support_phone}\n"
                f"Complaint ID: {complaint_id}"
            )
            
            logger.info(f"📱 SMS to {phone}:\n{message}")
            
            # For testing/demo, just log the message
            # Uncomment below for actual SMS sending with MSG91
            
            # if self.api_key:
            #     payload = {
            #         "sender": self.sender_id,
            #         "route": "4",
            #         "country": "91",
            #         "sms": [{
            #             "message": message,
            #             "to": [phone]
            #         }]
            #     }
            #     headers = {
            #         "authkey": self.api_key,
            #         "content-type": "application/json"
            #     }
            #     response = requests.post(
            #         f"{self.base_url}",
            #         json=payload,
            #         headers=headers
            #     )
            #     if response.status_code == 200:
            #         logger.info(f"✓ SMS sent successfully to {phone}")
            #         return {"success": True, "phone": phone, "message": message}
            
            return {"success": True, "phone": phone, "message": message}
            
        except Exception as e:
            logger.error(f"✗ Error sending SMS: {e}")
            return {"success": False, "phone": None, "message": str(e)}
