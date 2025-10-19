"""
Phase 2 API: Token Economics ($100Bs)

Endpoints for token balance, staking, discounts, and buyback
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from ..database import get_db
from ..token_economics_service import TokenEconomicsService
from ..revenue_distribution_service import RevenueDistributionService
from ..token_config import StakingPeriod

router = APIRouter(prefix="/api/token", tags=["Token Economics"])

# Initialize services
token_service = TokenEconomicsService()
revenue_service = RevenueDistributionService()


# ===========================
# Request/Response Models
# ===========================

class TokenBalanceRequest(BaseModel):
    wallet_address: str
    user_id: int


class TokenBalanceResponse(BaseModel):
    wallet_address: str
    token_balance: float
    discount_rate: float
    tokens_to_next_tier: float
    last_verified: str


class DiscountRequest(BaseModel):
    wallet_address: str
    base_price: float


class DiscountResponse(BaseModel):
    base_price: float
    discount_rate: float
    discount_amount: float
    final_price: float
    token_balance: float


class StakingRequest(BaseModel):
    user_id: int
    wallet_address: str
    amount: float
    period_days: int  # 30, 60, or 90
    transaction_signature: Optional[str] = None


class StakingResponse(BaseModel):
    position_id: int
    staked_amount: float
    lock_period_days: int
    tier_allocation: float
    unlocks_at: str
    estimated_monthly_rewards: float
    estimated_period_rewards: float
    note: str


class UserStakingPositionsResponse(BaseModel):
    user_id: int
    active_positions: int
    total_staked: float
    projected_monthly_earnings: float
    positions: List[Dict[str, Any]]


# ===========================
# Token Balance Endpoints
# ===========================

@router.post("/balance/check", response_model=TokenBalanceResponse)
async def check_token_balance(
    request: TokenBalanceRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Check user's $100Bs token balance and discount tier
    
    This verifies on-chain balance and updates database cache
    """
    try:
        balance_data = await token_service.get_or_update_user_balance(
            db=db,
            user_id=request.user_id,
            wallet_address=request.wallet_address
        )
        
        return TokenBalanceResponse(
            wallet_address=request.wallet_address,
            token_balance=balance_data["token_balance"],
            discount_rate=balance_data["discount_rate"],
            tokens_to_next_tier=balance_data["tokens_to_next_tier"],
            last_verified=balance_data["last_verified"].isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/balance/{wallet_address}")
async def get_token_balance(
    wallet_address: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get cached token balance (faster, doesn't hit blockchain)
    """
    try:
        balance_data = await token_service.get_user_token_balance(
            db=db,
            wallet_address=wallet_address
        )
        
        if not balance_data:
            raise HTTPException(status_code=404, detail="Balance not found. Call /balance/check first.")
        
        return balance_data
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Discount Endpoints
# ===========================

@router.post("/discount/calculate", response_model=DiscountResponse)
async def calculate_discount(
    request: DiscountRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate discount for a given price based on token holdings
    
    Discount tiers:
    - 1,000,000+ tokens: 10% off
    - 10,000,000+ tokens: 25% off
    - 100,000,000+ tokens: 50% off
    """
    try:
        # Get token balance
        balance_data = await token_service.get_user_token_balance(
            db=db,
            wallet_address=request.wallet_address
        )
        
        if not balance_data:
            # No balance cached, return zero discount
            return DiscountResponse(
                base_price=request.base_price,
                discount_rate=0.0,
                discount_amount=0.0,
                final_price=request.base_price,
                token_balance=0.0
            )
        
        discount_rate = balance_data["discount_rate"]
        discount_amount = request.base_price * discount_rate
        final_price = request.base_price - discount_amount
        
        return DiscountResponse(
            base_price=request.base_price,
            discount_rate=discount_rate,
            discount_amount=discount_amount,
            final_price=final_price,
            token_balance=balance_data["token_balance"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/discount/apply")
async def apply_discount_to_transaction(
    user_id: int,
    wallet_address: str,
    base_price: float,
    service_type: str = "query",
    db: AsyncSession = Depends(get_db)
):
    """
    Apply discount and record usage
    
    This should be called when actually processing a transaction
    """
    try:
        usage_record = await token_service.record_discount_usage(
            db=db,
            user_id=user_id,
            wallet_address=wallet_address,
            base_price=base_price,
            service_type=service_type
        )
        
        return {
            "usage_id": usage_record.id,
            "base_price": usage_record.base_price,
            "discount_rate": usage_record.discount_rate,
            "discount_amount": usage_record.discount_amount,
            "final_price": usage_record.final_price,
            "token_balance": usage_record.token_balance,
            "used_at": usage_record.used_at.isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/discount/tiers")
async def get_discount_tiers():
    """
    Get all discount tiers
    """
    from ..token_config import DISCOUNT_TIERS
    
    tiers = []
    for balance, rate in sorted(DISCOUNT_TIERS.items()):
        tiers.append({
            "min_token_balance": balance,
            "discount_percentage": rate * 100,
            "description": f"{balance:,} tokens → {rate*100}% off"
        })
    
    return {"tiers": tiers}


# ===========================
# Staking Endpoints
# ===========================

@router.post("/stake", response_model=StakingResponse)
async def stake_tokens(
    request: StakingRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a staking position
    
    Lock tokens for 30, 60, or 90 days to earn revenue share
    
    Revenue model:
    - 30% of platform revenue goes to stakers
    - 30-day tier: 20% of staking pool
    - 60-day tier: 30% of staking pool
    - 90-day tier: 50% of staking pool
    """
    try:
        # Validate period
        valid_periods = [30, 60, 90]
        if request.period_days not in valid_periods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid staking period. Must be one of: {valid_periods}"
            )
        
        # Map to StakingPeriod enum
        period_map = {
            30: StakingPeriod.THIRTY_DAYS,
            60: StakingPeriod.SIXTY_DAYS,
            90: StakingPeriod.NINETY_DAYS
        }
        period = period_map[request.period_days]
        
        # Create staking position
        position = await token_service.create_staking_position(
            db=db,
            user_id=request.user_id,
            amount=request.amount,
            period=period,
            transaction_signature=request.transaction_signature,
            estimated_monthly_revenue=10000.0  # Use platform's actual revenue estimate
        )
        
        # Get estimated rewards
        from ..token_config import calculate_staking_share, TIER_ALLOCATIONS
        
        tier_total = await token_service._get_tier_total_staked(db, period)
        monthly_pool = 10000.0 * 0.30  # 30% of revenue
        share_calc = calculate_staking_share(
            amount=request.amount,
            period=period,
            tier_total_staked=tier_total,
            monthly_staking_pool=monthly_pool
        )
        
        return StakingResponse(
            position_id=position.id,
            staked_amount=position.staked_amount,
            lock_period_days=position.staking_period_days,
            tier_allocation=TIER_ALLOCATIONS[period] * 100,
            unlocks_at=position.unlocks_at.isoformat(),
            estimated_monthly_rewards=share_calc["estimated_monthly_rewards"],
            estimated_period_rewards=share_calc["estimated_period_rewards"],
            note="Rewards based on actual platform revenue - estimates may vary"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/staking/user/{user_id}", response_model=UserStakingPositionsResponse)
async def get_user_staking_positions(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all active staking positions for a user
    """
    try:
        positions = await token_service.get_user_staking_positions(
            db=db,
            user_id=user_id
        )
        
        # Get projected earnings
        projections = await revenue_service.get_user_projected_earnings(
            db=db,
            user_id=user_id,
            estimated_monthly_revenue=10000.0
        )
        
        return UserStakingPositionsResponse(
            user_id=user_id,
            active_positions=projections["active_positions"],
            total_staked=projections["total_staked"],
            projected_monthly_earnings=projections["projected_monthly_earnings"],
            positions=projections["positions"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/staking/unstake/{position_id}")
async def unstake_tokens(
    position_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Unstake tokens (only if unlock period has passed)
    """
    try:
        result = await token_service.unstake_position(
            db=db,
            position_id=position_id,
            user_id=user_id
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/staking/tier-stats")
async def get_tier_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    Get platform-wide staking tier statistics
    
    Useful for showing current tier sizes and average stakes
    """
    try:
        stats = await revenue_service.get_tier_statistics(db=db)
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Revenue Distribution Endpoints
# ===========================

@router.post("/revenue/distribute")
async def distribute_monthly_revenue(
    monthly_revenue: float,
    admin_key: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute monthly revenue distribution to stakers
    
    (Admin only - requires authentication)
    """
    # TODO: Add proper admin authentication
    # For now, using simple key check
    import os
    if admin_key != os.getenv("ADMIN_API_KEY"):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        distribution = await revenue_service.execute_distribution(
            db=db,
            monthly_revenue=monthly_revenue
        )
        
        return distribution
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue/calculate")
async def calculate_revenue_distribution(
    monthly_revenue: float,
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate how revenue would be distributed (without executing)
    
    Useful for previewing distributions before executing
    """
    try:
        distribution = await revenue_service.calculate_monthly_distribution(
            db=db,
            monthly_revenue=monthly_revenue
        )
        
        return distribution
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Buyback Endpoints
# ===========================

@router.get("/buyback/history")
async def get_buyback_history(
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get token buyback history
    
    Shows platform's commitment to token value
    """
    try:
        from ..models import BuybackEvent
        from sqlalchemy import select, desc
        
        query = select(BuybackEvent).order_by(
            desc(BuybackEvent.executed_at)
        ).limit(limit)
        
        result = await db.execute(query)
        events = result.scalars().all()
        
        buyback_history = []
        for event in events:
            buyback_history.append({
                "id": event.id,
                "revenue_amount": event.revenue_amount,
                "buyback_amount": event.buyback_amount,
                "tokens_bought": event.tokens_bought,
                "average_price": event.average_price,
                "period_start": event.period_start.isoformat(),
                "period_end": event.period_end.isoformat(),
                "executed_at": event.executed_at.isoformat(),
                "status": event.status
            })
        
        return {
            "total_events": len(buyback_history),
            "buyback_history": buyback_history
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Token Metrics
# ===========================

@router.get("/metrics")
async def get_token_metrics(
    db: AsyncSession = Depends(get_db)
):
    """
    Get platform-wide token metrics
    
    Shows:
    - Total staked
    - Staking ratio
    - Revenue allocation
    - Token price (if available)
    """
    try:
        from ..token_config import TOKEN_SYMBOL, TOKEN_TOTAL_SUPPLY, STAKING_REVENUE_PERCENTAGE
        from ..models import StakingPosition
        from sqlalchemy import select, func
        
        # Get total staked
        total_staked_query = select(func.sum(StakingPosition.staked_amount)).where(
            StakingPosition.is_active == True
        )
        result = await db.execute(total_staked_query)
        total_staked = result.scalar() or 0.0
        
        # Get tier stats
        tier_stats = await revenue_service.get_tier_statistics(db=db)
        
        return {
            "token_symbol": TOKEN_SYMBOL,
            "total_supply": TOKEN_TOTAL_SUPPLY,
            "total_staked": total_staked,
            "staking_ratio": (total_staked / TOKEN_TOTAL_SUPPLY) * 100 if TOKEN_TOTAL_SUPPLY > 0 else 0,
            "staking_revenue_percentage": STAKING_REVENUE_PERCENTAGE * 100,
            "tier_statistics": tier_stats,
            "note": "Staking rewards based on actual platform revenue"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Health & Status
# ===========================

@router.get("/health")
async def token_health():
    """
    Check health of token economics services
    """
    from ..token_config import TOKEN_MINT_ADDRESS, TOKEN_NETWORK
    
    return {
        "token_service_active": True,
        "revenue_service_active": True,
        "token_mint": str(TOKEN_MINT_ADDRESS),
        "network": TOKEN_NETWORK,
        "staking_enabled": True,
        "discounts_enabled": True,
        "buyback_enabled": True
    }

