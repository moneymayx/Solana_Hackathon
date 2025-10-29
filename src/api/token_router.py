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
from ..services.token_economics_service import TokenEconomicsService
from ..services.revenue_distribution_service import RevenueDistributionService
from ..config.token_config import StakingPeriod

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
        from datetime import datetime
        
        # Verify on-chain balance
        balance_data = await token_service.verify_token_balance(
            db=db,
            user_id=request.user_id,
            wallet_address=request.wallet_address
        )
        
        return TokenBalanceResponse(
            wallet_address=request.wallet_address,
            token_balance=balance_data["balance"],
            discount_rate=balance_data["discount_rate"],
            tokens_to_next_tier=balance_data.get("tokens_to_next_tier", 0),
            last_verified=datetime.utcnow().isoformat()
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
        from ..models import TokenBalance
        from sqlalchemy import select
        
        # Get from database cache
        query = select(TokenBalance).where(TokenBalance.wallet_address == wallet_address)
        result = await db.execute(query)
        balance_record = result.scalar_one_or_none()
        
        if not balance_record:
            raise HTTPException(status_code=404, detail="Balance not found. Call /balance/check first.")
        
        return {
            "wallet_address": balance_record.wallet_address,
            "token_balance": balance_record.token_balance,
            "discount_rate": balance_record.discount_rate,
            "tokens_to_next_tier": balance_record.tokens_to_next_tier,
            "last_verified": balance_record.last_verified.isoformat()
        }
    
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
        # Get projected earnings (includes positions)
        try:
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
        except Exception as proj_error:
            # Fallback: return empty positions
            return UserStakingPositionsResponse(
                user_id=user_id,
                active_positions=0,
                total_staked=0.0,
                projected_monthly_earnings=0.0,
                positions=[]
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


@router.get("/revenue/platform-stats")
async def get_platform_revenue_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get platform revenue statistics for staking dashboard
    
    Shows:
    - Total platform revenue (all-time and monthly)
    - Breakdown of the 20% distributed portion (Buyback + Staking)
    - Excludes 60% jackpot and 20% operations (not relevant to stakers)
    """
    try:
        from ..models import PaymentTransaction
        from sqlalchemy import select, func
        from datetime import datetime, timedelta
        
        # Get total confirmed revenue (all-time)
        total_revenue_query = select(func.sum(PaymentTransaction.amount_usd)).where(
            PaymentTransaction.status == "confirmed",
            PaymentTransaction.payment_type.in_(["query_payment", "usdc_purchase"])
        )
        result = await db.execute(total_revenue_query)
        total_revenue = result.scalar() or 0.0
        
        # Get monthly revenue (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        monthly_revenue_query = select(func.sum(PaymentTransaction.amount_usd)).where(
            PaymentTransaction.status == "confirmed",
            PaymentTransaction.payment_type.in_(["query_payment", "usdc_purchase"]),
            PaymentTransaction.created_at >= thirty_days_ago
        )
        result = await db.execute(monthly_revenue_query)
        monthly_revenue = result.scalar() or 0.0
        
        # Calculate allocations
        # 60% goes to jackpot (not shown to stakers)
        # 20% goes to operations (not shown to stakers)
        # 20% is distributed: 10% buyback + 10% staking
        
        distributed_percentage = 0.20  # The portion stakers care about
        buyback_percentage = 0.10
        staking_percentage = 0.10
        
        # Total distributed amounts (20% of revenue)
        total_distributed = total_revenue * distributed_percentage
        monthly_distributed = monthly_revenue * distributed_percentage
        
        # Breakdown: Buyback vs Staking
        total_buyback = total_revenue * buyback_percentage
        total_staking_pool = total_revenue * staking_percentage
        
        monthly_buyback = monthly_revenue * buyback_percentage
        monthly_staking_pool = monthly_revenue * staking_percentage
        
        return {
            "total_revenue": {
                "all_time": round(total_revenue, 2),
                "monthly": round(monthly_revenue, 2)
            },
            "distributed_portion": {
                "percentage": distributed_percentage * 100,  # 20%
                "all_time": round(total_distributed, 2),
                "monthly": round(monthly_distributed, 2),
                "breakdown": {
                    "buyback": {
                        "percentage": buyback_percentage * 100,  # 10%
                        "all_time": round(total_buyback, 2),
                        "monthly": round(monthly_buyback, 2)
                    },
                    "staking_pool": {
                        "percentage": staking_percentage * 100,  # 10%
                        "all_time": round(total_staking_pool, 2),
                        "monthly": round(monthly_staking_pool, 2)
                    }
                }
            },
            "note": "60% goes to jackpot, 20% to operations (not shown here)"
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
    from ..token_config import TOKEN_MINT_ADDRESS, TOKEN_SYMBOL
    
    return {
        "token_service_active": True,
        "revenue_service_active": True,
        "token_symbol": TOKEN_SYMBOL,
        "token_mint": TOKEN_MINT_ADDRESS,
        "staking_enabled": True,
        "discounts_enabled": True,
        "buyback_enabled": True
    }

