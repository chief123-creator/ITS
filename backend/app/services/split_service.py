"""
Split Service
Handles revenue splitting for payments (90% Govt, 5% Reporter, 5% Platform)
"""
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class SplitService:
    """Service for calculating payment splits"""
    
    GOVT_PERCENTAGE = 0.90
    REPORTER_PERCENTAGE = 0.05
    PLATFORM_PERCENTAGE = 0.05
    
    @staticmethod
    def calculate_splits(amount: int) -> Dict[str, int]:
        """Calculate fund distribution for a payment amount"""
        if amount <= 0:
            raise ValueError("Amount must be positive and non-zero")
        
        # Calculate splits
        govt_share = int(amount * SplitService.GOVT_PERCENTAGE)
        reporter_share = int(amount * SplitService.REPORTER_PERCENTAGE)
        
        # Platform gets remainder to ensure sum equals total
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
        """Validate that splits sum to original amount"""
        total = splits.get('govt', 0) + splits.get('reporter', 0) + splits.get('platform', 0)
        return total == original_amount
    
    @staticmethod
    def get_split_percentages() -> Dict[str, float]:
        """Get the configured split percentages"""
        return {
            'govt': SplitService.GOVT_PERCENTAGE,
            'reporter': SplitService.REPORTER_PERCENTAGE,
            'platform': SplitService.PLATFORM_PERCENTAGE
        }
