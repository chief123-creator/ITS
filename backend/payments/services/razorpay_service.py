"""
Razorpay Service Module
Handles integration with Razorpay payment gateway for order creation and payment processing.
"""

import razorpay
from typing import Dict, Optional


class RazorpayService:
    """
    Service class for Razorpay payment gateway integration.
    Handles order creation and payment processing.
    """
    
    def __init__(self, key_id: str, key_secret: str):
        """
        Initialize Razorpay service with credentials.
        
        Args:
            key_id: Razorpay KEY_ID
            key_secret: Razorpay KEY_SECRET
            
        Raises:
            ValueError: If credentials are invalid
        """
        if not key_id or not key_secret:
            raise ValueError("Razorpay credentials are required")
        
        self.key_id = key_id
        self.key_secret = key_secret
        
        # Initialize Razorpay client
        try:
            self.client = razorpay.Client(auth=(key_id, key_secret))
        except Exception as e:
            raise ValueError(f"Failed to initialize Razorpay client: {e}")
    
    def create_order(
        self,
        amount: int,
        currency: str = 'INR',
        receipt: Optional[str] = None
    ) -> Dict:
        """
        Create a Razorpay order for payment processing.
        
        Args:
            amount: Amount in paisa (smallest currency unit)
            currency: Currency code (default: INR)
            receipt: Unique receipt identifier (optional)
            
        Returns:
            Dictionary containing order details:
            {
                "id": order_id,
                "amount": amount,
                "currency": currency,
                "receipt": receipt,
                "status": "created"
            }
            
        Raises:
            ValueError: If amount is invalid
            Exception: If Razorpay API call fails
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("Amount must be positive and non-zero")
        
        # Prepare order data
        order_data = {
            'amount': amount,
            'currency': currency,
            'payment_capture': 1  # Auto-capture payment
        }
        
        if receipt:
            order_data['receipt'] = receipt
        
        try:
            # Create order via Razorpay API
            order = self.client.order.create(data=order_data)
            return order
        except razorpay.errors.BadRequestError as e:
            raise Exception(f"Razorpay bad request: {e}")
        except razorpay.errors.ServerError as e:
            raise Exception(f"Razorpay server error: {e}")
        except Exception as e:
            raise Exception(f"Failed to create Razorpay order: {e}")
    
    def convert_to_paisa(self, rupees: float) -> int:
        """
        Convert rupee amount to paisa (smallest currency unit).
        
        Args:
            rupees: Amount in rupees
            
        Returns:
            Amount in paisa (rupees * 100)
        """
        return int(rupees * 100)
    
    def convert_to_rupees(self, paisa: int) -> float:
        """
        Convert paisa amount to rupees.
        
        Args:
            paisa: Amount in paisa
            
        Returns:
            Amount in rupees (paisa / 100)
        """
        return paisa / 100
    
    def fetch_order(self, order_id: str) -> Dict:
        """
        Fetch order details from Razorpay.
        
        Args:
            order_id: Razorpay order ID
            
        Returns:
            Order details dictionary
            
        Raises:
            Exception: If order fetch fails
        """
        try:
            order = self.client.order.fetch(order_id)
            return order
        except Exception as e:
            raise Exception(f"Failed to fetch order: {e}")
    
    def fetch_payment(self, payment_id: str) -> Dict:
        """
        Fetch payment details from Razorpay.
        
        Args:
            payment_id: Razorpay payment ID
            
        Returns:
            Payment details dictionary
            
        Raises:
            Exception: If payment fetch fails
        """
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            raise Exception(f"Failed to fetch payment: {e}")
