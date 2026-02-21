"""
Split Engine Service Module
Handles automatic fund splitting for challan payments.
Distributes fine amounts: 90% Govt, 5% Reporter, 5% Platform
"""

from typing import Dict
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SplitEngine:
    """
    Service class for automatic fund splitting.
    Calculates and executes distribution of fine amounts among stakeholders.
    """
    
    # Split percentages
    GOVT_PERCENTAGE = 0.90
    REPORTER_PERCENTAGE = 0.05
    PLATFORM_PERCENTAGE = 0.05
    
    @staticmethod
    def calculate_splits(amount: int) -> Dict[str, int]:
        """
        Calculate fund distribution for a payment amount.
        
        Split Logic:
            - Government: 90% of fine amount
            - Reporter: 5% of fine amount
            - Platform: 5% of fine amount
            - Ensures sum of splits equals original amount (handles rounding)
        
        Args:
            amount: Total payment amount in paisa
            
        Returns:
            Dictionary with split amounts:
            {
                "govt": int,
                "reporter": int,
                "platform": int
            }
            
        Raises:
            ValueError: If amount is not positive
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("Amount must be positive and non-zero")
        
        # Calculate splits
        govt_share = int(amount * SplitEngine.GOVT_PERCENTAGE)
        reporter_share = int(amount * SplitEngine.REPORTER_PERCENTAGE)
        
        # Platform gets remainder to ensure sum equals total
        # This handles any rounding discrepancies
        platform_share = amount - govt_share - reporter_share
        
        splits = {
            'govt': govt_share,
            'reporter': reporter_share,
            'platform': platform_share
        }
        
        # Verify sum equals original amount
        total = govt_share + reporter_share + platform_share
        if total != amount:
            logger.error(f"Split calculation error: sum ({total}) != amount ({amount})")
            raise ValueError("Split calculation resulted in incorrect total")
        
        logger.info(
            f"Split calculated - Amount: ₹{amount/100:.2f}, "
            f"Govt: ₹{govt_share/100:.2f}, "
            f"Reporter: ₹{reporter_share/100:.2f}, "
            f"Platform: ₹{platform_share/100:.2f}"
        )
        
        return splits
    
    @staticmethod
    def validate_splits(splits: Dict[str, int], original_amount: int) -> bool:
        """
        Validate that splits sum to original amount.
        
        Args:
            splits: Dictionary with govt, reporter, platform amounts
            original_amount: Original payment amount
            
        Returns:
            True if valid, False otherwise
        """
        total = splits.get('govt', 0) + splits.get('reporter', 0) + splits.get('platform', 0)
        return total == original_amount
    
    @staticmethod
    def get_split_percentages() -> Dict[str, float]:
        """
        Get the configured split percentages.
        
        Returns:
            Dictionary with percentage values
        """
        return {
            'govt': SplitEngine.GOVT_PERCENTAGE,
            'reporter': SplitEngine.REPORTER_PERCENTAGE,
            'platform': SplitEngine.PLATFORM_PERCENTAGE
        }
    
    @staticmethod
    def format_split_breakdown(splits: Dict[str, int]) -> str:
        """
        Format split breakdown as human-readable string.
        
        Args:
            splits: Dictionary with split amounts
            
        Returns:
            Formatted string with split breakdown
        """
        return (
            f"Government: ₹{splits['govt']/100:.2f} (90%), "
            f"Reporter: ₹{splits['reporter']/100:.2f} (5%), "
            f"Platform: ₹{splits['platform']/100:.2f} (5%)"
        )
