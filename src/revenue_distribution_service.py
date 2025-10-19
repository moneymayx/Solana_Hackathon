"""
Revenue Distribution Service

Handles monthly distribution of platform revenue to stakers
based on the tiered revenue-share model
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from .models import StakingPosition, User
from .token_config import (
    StakingPeriod,
    STAKING_REVENUE_PERCENTAGE,
    TIER_ALLOCATIONS
)


class RevenueDistributionService:
    """
    Manages monthly revenue distribution to stakers
    """
    
    async def calculate_monthly_distribution(
        self,
        db: AsyncSession,
        monthly_revenue: float,
        distribution_date: datetime = None
    ) -> Dict[str, Any]:
        """
        Calculate how revenue should be distributed to all active stakers
        
        Args:
            db: Database session
            monthly_revenue: Total platform revenue for the month
            distribution_date: Date of distribution (default: now)
            
        Returns:
            Dictionary with distribution breakdown
        """
        if distribution_date is None:
            distribution_date = datetime.utcnow()
        
        # Calculate total staking pool
        total_staking_pool = monthly_revenue * STAKING_REVENUE_PERCENTAGE
        
        # Get all active staking positions
        query = select(StakingPosition).where(
            StakingPosition.is_active == True,
            StakingPosition.staked_at <= distribution_date
        )
        result = await db.execute(query)
        all_positions = result.scalars().all()
        
        # Group by tier
        tiers = {
            StakingPeriod.THIRTY_DAYS: [],
            StakingPeriod.SIXTY_DAYS: [],
            StakingPeriod.NINETY_DAYS: []
        }
        
        for position in all_positions:
            for period in StakingPeriod:
                if position.staking_period_days == period.value:
                    tiers[period].append(position)
                    break
        
        # Calculate distribution for each tier
        tier_distributions = {}
        total_distributed = 0.0
        
        for period, positions in tiers.items():
            if not positions:
                tier_distributions[period.value] = {
                    "tier_pool": 0.0,
                    "total_staked": 0.0,
                    "staker_count": 0,
                    "distributions": []
                }
                continue
            
            # Calculate this tier's pool
            tier_allocation = TIER_ALLOCATIONS[period]
            tier_pool = total_staking_pool * tier_allocation
            
            # Calculate total staked in tier
            tier_total_staked = sum(p.staked_amount for p in positions)
            
            # Calculate distribution for each position
            distributions = []
            for position in positions:
                if tier_total_staked > 0:
                    share = position.staked_amount / tier_total_staked
                    reward = tier_pool * share
                else:
                    share = 0
                    reward = 0
                
                distributions.append({
                    "position_id": position.id,
                    "user_id": position.user_id,
                    "staked_amount": position.staked_amount,
                    "share_percentage": share * 100,
                    "reward_amount": reward
                })
                
                total_distributed += reward
            
            tier_distributions[period.value] = {
                "tier_pool": tier_pool,
                "tier_allocation_percentage": tier_allocation * 100,
                "total_staked": tier_total_staked,
                "staker_count": len(positions),
                "distributions": distributions
            }
        
        return {
            "monthly_revenue": monthly_revenue,
            "staking_revenue_percentage": STAKING_REVENUE_PERCENTAGE * 100,
            "total_staking_pool": total_staking_pool,
            "total_distributed": total_distributed,
            "distribution_date": distribution_date.isoformat(),
            "tiers": tier_distributions,
            "total_stakers": sum(len(positions) for positions in tiers.values())
        }
    
    async def execute_distribution(
        self,
        db: AsyncSession,
        monthly_revenue: float,
        distribution_date: datetime = None
    ) -> Dict[str, Any]:
        """
        Execute the monthly distribution and update staking positions
        
        Args:
            db: Database session
            monthly_revenue: Total platform revenue
            distribution_date: Distribution date
            
        Returns:
            Distribution summary
        """
        # Calculate distribution
        distribution = await self.calculate_monthly_distribution(
            db=db,
            monthly_revenue=monthly_revenue,
            distribution_date=distribution_date
        )
        
        # Update each staking position with actual rewards
        for tier_data in distribution["tiers"].values():
            for dist in tier_data["distributions"]:
                # Get position
                query = select(StakingPosition).where(
                    StakingPosition.id == dist["position_id"]
                )
                result = await db.execute(query)
                position = result.scalar_one_or_none()
                
                if position:
                    # Add to claimed rewards
                    position.claimed_rewards += dist["reward_amount"]
        
        await db.commit()
        
        return {
            **distribution,
            "status": "completed",
            "executed_at": datetime.utcnow().isoformat()
        }
    
    async def get_user_projected_earnings(
        self,
        db: AsyncSession,
        user_id: int,
        estimated_monthly_revenue: float = 10000.0
    ) -> Dict[str, Any]:
        """
        Get projected earnings for a user's staking positions
        
        Args:
            db: Database session
            user_id: User ID
            estimated_monthly_revenue: Estimated monthly revenue for projections
            
        Returns:
            Projected earnings breakdown
        """
        # Get user's active positions
        query = select(StakingPosition).where(
            StakingPosition.user_id == user_id,
            StakingPosition.is_active == True
        )
        result = await db.execute(query)
        positions = result.scalars().all()
        
        if not positions:
            return {
                "user_id": user_id,
                "active_positions": 0,
                "total_staked": 0.0,
                "projected_monthly_earnings": 0.0
            }
        
        # Calculate projections
        total_staked = sum(p.staked_amount for p in positions)
        total_monthly_earnings = 0.0
        position_details = []
        
        for position in positions:
            # Determine period
            period = None
            for p in StakingPeriod:
                if p.value == position.staking_period_days:
                    period = p
                    break
            
            if not period:
                continue
            
            # Get tier total
            tier_total_query = select(func.sum(StakingPosition.staked_amount)).where(
                StakingPosition.staking_period_days == period.value,
                StakingPosition.is_active == True
            )
            tier_result = await db.execute(tier_total_query)
            tier_total = tier_result.scalar() or 0.0
            
            # Calculate projections
            staking_pool = estimated_monthly_revenue * STAKING_REVENUE_PERCENTAGE
            tier_pool = staking_pool * TIER_ALLOCATIONS[period]
            
            if tier_total > 0:
                share = position.staked_amount / tier_total
                monthly_earnings = tier_pool * share
            else:
                share = 0
                monthly_earnings = 0
            
            total_monthly_earnings += monthly_earnings
            
            # Calculate remaining months
            days_remaining = (position.unlocks_at - datetime.utcnow()).days
            months_remaining = max(0, days_remaining / 30)
            projected_period_earnings = monthly_earnings * months_remaining
            
            position_details.append({
                "position_id": position.id,
                "staked_amount": position.staked_amount,
                "lock_period_days": position.staking_period_days,
                "tier_allocation": TIER_ALLOCATIONS[period] * 100,
                "unlocks_at": position.unlocks_at.isoformat(),
                "days_remaining": max(0, days_remaining),
                "claimed_rewards": position.claimed_rewards,
                "projected_monthly_earnings": monthly_earnings,
                "projected_remaining_earnings": projected_period_earnings,
                "share_of_tier": share * 100
            })
        
        return {
            "user_id": user_id,
            "active_positions": len(positions),
            "total_staked": total_staked,
            "projected_monthly_earnings": total_monthly_earnings,
            "estimated_monthly_revenue": estimated_monthly_revenue,
            "positions": position_details,
            "note": "Projections based on estimated revenue and current tier sizes - actual may vary"
        }
    
    async def get_tier_statistics(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get current statistics for all staking tiers
        
        Args:
            db: Database session
            
        Returns:
            Tier statistics
        """
        stats = {}
        
        for period in StakingPeriod:
            # Get total staked in tier
            total_query = select(func.sum(StakingPosition.staked_amount)).where(
                StakingPosition.staking_period_days == period.value,
                StakingPosition.is_active == True
            )
            total_result = await db.execute(total_query)
            total_staked = total_result.scalar() or 0.0
            
            # Get staker count
            count_query = select(func.count(StakingPosition.id)).where(
                StakingPosition.staking_period_days == period.value,
                StakingPosition.is_active == True
            )
            count_result = await db.execute(count_query)
            staker_count = count_result.scalar() or 0
            
            stats[f"{period.value}_day_tier"] = {
                "lock_period_days": period.value,
                "tier_allocation": TIER_ALLOCATIONS[period] * 100,
                "total_staked": total_staked,
                "staker_count": staker_count,
                "avg_stake_size": total_staked / staker_count if staker_count > 0 else 0
            }
        
        return {
            "tiers": stats,
            "total_active_stakers": sum(tier["staker_count"] for tier in stats.values()),
            "total_tokens_staked": sum(tier["total_staked"] for tier in stats.values())
        }


# Global singleton
revenue_distribution_service = RevenueDistributionService()

