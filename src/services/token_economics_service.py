"""
Token Economics Service for $100Bs Integration

Handles:
- Token balance verification on Solana
- Discount calculation and application
- Staking operations
- Buyback tracking
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from solders.pubkey import Pubkey  # type: ignore
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
import os

from ..models import TokenBalance, StakingPosition, DiscountUsage, BuybackEvent, TokenPrice
from ..config.token_config import (
    TOKEN_MINT_ADDRESS,
    TOKEN_DECIMALS,
    get_discount_for_balance,
    calculate_discounted_price,
    calculate_staking_share,
    StakingPeriod,
    TIER_ALLOCATIONS,
    STAKING_REVENUE_PERCENTAGE
)


class TokenEconomicsService:
    """
    Service for managing $100Bs token economics
    """
    
    def __init__(self):
        # Solana RPC connection
        rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        self.client = AsyncClient(rpc_url, commitment=Confirmed)
        
        # Token configuration
        self.token_mint = Pubkey.from_string(TOKEN_MINT_ADDRESS)
        self.decimals = TOKEN_DECIMALS
    
    async def verify_token_balance(
        self,
        db: AsyncSession,
        user_id: int,
        wallet_address: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Verify user's $100Bs token balance on-chain
        
        Args:
            db: Database session
            user_id: User ID
            wallet_address: Solana wallet address
            force_refresh: Force on-chain verification even if recent cache exists
            
        Returns:
            Dictionary with balance and discount info
        """
        # Check for cached balance (within last 5 minutes)
        if not force_refresh:
            query = select(TokenBalance).where(
                TokenBalance.user_id == user_id,
                TokenBalance.last_verified >= datetime.utcnow() - timedelta(minutes=5)
            )
            result = await db.execute(query)
            cached = result.scalar_one_or_none()
            
            if cached:
                return {
                    "balance": cached.token_balance,
                    "discount_rate": cached.discount_rate,
                    "tokens_to_next_tier": cached.tokens_to_next_tier,
                    "cached": True,
                    "last_verified": cached.last_verified
                }
        
        # Fetch balance from Solana
        try:
            wallet_pubkey = Pubkey.from_string(wallet_address)
            
            # Get token accounts for this wallet
            response = await self.client.get_token_accounts_by_owner(
                wallet_pubkey,
                {"mint": self.token_mint}
            )
            
            balance = 0.0
            if response.value:
                # Parse token account balance
                for account in response.value:
                    account_data = account.account.data
                    # Token amount is stored in the account data
                    # This is a simplified version - in production, use proper SPL token parsing
                    if hasattr(account_data, 'parsed'):
                        token_amount = account_data.parsed['info']['tokenAmount']
                        balance = float(token_amount['uiAmount'])
            
            # Calculate discount tier
            discount_rate = get_discount_for_balance(balance)
            
            # Get next tier requirement
            from ..config.token_config import get_next_tier_requirement
            tokens_to_next = get_next_tier_requirement(balance)
            
            # Update or create TokenBalance record
            query = select(TokenBalance).where(TokenBalance.user_id == user_id)
            result = await db.execute(query)
            token_balance = result.scalar_one_or_none()
            
            if token_balance:
                token_balance.token_balance = balance
                token_balance.wallet_address = wallet_address
                token_balance.discount_rate = discount_rate
                token_balance.tokens_to_next_tier = tokens_to_next
                token_balance.last_verified = datetime.utcnow()
                token_balance.updated_at = datetime.utcnow()
            else:
                token_balance = TokenBalance(
                    user_id=user_id,
                    wallet_address=wallet_address,
                    token_balance=balance,
                    discount_rate=discount_rate,
                    tokens_to_next_tier=tokens_to_next,
                    last_verified=datetime.utcnow()
                )
                db.add(token_balance)
            
            await db.commit()
            
            return {
                "balance": balance,
                "discount_rate": discount_rate,
                "tokens_to_next_tier": tokens_to_next,
                "cached": False,
                "last_verified": datetime.utcnow()
            }
            
        except Exception as e:
            print(f"❌ Error verifying token balance: {e}")
            # Return zero balance on error
            return {
                "balance": 0.0,
                "discount_rate": 0.0,
                "tokens_to_next_tier": 0.0,
                "cached": False,
                "error": str(e)
            }
    
    async def calculate_query_discount(
        self,
        db: AsyncSession,
        user_id: int,
        base_price: float
    ) -> Dict[str, float]:
        """
        Calculate discount for a query based on user's token balance
        
        Args:
            db: Database session
            user_id: User ID
            base_price: Original query price
            
        Returns:
            Dictionary with pricing breakdown
        """
        # Get user's token balance
        query = select(TokenBalance).where(TokenBalance.user_id == user_id)
        result = await db.execute(query)
        token_balance = result.scalar_one_or_none()
        
        if not token_balance:
            # No tokens, no discount
            return {
                "base_price": base_price,
                "discount_rate": 0.0,
                "discount_amount": 0.0,
                "final_price": base_price,
                "token_balance": 0.0
            }
        
        # Calculate discounted price
        pricing = calculate_discounted_price(base_price, token_balance.token_balance)
        pricing["token_balance"] = token_balance.token_balance
        
        return pricing
    
    async def record_discount_usage(
        self,
        db: AsyncSession,
        user_id: int,
        base_price: float,
        discount_rate: float,
        discount_amount: float,
        final_price: float,
        token_balance: float,
        service_type: str = "query"
    ) -> DiscountUsage:
        """
        Record usage of token holder discount
        
        Args:
            db: Database session
            user_id: User ID
            base_price: Original price
            discount_rate: Discount percentage applied
            discount_amount: Dollar amount saved
            final_price: Final price after discount
            token_balance: Token balance at time of discount
            service_type: Type of service (query, entry_fee, etc.)
            
        Returns:
            Created DiscountUsage record
        """
        usage = DiscountUsage(
            user_id=user_id,
            base_price=base_price,
            discount_rate=discount_rate,
            discount_amount=discount_amount,
            final_price=final_price,
            token_balance=token_balance,
            service_type=service_type
        )
        
        db.add(usage)
        await db.commit()
        await db.refresh(usage)
        
        return usage
    
    async def create_staking_position(
        self,
        db: AsyncSession,
        user_id: int,
        amount: float,
        period: StakingPeriod,
        transaction_signature: Optional[str] = None,
        estimated_monthly_revenue: float = 10000.0  # Used for estimates
    ) -> StakingPosition:
        """
        Create a new staking position with revenue-based rewards
        
        Args:
            db: Database session
            user_id: User ID
            amount: Amount of tokens to stake
            period: Staking period (30/60/90 days)
            transaction_signature: On-chain transaction signature
            estimated_monthly_revenue: Estimated monthly platform revenue (for reward estimates)
            
        Returns:
            Created StakingPosition
        """
        # Get total staked in this tier to calculate share
        tier_total = await self._get_tier_total_staked(db, period)
        
        # Calculate estimated monthly staking pool
        monthly_staking_pool = estimated_monthly_revenue * STAKING_REVENUE_PERCENTAGE
        
        # Calculate estimated rewards
        share_calc = calculate_staking_share(
            amount=amount,
            period=period,
            tier_total_staked=tier_total + amount,  # Include this stake
            monthly_staking_pool=monthly_staking_pool
        )
        
        # Calculate unlock date
        unlock_date = datetime.utcnow() + timedelta(days=period.value)
        
        # Create position (store tier allocation instead of APY)
        position = StakingPosition(
            user_id=user_id,
            staked_amount=amount,
            staking_period_days=period.value,
            apy_rate=TIER_ALLOCATIONS[period] * 100,  # Store tier % in apy_rate field for compatibility
            staked_at=datetime.utcnow(),
            unlocks_at=unlock_date,
            estimated_rewards=share_calc["estimated_period_rewards"],
            transaction_signature=transaction_signature,
            is_active=True
        )
        
        db.add(position)
        await db.commit()
        await db.refresh(position)
        
        return position
    
    async def _get_tier_total_staked(
        self,
        db: AsyncSession,
        period: StakingPeriod
    ) -> float:
        """
        Get total amount staked in a specific tier
        
        Args:
            db: Database session
            period: Staking period (tier)
            
        Returns:
            Total tokens staked in this tier
        """
        query = select(func.sum(StakingPosition.staked_amount)).where(
            StakingPosition.staking_period_days == period.value,
            StakingPosition.is_active == True
        )
        result = await db.execute(query)
        total = result.scalar()
        
        return total or 0.0
    
    async def get_user_staking_positions(
        self,
        db: AsyncSession,
        user_id: int,
        active_only: bool = True
    ) -> List[StakingPosition]:
        """
        Get all staking positions for a user
        
        Args:
            db: Database session
            user_id: User ID
            active_only: Only return active positions
            
        Returns:
            List of StakingPosition objects
        """
        query = select(StakingPosition).where(StakingPosition.user_id == user_id)
        
        if active_only:
            query = query.where(StakingPosition.is_active == True)
        
        query = query.order_by(StakingPosition.staked_at.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def unstake_position(
        self,
        db: AsyncSession,
        position_id: int,
        user_id: int,
        transaction_signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Unstake a position (only if unlock period has passed)
        
        Args:
            db: Database session
            position_id: Staking position ID
            user_id: User ID (for verification)
            transaction_signature: On-chain unstake transaction
            
        Returns:
            Dictionary with unstaking details
        """
        # Get position
        query = select(StakingPosition).where(
            StakingPosition.id == position_id,
            StakingPosition.user_id == user_id,
            StakingPosition.is_active == True
        )
        result = await db.execute(query)
        position = result.scalar_one_or_none()
        
        if not position:
            return {"error": "Position not found or not active"}
        
        # Check if unlock period has passed
        if datetime.utcnow() < position.unlocks_at:
            return {
                "error": "Position is still locked",
                "unlocks_at": position.unlocks_at,
                "days_remaining": (position.unlocks_at - datetime.utcnow()).days
            }
        
        # Mark as inactive
        position.is_active = False
        position.withdrawn_at = datetime.utcnow()
        
        # Calculate actual rewards (could be different if withdrawn early)
        days_staked = (datetime.utcnow() - position.staked_at).days
        actual_rewards = position.estimated_rewards  # Full rewards if unlocked
        
        await db.commit()
        
        return {
            "success": True,
            "staked_amount": position.staked_amount,
            "rewards_earned": actual_rewards,
            "total_return": position.staked_amount + actual_rewards,
            "days_staked": days_staked,
            "transaction_signature": transaction_signature
        }
    
    async def get_discount_stats(
        self,
        db: AsyncSession,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get statistics on discount usage
        
        Args:
            db: Database session
            days_back: Number of days to look back
            
        Returns:
            Dictionary with discount statistics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Total discounts given
        total_query = select(
            func.count(DiscountUsage.id),
            func.sum(DiscountUsage.discount_amount),
            func.avg(DiscountUsage.discount_rate)
        ).where(DiscountUsage.used_at >= cutoff_date)
        
        result = await db.execute(total_query)
        count, total_saved, avg_rate = result.one()
        
        return {
            "period_days": days_back,
            "total_discounts_used": count or 0,
            "total_amount_saved": total_saved or 0.0,
            "average_discount_rate": (avg_rate or 0.0) * 100,  # Convert to percentage
        }
    
    async def close(self):
        """Close the Solana RPC client"""
        await self.client.close()

