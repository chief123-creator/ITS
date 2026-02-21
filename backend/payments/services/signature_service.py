"""
Signature Verification Service Module
Verifies Razorpay payment signatures to prevent fraudulent transactions.
"""

import hmac
import hashlib
import logging
from typing import Optional
from datetime import datetime


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignatureVerifier:
    """
    Service class for verifying Razorpay payment signatures.
    Uses HMAC SHA256 for signature validation.
    """
    
    @staticmethod
    def verify_payment_signature(
        order_id: str,
        payment_id: str,
        signature: str,
        secret: str
    ) -> bool:
        """
        Verify Razorpay payment signature using HMAC SHA256.
        
        Algorithm:
            1. Create message: order_id + "|" + payment_id
            2. Generate HMAC SHA256 signature using secret key
            3. Compare generated signature with received signature
        
        Args:
            order_id: Razorpay order ID
            payment_id: Razorpay payment ID
            signature: Signature from Razorpay callback
            secret: Razorpay key secret
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Create the message to sign
            message = f"{order_id}|{payment_id}"
            
            # Generate signature using HMAC SHA256
            generated_signature = hmac.new(
                key=secret.encode('utf-8'),
                msg=message.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            # Compare signatures (constant-time comparison)
            is_valid = hmac.compare_digest(generated_signature, signature)
            
            if is_valid:
                logger.info(f"✓ Signature verified successfully for order: {order_id}")
            else:
                logger.warning(f"✗ Signature verification failed for order: {order_id}")
                SignatureVerifier._log_failed_verification(order_id, payment_id)
            
            return is_valid
            
        except Exception as e:
            logger.error(f"✗ Signature verification error: {e}")
            SignatureVerifier._log_failed_verification(order_id, payment_id, str(e))
            return False
    
    @staticmethod
    def _log_failed_verification(
        order_id: str,
        payment_id: str,
        error: Optional[str] = None
    ) -> None:
        """
        Log failed signature verification attempts for security audit.
        
        Args:
            order_id: Razorpay order ID
            payment_id: Razorpay payment ID
            error: Optional error message
        """
        timestamp = datetime.now().isoformat()
        log_message = (
            f"[SECURITY AUDIT] Failed signature verification - "
            f"Timestamp: {timestamp}, "
            f"Order ID: {order_id}, "
            f"Payment ID: {payment_id}"
        )
        
        if error:
            log_message += f", Error: {error}"
        
        logger.warning(log_message)
        
        # In production, this should also write to a dedicated security audit log file
        # or send alerts to monitoring systems
    
    @staticmethod
    def verify_webhook_signature(
        webhook_body: str,
        webhook_signature: str,
        secret: str
    ) -> bool:
        """
        Verify Razorpay webhook signature.
        
        Args:
            webhook_body: Raw webhook request body
            webhook_signature: X-Razorpay-Signature header value
            secret: Razorpay webhook secret
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Generate signature using HMAC SHA256
            generated_signature = hmac.new(
                key=secret.encode('utf-8'),
                msg=webhook_body.encode('utf-8'),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            is_valid = hmac.compare_digest(generated_signature, webhook_signature)
            
            if not is_valid:
                logger.warning("✗ Webhook signature verification failed")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"✗ Webhook signature verification error: {e}")
            return False
