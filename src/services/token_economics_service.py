"""Token economics helpers for staking and discount flows.

This module provides a lightweight, database-backed implementation of the
`/api/token/*` surface so the frontend can exercise staking screens even when
the full Solana integration is not available locally. The helper methods focus
on deterministic calculations that mirror the 60/20/10/10 lottery split defined
in the smart contract configuration files.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.token_config import (
    BUYBACK_RATE,
    STAKING_REVENUE_PERCENTAGE,
    TIER_ALLOCATIONS,
    StakingPeriod,
    get_discount_for_balance,
    get_tier_allocation,
    get_tier_info,
)
from ..models import DiscountUsage, StakingPosition


logger = logging.getLogger(__name__)


class TokenEconomicsService:
    """Manage staking positions and derived platform metrics.

    The original implementation depended on live Solana RPC calls to verify
    wallet balances. For local development we instead project balances from the
    database so the UI can still render realistic data. Whenever the on-chain
    verifier is restored we can swap the internals here without changing the
    API surface.
    """

    def __init__(self) -> None:
        # Allow developers to control the revenue baseline when testing staking
        # payouts. We default to a modest figure so projections are non-zero.
        default_revenue = os.getenv("TOKEN_MONTHLY_REVENUE", "25000")
        try:
            self._monthly_revenue = max(float(default_revenue), 0.0)
        except ValueError:
            logger.warning(
                "Invalid TOKEN_MONTHLY_REVENUE value '%s'; falling back to 0", default_revenue
            )
            self._monthly_revenue = 0.0

    async def create_staking_position(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        wallet_address: str,
        amount: float,
        period_days: int,
        transaction_signature: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a staking position and project rewards.

        The lottery contract allocates 10% of every bounty entry to the staking
        vault. We mirror that split here so projected rewards stay aligned with
        the on-chain distribution.
        """

        period_enum = self._validate_period(period_days)
        tier_allocation = get_tier_allocation(period_days)

        tier_totals = await self._fetch_tier_totals(db)
        current_total = tier_totals.get(period_days, 0.0)

        projected_monthly, projected_period = self._project_rewards(
            stake_amount=amount,
            period_days=period_days,
            tier_total=current_total,
        )

        unlocks_at = datetime.utcnow() + timedelta(days=period_days)

        position = StakingPosition(
            user_id=user_id,
            wallet_address=wallet_address,
            stake_tx_signature=transaction_signature,
            staked_amount=amount,
            staking_period_days=period_days,
            apy_rate=tier_allocation * 100,
            tier_allocation_percentage=tier_allocation * 100,
            # Store the total revenue projection so mock staking mirrors the on-chain 60/20/10 payouts.
            estimated_rewards=projected_period,
            claimable_rewards=projected_monthly,
            total_rewards_earned=0.0,
            unlocks_at=unlocks_at,
            status="active",
            is_active=True,
            extra_metadata={
                "projected_monthly_rewards": projected_monthly,
                "projected_period_rewards": projected_period,
            },
        )

        db.add(position)
        await db.commit()
        await db.refresh(position)

        logger.info(
            "Created staking position",
            extra={
                "user_id": user_id,
                "period": period_enum.name,
                "amount": amount,
                "projected_monthly": projected_monthly,
            },
        )

        # Refresh totals to include the new stake when serialising.
        tier_totals[period_days] = current_total + amount
        payload = self._serialize_position(position, tier_totals)

        return {
            "success": True,
            "is_mock": True,  # Local mode simulates the on-chain transaction.
            "position": payload,
        }

    async def get_user_positions(self, db: AsyncSession, *, user_id: int) -> Dict[str, Any]:
        """Return structured staking data for a user."""

        tier_totals = await self._fetch_tier_totals(db)

        query = (
            select(StakingPosition)
            .where(StakingPosition.user_id == user_id)
            .order_by(StakingPosition.staked_at.desc())
        )
        result = await db.execute(query)
        positions = list(result.scalars().all())

        serialized = [self._serialize_position(position, tier_totals) for position in positions]

        total_staked = sum(item["staked_amount"] for item in serialized)
        total_rewards = sum(item.get("projected_monthly_earnings", 0.0) for item in serialized)
        active_positions = sum(1 for item in serialized if item["status"] == "active")

        monthly_staking_pool = self._monthly_revenue * STAKING_REVENUE_PERCENTAGE

        # Surface the revenue assumptions so the UI can label projections accurately.
        projection_context = {
            "monthly_platform_revenue": round(self._monthly_revenue, 2),
            "monthly_staking_pool": round(monthly_staking_pool, 2),
            "staking_pool_percentage": STAKING_REVENUE_PERCENTAGE * 100,
            "explanation": (
                "Projected rewards mirror the 60/20/10/10 lottery split, "
                "with this stake sharing in the staking vault's percentage of monthly platform revenue."
            ),
        }

        return {
            "user_id": user_id,
            "positions": serialized,
            "summary": {
                "total_staked": total_staked,
                "total_rewards_earned": total_rewards,
                "active_positions": active_positions,
            },
            "projection_context": projection_context,
        }

    async def claim_rewards(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        wallet_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Move claimable rewards into the claimed bucket for a user."""

        query = select(StakingPosition).where(
            StakingPosition.user_id == user_id,
            StakingPosition.is_active.is_(True),
        )
        result = await db.execute(query)
        positions = list(result.scalars().all())

        total_claimed = 0.0
        now = datetime.utcnow()

        for position in positions:
            claimable = float(position.claimable_rewards or 0.0)
            if claimable <= 0:
                continue

            total_claimed += claimable
            position.claimed_rewards = float(position.claimed_rewards or 0.0) + claimable
            position.total_rewards_earned = float(position.total_rewards_earned or 0.0) + claimable
            position.claimable_rewards = 0.0
            position.last_reward_calculated_at = now
            position.updated_at = now

        if total_claimed == 0.0:
            logger.info(
                "Claim attempted but no rewards available",
                extra={"user_id": user_id, "wallet_address": wallet_address},
            )
            return {"success": False, "amount_claimed": 0.0, "error": "No rewards available"}

        await db.commit()

        logger.info(
            "Claimed staking rewards",
            extra={"user_id": user_id, "wallet_address": wallet_address, "amount": total_claimed},
        )

        return {"success": True, "amount_claimed": total_claimed}

    async def unstake_position(
        self,
        db: AsyncSession,
        *,
        position_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """Set a staking position to inactive once the lock period elapses."""

        query = select(StakingPosition).where(
            StakingPosition.id == position_id,
            StakingPosition.user_id == user_id,
            StakingPosition.is_active.is_(True),
        )
        result = await db.execute(query)
        position = result.scalar_one_or_none()

        if position is None:
            return {"success": False, "error": "Position not found"}

        now = datetime.utcnow()
        if position.unlocks_at and position.unlocks_at > now:
            days_remaining = (position.unlocks_at - now).days
            return {
                "success": False,
                "error": "Position is still locked",
                "days_remaining": max(days_remaining, 0),
            }

        amount_returned = float(position.staked_amount or 0.0) + float(position.claimable_rewards or 0.0)

        position.is_active = False
        position.status = "unstaked"
        position.claimable_rewards = 0.0
        position.unstaked_at = now
        position.updated_at = now

        await db.commit()

        logger.info(
            "Unstaked position",
            extra={"user_id": user_id, "position_id": position_id, "amount": amount_returned},
        )

        return {"success": True, "amount_returned": amount_returned}

    async def get_tier_statistics(self, db: AsyncSession) -> Dict[str, Any]:
        """Aggregate staking totals per tier."""

        query = select(StakingPosition).where(StakingPosition.is_active.is_(True))
        result = await db.execute(query)
        positions = list(result.scalars().all())

        tiers: Dict[str, Dict[str, float]] = {}
        lock_day_accumulator: Dict[int, float] = {}

        for position in positions:
            period_days = int(position.staking_period_days)
            key = f"{period_days}_DAYS"
            tier_data = tiers.setdefault(
                key,
                {
                    "total_staked": 0.0,
                    "staker_count": 0,
                    "tier_allocation": TIER_ALLOCATIONS.get(
                        self._validate_period(period_days),
                        0.0,
                    ) * 100,
                    "average_lock_days": 0.0,
                },
            )

            tier_data["total_staked"] += float(position.staked_amount or 0.0)
            tier_data["staker_count"] += 1

            if position.unlocks_at and position.staked_at:
                lock_days = (position.unlocks_at - position.staked_at).total_seconds() / 86400
                lock_day_accumulator[period_days] = lock_day_accumulator.get(period_days, 0.0) + lock_days

        for tier_name, tier_data in tiers.items():
            period_days = int(tier_name.split("_", 1)[0])
            count = tier_data["staker_count"]
            if count > 0:
                tier_data["average_lock_days"] = lock_day_accumulator.get(period_days, 0.0) / count

            # Round values for stability in responses
            tier_data["total_staked"] = round(tier_data["total_staked"], 2)
            tier_data["average_lock_days"] = round(tier_data["average_lock_days"], 2)

        return {"tiers": tiers, "updated_at": datetime.utcnow().isoformat()}

    async def get_platform_revenue_snapshot(self) -> Dict[str, Any]:
        """Produce a deterministic revenue breakdown for dashboards."""

        monthly = self._monthly_revenue
        weekly = monthly / 4 if monthly else 0.0
        daily = monthly / 30 if monthly else 0.0

        staking_monthly = monthly * STAKING_REVENUE_PERCENTAGE
        buyback_monthly = monthly * BUYBACK_RATE
        distributed_monthly = staking_monthly + buyback_monthly

        return {
            "total_revenue": {
                "monthly": monthly,
                "weekly": weekly,
                "daily": daily,
            },
            "distributed_portion": {
                "percentage": (STAKING_REVENUE_PERCENTAGE + BUYBACK_RATE) * 100,
                "monthly": distributed_monthly,
                "weekly": distributed_monthly / 4 if distributed_monthly else 0.0,
                "breakdown": {
                    "staking_pool": {
                        "percentage": STAKING_REVENUE_PERCENTAGE * 100,
                        "monthly": staking_monthly,
                        "weekly": staking_monthly / 4 if staking_monthly else 0.0,
                        "daily": staking_monthly / 30 if staking_monthly else 0.0,
                    },
                    "buyback": {
                        "percentage": BUYBACK_RATE * 100,
                        "monthly": buyback_monthly,
                        "weekly": buyback_monthly / 4 if buyback_monthly else 0.0,
                        "daily": buyback_monthly / 30 if buyback_monthly else 0.0,
                    },
                },
            },
        }

    async def estimate_token_balance(self, db: AsyncSession, *, user_id: int) -> float:
        """Estimate a holder's balance from active staking positions."""

        query = select(func.sum(StakingPosition.staked_amount)).where(
            StakingPosition.user_id == user_id,
            StakingPosition.is_active.is_(True),
        )
        result = await db.execute(query)
        total = result.scalar()
        return float(total or 0.0)

    async def record_discount_usage(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        base_price: float,
        discount_rate: float,
        discount_amount: float,
        final_price: float,
        token_balance: float,
        service_type: str = "query",
    ) -> DiscountUsage:
        """Persist a discount usage record for auditability."""

        usage = DiscountUsage(
            user_id=user_id,
            base_price=base_price,
            discount_rate=discount_rate,
            discount_amount=discount_amount,
            final_price=final_price,
            token_balance=token_balance,
            service_type=service_type,
        )

        db.add(usage)
        await db.commit()
        await db.refresh(usage)

        logger.info(
            "Recorded discount usage",
            extra={
                "user_id": user_id,
                "base_price": base_price,
                "discount_rate": discount_rate,
                "final_price": final_price,
            },
        )

        return usage

    def get_discount_tiers(self) -> Dict[str, List[Dict[str, float]]]:
        """Expose static discount tiers to API consumers."""

        return {"tiers": get_tier_info(), "updated_at": datetime.utcnow().isoformat()}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_period(self, period_days: int) -> StakingPeriod:
        try:
            return StakingPeriod(period_days)
        except ValueError as exc:  # pragma: no cover - defensive
            raise ValueError("Unsupported staking period") from exc

    async def _fetch_tier_totals(self, db: AsyncSession) -> Dict[int, float]:
        query = (
            select(
                StakingPosition.staking_period_days,
                func.sum(StakingPosition.staked_amount),
            )
            .where(StakingPosition.is_active.is_(True))
            .group_by(StakingPosition.staking_period_days)
        )
        result = await db.execute(query)
        return {int(period): float(total or 0.0) for period, total in result}

    def _project_rewards(
        self,
        *,
        stake_amount: float,
        period_days: int,
        tier_total: float,
    ) -> Tuple[float, float]:
        monthly_pool = self._monthly_revenue * STAKING_REVENUE_PERCENTAGE
        tier_allocation = get_tier_allocation(period_days)
        tier_pool = monthly_pool * tier_allocation

        denominator = tier_total + stake_amount
        if denominator <= 0:
            return 0.0, 0.0

        share = stake_amount / denominator
        projected_monthly = tier_pool * share
        projected_period = projected_monthly * (period_days / 30)
        return projected_monthly, projected_period

    def _serialize_position(
        self,
        position: StakingPosition,
        tier_totals: Dict[int, float],
    ) -> Dict[str, Any]:
        tier_total = tier_totals.get(position.staking_period_days, position.staked_amount)
        share = 100.0 if tier_total == 0 else (position.staked_amount / tier_total) * 100
        is_unlocked = bool(position.unlocks_at and position.unlocks_at <= datetime.utcnow())

        metadata = position.extra_metadata or {}
        projected_monthly = float(
            metadata.get("projected_monthly_rewards", position.claimable_rewards or 0.0)
        )

        return {
            "position_id": position.id,
            "staked_amount": float(position.staked_amount or 0.0),
            "lock_period_days": position.staking_period_days,
            "tier_allocation": float(position.tier_allocation_percentage or 0.0),
            "apy_rate": float(getattr(position, "apy_rate", 0.0) or 0.0),
            "estimated_rewards": float(getattr(position, "estimated_rewards", 0.0) or 0.0),
            "unlocks_at": position.unlocks_at.isoformat() if position.unlocks_at else None,
            "claimable_rewards": float(position.claimable_rewards or 0.0),
            "claimed_rewards": float(position.claimed_rewards or 0.0),
            "total_rewards_earned": float(position.total_rewards_earned or 0.0),
            "projected_monthly_earnings": projected_monthly,
            "status": position.status,
            "is_unlocked": is_unlocked,
            "share_of_tier": share,
            "wallet_address": position.wallet_address,
        }


