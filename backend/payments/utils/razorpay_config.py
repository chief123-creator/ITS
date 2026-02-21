"""
Razorpay Configuration Module
Manages Razorpay API credentials and configuration settings.
"""

import os
from typing import Optional, Dict


class RazorpayConfig:
    """
    Razorpay configuration manager.
    Loads credentials from environment variables or config file.
    """
    
    def __init__(self):
        """Initialize Razorpay configuration."""
        self.key_id: Optional[str] = None
        self.key_secret: Optional[str] = None
        self.test_mode: bool = True
        self._load_config()
    
    def _load_config(self) -> None:
        """
        Load Razorpay credentials from environment variables.
        Falls back to default test credentials if not found.
        """
        # Load from environment variables
        self.key_id = os.getenv('RAZORPAY_KEY_ID')
        self.key_secret = os.getenv('RAZORPAY_KEY_SECRET')
        
        # Check if test mode is explicitly set
        test_mode_env = os.getenv('RAZORPAY_TEST_MODE', 'true').lower()
        self.test_mode = test_mode_env in ('true', '1', 'yes')
        
        # Validate configuration
        if not self.key_id or not self.key_secret:
            print("⚠ Warning: Razorpay credentials not found in environment variables")
            print("  Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET environment variables")
            print("  Using placeholder values for development")
            
            # Set placeholder values for development
            self.key_id = self.key_id or "rzp_test_placeholder_key_id"
            self.key_secret = self.key_secret or "placeholder_key_secret"
    
    def validate(self) -> bool:
        """
        Validate that required credentials are present.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        if not self.key_id or not self.key_secret:
            return False
        
        # Check for placeholder values
        if 'placeholder' in self.key_id.lower() or 'placeholder' in self.key_secret.lower():
            return False
        
        return True
    
    def get_credentials(self) -> Dict[str, str]:
        """
        Get Razorpay credentials as dictionary.
        
        Returns:
            Dictionary with key_id and key_secret
            
        Raises:
            ValueError: If credentials are not configured
        """
        if not self.key_id or not self.key_secret:
            raise ValueError("Razorpay credentials not configured")
        
        return {
            'key_id': self.key_id,
            'key_secret': self.key_secret
        }
    
    def get_key_id(self) -> str:
        """
        Get Razorpay KEY_ID.
        
        Returns:
            Razorpay KEY_ID
            
        Raises:
            ValueError: If KEY_ID is not configured
        """
        if not self.key_id:
            raise ValueError("Razorpay KEY_ID not configured")
        return self.key_id
    
    def get_key_secret(self) -> str:
        """
        Get Razorpay KEY_SECRET.
        
        Returns:
            Razorpay KEY_SECRET
            
        Raises:
            ValueError: If KEY_SECRET is not configured
        """
        if not self.key_secret:
            raise ValueError("Razorpay KEY_SECRET not configured")
        return self.key_secret
    
    def is_test_mode(self) -> bool:
        """
        Check if running in test mode.
        
        Returns:
            True if test mode is enabled
        """
        return self.test_mode
    
    def sanitize_for_logging(self, text: str) -> str:
        """
        Sanitize text to remove sensitive credentials before logging.
        
        Args:
            text: Text that may contain sensitive information
            
        Returns:
            Sanitized text with credentials masked
        """
        sanitized = text
        
        if self.key_secret and self.key_secret in sanitized:
            sanitized = sanitized.replace(self.key_secret, '***REDACTED***')
        
        # Also mask partial key_secret (last 4 chars visible)
        if self.key_secret and len(self.key_secret) > 4:
            partial_secret = self.key_secret[:-4]
            if partial_secret in sanitized:
                sanitized = sanitized.replace(partial_secret, '***')
        
        return sanitized


# Global configuration instance
_config_instance: Optional[RazorpayConfig] = None


def get_razorpay_config() -> RazorpayConfig:
    """
    Get the global Razorpay configuration instance.
    
    Returns:
        RazorpayConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = RazorpayConfig()
    return _config_instance


def load_config_from_file(config_path: str) -> RazorpayConfig:
    """
    Load Razorpay configuration from a file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        RazorpayConfig instance
        
    Note:
        This is a placeholder for file-based configuration.
        Currently loads from environment variables.
    """
    # For now, just return the standard config
    # Can be extended to read from JSON/YAML files
    return get_razorpay_config()
