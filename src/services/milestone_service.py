"""
Milestone Service for Celebrations

Detects and manages user milestones for celebration animations.

Author: Billions Bounty
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import User, Milestone
from src.services.points_service import points_service
import logging

logger = logging.getLogger(__name__)


class MilestoneService:
    """Service for managing milestones and celebrations"""
    
    # Milestone definitions
    MILESTONE_DEFINITIONS = {
        # Points milestones
        "first_100_points": {
            "name": "First 100 Points!",
            "description": "You've reached 100 points!",
            "icon": "💯",
            "threshold": 100
        },
        "first_500_points": {
            "name": "500 Points!",
            "description": "Halfway to 1,000!",
            "icon": "🎯",
            "threshold": 500
        },
        "first_1000_points": {
            "name": "1,000 Points!",
            "description": "You're a point master!",
            "icon": "🏆",
            "threshold": 1000
        },
        "first_10000_points": {
            "name": "10,000 Points!",
            "description": "Legendary status achieved!",
            "icon": "👑",
            "threshold": 10000
        },
        
        # Tier milestones
        "tier_bronze": {
            "name": "Bronze Tier!",
            "description": "You've reached Bronze tier!",
            "icon": "🥉",
            "tier": "bronze"
        },
        "tier_silver": {
            "name": "Silver Tier!",
            "description": "You've reached Silver tier!",
            "icon": "⭐",
            "tier": "silver"
        },
        "tier_gold": {
            "name": "Gold Tier!",
            "description": "You've reached Gold tier!",
            "icon": "🏆",
            "tier": "gold"
        },
        "tier_platinum": {
            "name": "Platinum Tier!",
            "description": "You've reached Platinum tier!",
            "icon": "🥈",
            "tier": "platinum"
        },
        "tier_diamond": {
            "name": "Diamond Tier!",
            "description": "You've reached Diamond tier!",
            "icon": "💎",
            "tier": "diamond"
        },
        "tier_legendary": {
            "name": "Legendary Tier!",
            "description": "You've reached Legendary tier!",
            "icon": "👑",
            "tier": "legendary"
        },
        
        # Activity milestones
        "first_jailbreak": {
            "name": "First Jailbreak!",
            "description": "You successfully completed your first jailbreak!",
            "icon": "🎯"
        },
        "first_referral": {
            "name": "First Referral!",
            "description": "You referred your first friend!",
            "icon": "👥"
        },
        "first_question": {
            "name": "First Question!",
            "description": "You asked your first question!",
            "icon": "❓"
        },
        
        # Leaderboard milestones
        "top_100": {
            "name": "Top 100!",
            "description": "You're in the top 100 players!",
            "icon": "🎖️",
            "rank_threshold": 100
        },
        "top_50": {
            "name": "Top 50!",
            "description": "You're in the top 50 players!",
            "icon": "🎖️",
            "rank_threshold": 50
        },
        "top_10": {
            "name": "Top 10!",
            "description": "You're in the top 10 players!",
            "icon": "🏅",
            "rank_threshold": 10
        },
        "top_3": {
            "name": "Top 3!",
            "description": "You're in the top 3 players!",
            "icon": "🥉",
            "rank_threshold": 3
        },
        "rank_1": {
            "name": "#1 Player!",
            "description": "You're the #1 player!",
            "icon": "🥇",
            "rank_threshold": 1
        }
    }
    
    async def check_milestones(
        self, 
        session: AsyncSession, 
        user_id: int,
        previous_points: int = 0,
        previous_tier: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Check for new milestones based on user's current state
        
        Returns:
            List of newly achieved milestones
        """
        try:
            # Get user
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return []
            
            # Get current points and tier
            points_data = await points_service.calculate_user_points(session, user_id)
            current_points = points_data['total_points']
            current_tier = points_service._get_user_tier(current_points)
            
            # Get existing milestones
            existing_result = await session.execute(
                select(Milestone).where(Milestone.user_id == user_id)
            )
            existing_milestones = {m.milestone_type for m in existing_result.scalars().all()}
            
            new_milestones = []
            
            # Check points milestones
            for milestone_id, definition in self.MILESTONE_DEFINITIONS.items():
                if milestone_id in existing_milestones:
                    continue
                
                # Points milestones
                if "threshold" in definition:
                    if previous_points < definition["threshold"] <= current_points:
                        milestone = Milestone(
                            user_id=user_id,
                            milestone_type=milestone_id,
                            milestone_name=definition["name"],
                            description=definition["description"],
                            value=definition["threshold"],
                            celebration_shown=False
                        )
                        session.add(milestone)
                        new_milestones.append({
                            "milestone_type": milestone_id,
                            "name": definition["name"],
                            "description": definition["description"],
                            "icon": definition["icon"],
                            "value": definition["threshold"]
                        })
                
                # Tier milestones
                elif "tier" in definition:
                    if previous_tier != definition["tier"] and current_tier == definition["tier"]:
                        milestone = Milestone(
                            user_id=user_id,
                            milestone_type=milestone_id,
                            milestone_name=definition["name"],
                            description=definition["description"],
                            value=None,
                            celebration_shown=False
                        )
                        session.add(milestone)
                        new_milestones.append({
                            "milestone_type": milestone_id,
                            "name": definition["name"],
                            "description": definition["description"],
                            "icon": definition["icon"],
                            "tier": definition["tier"]
                        })
            
            if new_milestones:
                await session.commit()
                logger.info(f"🎉 User {user_id} achieved {len(new_milestones)} new milestones!")
            
            return new_milestones
        
        except Exception as e:
            logger.error(f"Error checking milestones for user {user_id}: {e}")
            await session.rollback()
            return []
    
    async def get_unshown_milestones(
        self, 
        session: AsyncSession, 
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Get milestones that haven't been shown to the user yet"""
        try:
            result = await session.execute(
                select(Milestone).where(
                    and_(
                        Milestone.user_id == user_id,
                        Milestone.celebration_shown == False
                    )
                ).order_by(Milestone.achieved_at.desc())
            )
            milestones = result.scalars().all()
            
            return [
                {
                    "id": m.id,
                    "milestone_type": m.milestone_type,
                    "name": m.milestone_name,
                    "description": m.description,
                    "value": m.value,
                    "achieved_at": m.achieved_at.isoformat()
                }
                for m in milestones
            ]
        
        except Exception as e:
            logger.error(f"Error getting unshown milestones for user {user_id}: {e}")
            return []
    
    async def mark_milestone_shown(
        self, 
        session: AsyncSession, 
        milestone_id: int
    ) -> bool:
        """Mark a milestone as shown (celebration displayed)"""
        try:
            result = await session.execute(
                select(Milestone).where(Milestone.id == milestone_id)
            )
            milestone = result.scalar_one_or_none()
            
            if milestone:
                milestone.celebration_shown = True
                await session.commit()
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error marking milestone {milestone_id} as shown: {e}")
            await session.rollback()
            return False


# Create singleton instance
milestone_service = MilestoneService()

