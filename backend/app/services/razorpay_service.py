"""
Razorpay Service
Handles Razorpay payment gateway integration
"""
import razorpay
from typing import Dict, Optional
import hmac
import hashlib


class RazorpayService:
    """Service for Razorpay payment gateway operations"""
    
    def __init__(self, key_id: str, key_secret: str):
        if not key_id or not key_secret:
            raise ValueError("Razorpay credentials are required")
        
        self.key_id = key_id
        self.key_secret = key_secret
        self.client = razorpay.Client(auth=(key_id, key_secret))
    
    def create_order(
        self,
        amount: int,
        currency: str = 'INR',
        receipt: Optional[str] = None
    ) -> Dict:
        """Create a Razorpay order"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        order_data = {
            'amount': amount,
            'currency': currency,
            'payment_capture': 1
        }
        
        if receipt:
            order_data['receipt'] = receipt
        
        try:
            order = self.client.order.create(data=order_data)
            return order
        except Exception as e:
            raise Exception(f"Failed to create Razorpay order: {e}")
    
    def verify_signature(
        self,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> bool:
        """Verify Razorpay payment signature"""
        try:
            message = f"{order_id}|{payment_id}"
            generated_signature = hmac.new(
                self.key_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(generated_signature, signature)
        except Exception:
            return False
    
    def convert_to_paisa(self, rupees: float) -> int:
        """Convert rupees to paisa"""
        return int(rupees * 100)
    
    def convert_to_rupees(self, paisa: int) -> float:
        """Convert paisa to rupees"""
        return paisa / 100
