"""Phase 2 Token Economics API routes.

The endpoints below provide the JSON surface expected by the staking dashboard
and token discount utilities. They currently operate in "mock" mode, meaning
all staking activity is stored in the SQL database while on-chain transactions
are simulated. This keeps the frontend unblocked during local development and
mirrors the 60/20/10/10 lottery split defined in the Solana program.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.token_config import calculate_discounted_price, get_discount_for_balance
from ..database import get_db
from ..services.token_economics_service import TokenEconomicsService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/token", tags=["Token Economics"])

token_service = TokenEconomicsService()


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class TokenBalanceRequest(BaseModel):
    user_id: int
    wallet_address: str


class DiscountRequest(BaseModel):
    wallet_address: str
    base_price: float = Field(gt=0)
    user_id: Optional[int] = None


class StakeRequest(BaseModel):
    user_id: int
    wallet_address: str
    amount: float = Field(gt=0)
    period_days: int
    transaction_signature: Optional[str] = None


class ClaimRewardsRequest(BaseModel):
    user_id: int
    wallet_address: Optional[str] = None


class UnstakeRequest(BaseModel):
    user_id: int


# ---------------------------------------------------------------------------
# Balance + discount endpoints
# ---------------------------------------------------------------------------


@router.post("/balance/check")
async def check_balance(request: TokenBalanceRequest, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Approximate the holder balance from active staking positions."""

    try:
        balance = await token_service.estimate_token_balance(db, user_id=request.user_id)
        discount_rate = get_discount_for_balance(balance)

        return {
            "wallet_address": request.wallet_address,
            "token_balance": balance,
            "discount_rate": discount_rate,
            "tokens_to_next_tier": max(0.0, 1_000_000 - balance),
            "last_verified": "mock",
        }
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to check token balance", extra={"user_id": request.user_id})
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/balance/{wallet_address}")
async def get_balance(wallet_address: str, user_id: int, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Return the cached balance approximation for the given user."""

    return await check_balance(TokenBalanceRequest(user_id=user_id, wallet_address=wallet_address), db)


@router.post("/discount/calculate")
async def calculate_discount(request: DiscountRequest, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Calculate discount using the estimated staking balance."""

    user_id = request.user_id or 0
    balance = await token_service.estimate_token_balance(db, user_id=user_id)

    pricing = calculate_discounted_price(request.base_price, balance)
    pricing["token_balance"] = balance

    return pricing


@router.post("/discount/apply")
async def apply_discount(
    user_id: int,
    wallet_address: str,
    base_price: float,
    service_type: str = "query",
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Record a discount usage entry for auditing."""

    balance = await token_service.estimate_token_balance(db, user_id=user_id)
    discount_rate = get_discount_for_balance(balance)
    discount_amount = base_price * discount_rate
    final_price = base_price - discount_amount

    usage = await token_service.record_discount_usage(
        db,
        user_id=user_id,
        base_price=base_price,
        discount_rate=discount_rate,
        discount_amount=discount_amount,
        final_price=final_price,
        token_balance=balance,
        service_type=service_type,
    )

    return {
        "usage_id": usage.id,
        "wallet_address": wallet_address,
        "base_price": base_price,
        "discount_rate": discount_rate,
        "discount_amount": discount_amount,
        "final_price": final_price,
        "token_balance": balance,
        "used_at": usage.used_at.isoformat(),
    }


@router.get("/discount/tiers")
async def get_discount_tiers() -> Dict[str, Any]:
    """Expose static tier information."""

    return token_service.get_discount_tiers()


# ---------------------------------------------------------------------------
# Staking endpoints
# ---------------------------------------------------------------------------


@router.post("/stake")
async def stake_tokens(request: StakeRequest, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Create a staking position in mock mode."""

    try:
        return await token_service.create_staking_position(
            db,
            user_id=request.user_id,
            wallet_address=request.wallet_address,
            amount=request.amount,
            period_days=request.period_days,
            transaction_signature=request.transaction_signature,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to create staking position", extra={"user_id": request.user_id})
        raise HTTPException(status_code=500, detail="Failed to create staking position") from exc


@router.get("/staking/user/{user_id}")
async def get_user_staking_positions(user_id: int, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Return staking positions and summary for the requested user."""

    return await token_service.get_user_positions(db, user_id=user_id)


@router.post("/staking/claim")
async def claim_rewards(request: ClaimRewardsRequest, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Claim available rewards for a user."""

    return await token_service.claim_rewards(
        db,
        user_id=request.user_id,
        wallet_address=request.wallet_address,
    )


@router.post("/staking/unstake/{position_id}")
async def unstake_tokens(position_id: int, request: UnstakeRequest, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Mark the staking position as withdrawn once unlocked."""

    return await token_service.unstake_position(
        db,
        position_id=position_id,
        user_id=request.user_id,
    )


@router.get("/staking/tier-stats")
async def get_tier_stats(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Aggregate active staking positions by tier."""

    return await token_service.get_tier_statistics(db)


# ---------------------------------------------------------------------------
# Platform metrics
# ---------------------------------------------------------------------------


@router.get("/revenue/platform-stats")
async def get_platform_revenue() -> Dict[str, Any]:
    """Return deterministic revenue snapshot used by the dashboard UI."""

    return await token_service.get_platform_revenue_snapshot()


@router.get("/health")
async def token_health() -> Dict[str, Any]:
    """Simple health probe so monitoring can ping the token service."""

    return {
        "token_service_active": True,
        "staking_enabled": True,
        "discounts_enabled": True,
        "mode": "mock",
    }





