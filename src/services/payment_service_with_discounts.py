"""
Payment Service with $100Bs Token Discount Integration

Wraps payment processing to apply token holder discounts automatically
"""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .token_economics_service import TokenEconomicsService
from ..config.token_config import BASE_QUERY_COST


class PaymentServiceWithDiscounts:
    """
    Enhanced payment service that applies $100Bs token holder discounts
    """
    
    def __init__(self):
        self.token_service = TokenEconomicsService()
    
    async def calculate_query_cost(
        self,
        db: AsyncSession,
        user_id: int,
        wallet_address: Optional[str] = None,
        verify_balance: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate query cost with token holder discount applied
        
        Args:
            db: Database session
            user_id: User ID
            wallet_address: User's Solana wallet (for balance verification)
            verify_balance: Whether to verify on-chain balance (or use cache)
            
        Returns:
            Dictionary with pricing details
        """
        base_price = BASE_QUERY_COST
        
        # If wallet address provided and verification requested, update balance
        if wallet_address and verify_balance:
            await self.token_service.verify_token_balance(
                db=db,
                user_id=user_id,
                wallet_address=wallet_address,
                force_refresh=False  # Use 5-min cache
            )
        
        # Calculate discount
        pricing = await self.token_service.calculate_query_discount(
            db=db,
            user_id=user_id,
            base_price=base_price
        )
        
        return {
            **pricing,
            "has_discount": pricing["discount_rate"] > 0,
            "savings_percentage": pricing["discount_rate"] * 100,
        }
    
    async def process_query_payment(
        self,
        db: AsyncSession,
        user_id: int,
        wallet_address: Optional[str] = None,
        eligibility_type: str = "paid",
        payment_method: str = "crypto"
    ) -> Dict[str, Any]:
        """
        Process query payment with automatic discount application
        
        Args:
            db: Database session
            user_id: User ID
            wallet_address: User's Solana wallet
            eligibility_type: free_questions, paid, referral_signup, etc.
            payment_method: crypto, credit_card, etc.
            
        Returns:
            Payment result with discount details
        """
        # Free queries don't need discount calculation
        if eligibility_type in ["free_questions", "referral_signup", "anonymous"]:
            return {
                "success": True,
                "paid": False,
                "eligibility_type": eligibility_type,
                "amount_charged": 0.0,
                "discount_applied": False
            }
        
        # Calculate cost with discount
        pricing = await self.calculate_query_cost(
            db=db,
            user_id=user_id,
            wallet_address=wallet_address,
            verify_balance=True
        )
        
        # Record discount usage if applicable
        if pricing["has_discount"]:
            await self.token_service.record_discount_usage(
                db=db,
                user_id=user_id,
                base_price=pricing["base_price"],
                discount_rate=pricing["discount_rate"],
                discount_amount=pricing["discount_amount"],
                final_price=pricing["final_price"],
                token_balance=pricing.get("token_balance", 0.0),
                service_type="query"
            )
        
        # TODO: Integrate with actual payment processor
        # For now, return success with pricing details
        
        return {
            "success": True,
            "paid": True,
            "eligibility_type": eligibility_type,
            "payment_method": payment_method,
            "base_price": pricing["base_price"],
            "discount_applied": pricing["has_discount"],
            "discount_percentage": pricing["savings_percentage"],
            "discount_amount": pricing["discount_amount"],
            "final_price": pricing["final_price"],
            "amount_charged": pricing["final_price"],
            "token_balance": pricing.get("token_balance", 0.0),
            "tokens_to_next_tier": pricing.get("tokens_required", 0.0)
        }
    
    async def get_user_discount_info(
        self,
        db: AsyncSession,
        user_id: int,
        wallet_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get user's current discount tier and token balance
        
        Args:
            db: Database session
            user_id: User ID
            wallet_address: User's wallet (optional, for refresh)
            
        Returns:
            Dictionary with discount tier information
        """
        # Verify balance if wallet provided
        if wallet_address:
            balance_info = await self.token_service.verify_token_balance(
                db=db,
                user_id=user_id,
                wallet_address=wallet_address,
                force_refresh=False
            )
        else:
            # Use cached balance
            pricing = await self.token_service.calculate_query_discount(
                db=db,
                user_id=user_id,
                base_price=BASE_QUERY_COST
            )
            balance_info = {
                "balance": pricing.get("token_balance", 0.0),
                "discount_rate": pricing.get("discount_rate", 0.0),
                "cached": True
            }
        
        # Calculate what they'd save on a query
        example_pricing = await self.token_service.calculate_query_discount(
            db=db,
            user_id=user_id,
            base_price=BASE_QUERY_COST
        )
        
        # Get tier information
        from ..config.token_config import get_tier_info
        tiers = get_tier_info()
        
        return {
            "token_balance": balance_info["balance"],
            "current_discount_percentage": balance_info["discount_rate"] * 100,
            "tokens_to_next_tier": balance_info.get("tokens_to_next_tier", 0.0),
            "example_query_cost": example_pricing["final_price"],
            "example_savings": example_pricing["discount_amount"],
            "all_tiers": tiers,
            "cached": balance_info.get("cached", False),
            "last_verified": balance_info.get("last_verified")
        }
    
    async def close(self):
        """Close connections"""
        await self.token_service.close()


# Global singleton instance
payment_service = PaymentServiceWithDiscounts()

