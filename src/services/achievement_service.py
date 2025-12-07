"""
Enhanced Achievement Service

Manages user achievements, badges, and unlocks. Expands on the existing achievement system.

Author: Billions Bounty
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import User, Achievement, Conversation, Referral, AttackAttempt, Milestone
import logging

logger = logging.getLogger(__name__)


class AchievementService:
    """Service for managing achievements and badges"""
    
    # Achievement definitions
    ACHIEVEMENT_DEFINITIONS = {
        # Points-based achievements
        "point_collector_100": {
            "type": "points",
            "name": "Point Collector",
            "description": "Reach 100 total points",
            "rarity": "common",
            "points_reward": 10,
            "icon": "💯",
            "condition": {"type": "points", "threshold": 100}
        },
        "point_collector_500": {
            "type": "points",
            "name": "Point Collector",
            "description": "Reach 500 total points",
            "rarity": "rare",
            "points_reward": 50,
            "icon": "💎",
            "condition": {"type": "points", "threshold": 500}
        },
        "point_collector_1000": {
            "type": "points",
            "name": "Point Collector",
            "description": "Reach 1,000 total points",
            "rarity": "epic",
            "points_reward": 100,
            "icon": "🏆",
            "condition": {"type": "points", "threshold": 1000}
        },
        "point_collector_10000": {
            "type": "points",
            "name": "Point Collector",
            "description": "Reach 10,000 total points",
            "rarity": "legendary",
            "points_reward": 1000,
            "icon": "👑",
            "condition": {"type": "points", "threshold": 10000}
        },
        "rapid_riser": {
            "type": "points",
            "name": "Rapid Riser",
            "description": "Gain 100 points in a single day",
            "rarity": "rare",
            "points_reward": 25,
            "icon": "⚡",
            "condition": {"type": "daily_points", "threshold": 100}
        },
        
        # Jailbreak achievements
        "first_break": {
            "type": "jailbreak",
            "name": "First Break",
            "description": "Successfully complete your first jailbreak",
            "rarity": "rare",
            "points_reward": 50,
            "icon": "🎯",
            "condition": {"type": "jailbreaks", "threshold": 1}
        },
        "serial_breaker_3": {
            "type": "jailbreak",
            "name": "Serial Breaker",
            "description": "Complete 3 successful jailbreaks",
            "rarity": "epic",
            "points_reward": 100,
            "icon": "🔥",
            "condition": {"type": "jailbreaks", "threshold": 3}
        },
        "serial_breaker_5": {
            "type": "jailbreak",
            "name": "Serial Breaker",
            "description": "Complete 5 successful jailbreaks",
            "rarity": "epic",
            "points_reward": 200,
            "icon": "🔥",
            "condition": {"type": "jailbreaks", "threshold": 5}
        },
        "serial_breaker_10": {
            "type": "jailbreak",
            "name": "Serial Breaker",
            "description": "Complete 10 successful jailbreaks",
            "rarity": "legendary",
            "points_reward": 500,
            "icon": "🔥",
            "condition": {"type": "jailbreaks", "threshold": 10}
        },
        "perfect_week": {
            "type": "jailbreak",
            "name": "Perfect Week",
            "description": "Complete 7 jailbreaks in 7 days",
            "rarity": "legendary",
            "points_reward": 1000,
            "icon": "🌟",
            "condition": {"type": "jailbreaks_week", "threshold": 7}
        },
        "multiplier_master": {
            "type": "jailbreak",
            "name": "Multiplier Master",
            "description": "Reach 100x multiplier (10 jailbreaks)",
            "rarity": "legendary",
            "points_reward": 2000,
            "icon": "💫",
            "condition": {"type": "multiplier", "threshold": 100}
        },
        
        # Referral achievements
        "social_butterfly_5": {
            "type": "referral",
            "name": "Social Butterfly",
            "description": "Successfully refer 5 friends",
            "rarity": "common",
            "points_reward": 20,
            "icon": "🦋",
            "condition": {"type": "referrals", "threshold": 5}
        },
        "social_butterfly_10": {
            "type": "referral",
            "name": "Social Butterfly",
            "description": "Successfully refer 10 friends",
            "rarity": "rare",
            "points_reward": 50,
            "icon": "🦋",
            "condition": {"type": "referrals", "threshold": 10}
        },
        "social_butterfly_25": {
            "type": "referral",
            "name": "Social Butterfly",
            "description": "Successfully refer 25 friends",
            "rarity": "epic",
            "points_reward": 200,
            "icon": "🦋",
            "condition": {"type": "referrals", "threshold": 25}
        },
        "social_butterfly_50": {
            "type": "referral",
            "name": "Social Butterfly",
            "description": "Successfully refer 50 friends",
            "rarity": "legendary",
            "points_reward": 500,
            "icon": "🦋",
            "condition": {"type": "referrals", "threshold": 50}
        },
        "viral_creator": {
            "type": "referral",
            "name": "Viral Creator",
            "description": "Refer 10 people in one week",
            "rarity": "epic",
            "points_reward": 300,
            "icon": "📢",
            "condition": {"type": "referrals_week", "threshold": 10}
        },
        
        # Question achievements
        "question_master_100": {
            "type": "question",
            "name": "Question Master",
            "description": "Ask 100 questions",
            "rarity": "common",
            "points_reward": 15,
            "icon": "❓",
            "condition": {"type": "questions", "threshold": 100}
        },
        "question_master_500": {
            "type": "question",
            "name": "Question Master",
            "description": "Ask 500 questions",
            "rarity": "rare",
            "points_reward": 75,
            "icon": "❓",
            "condition": {"type": "questions", "threshold": 500}
        },
        "question_master_1000": {
            "type": "question",
            "name": "Question Master",
            "description": "Ask 1,000 questions",
            "rarity": "epic",
            "points_reward": 200,
            "icon": "❓",
            "condition": {"type": "questions", "threshold": 1000}
        },
        
        # Streak achievements
        "week_warrior": {
            "type": "streak",
            "name": "Week Warrior",
            "description": "Maintain a 7-day streak",
            "rarity": "rare",
            "points_reward": 50,
            "icon": "🔥",
            "condition": {"type": "streak", "threshold": 7}
        },
        "monthly_master": {
            "type": "streak",
            "name": "Monthly Master",
            "description": "Maintain a 30-day streak",
            "rarity": "epic",
            "points_reward": 200,
            "icon": "📅",
            "condition": {"type": "streak", "threshold": 30}
        },
        "centurion": {
            "type": "streak",
            "name": "Centurion",
            "description": "Maintain a 100-day streak",
            "rarity": "legendary",
            "points_reward": 1000,
            "icon": "💯",
            "condition": {"type": "streak", "threshold": 100}
        }
    }
    
    async def check_and_unlock_achievements(
        self, 
        session: AsyncSession, 
        user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Check user stats and unlock any new achievements
        
        Returns:
            List of newly unlocked achievements
        """
        try:
            # Get user
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return []
            
            # Get existing achievements
            existing_result = await session.execute(
                select(Achievement).where(Achievement.user_id == user_id)
            )
            existing_achievements = {a.achievement_id for a in existing_result.scalars().all()}
            
            # Get user stats
            stats = await self._get_user_stats(session, user_id)
            
            # Check each achievement definition
            newly_unlocked = []
            
            for achievement_id, definition in self.ACHIEVEMENT_DEFINITIONS.items():
                # Skip if already unlocked
                if achievement_id in existing_achievements:
                    continue
                
                # Check if condition is met
                if self._check_condition(definition["condition"], stats, user):
                    # Unlock achievement
                    achievement = Achievement(
                        user_id=user_id,
                        achievement_type=definition["type"],
                        achievement_id=achievement_id,
                        name=definition["name"],
                        description=definition["description"],
                        rarity=definition["rarity"],
                        points_reward=definition["points_reward"],
                        icon=definition["icon"],
                        unlocked_at=datetime.utcnow()
                    )
                    session.add(achievement)
                    
                    # Award points
                    user.total_points += definition["points_reward"]
                    
                    # Create milestone for celebration
                    milestone = Milestone(
                        user_id=user_id,
                        milestone_type="achievement",
                        milestone_name=definition["name"],
                        description=f"Achievement Unlocked: {definition['description']}",
                        value=definition["points_reward"],
                        celebration_shown=False
                    )
                    session.add(milestone)
                    
                    newly_unlocked.append({
                        "achievement_id": achievement_id,
                        "name": definition["name"],
                        "description": definition["description"],
                        "rarity": definition["rarity"],
                        "points_reward": definition["points_reward"],
                        "icon": definition["icon"]
                    })
                    
                    logger.info(f"🎉 User {user_id} unlocked achievement: {definition['name']}")
            
            if newly_unlocked:
                await session.commit()
            
            return newly_unlocked
        
        except Exception as e:
            logger.error(f"Error checking achievements for user {user_id}: {e}")
            await session.rollback()
            return []
    
    async def _get_user_stats(
        self, 
        session: AsyncSession, 
        user_id: int
    ) -> Dict[str, Any]:
        """Get comprehensive user stats for achievement checking"""
        try:
            # Count questions
            questions_result = await session.execute(
                select(func.count(Conversation.id))
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Conversation.message_type == 'user'
                    )
                )
            )
            question_count = questions_result.scalar() or 0
            
            # Count referrals
            referrals_result = await session.execute(
                select(func.count(Referral.id))
                .where(
                    and_(
                        Referral.referrer_id == user_id,
                        Referral.is_valid == True
                    )
                )
            )
            referral_count = referrals_result.scalar() or 0
            
            # Count jailbreaks
            jailbreaks_result = await session.execute(
                select(func.count(AttackAttempt.id))
                .where(
                    and_(
                        AttackAttempt.user_id == user_id,
                        AttackAttempt.was_successful == True
                    )
                )
            )
            jailbreak_count = jailbreaks_result.scalar() or 0
            
            # Get user
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            return {
                "points": user.total_points if user else 0,
                "questions": question_count,
                "referrals": referral_count,
                "jailbreaks": jailbreak_count,
                "multiplier": 10 ** jailbreak_count if jailbreak_count > 0 else 1,
                "streak": user.current_streak if user else 0
            }
        
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    def _check_condition(
        self, 
        condition: Dict[str, Any], 
        stats: Dict[str, Any],
        user: User
    ) -> bool:
        """Check if an achievement condition is met"""
        condition_type = condition.get("type")
        threshold = condition.get("threshold")
        
        if condition_type == "points":
            return stats.get("points", 0) >= threshold
        elif condition_type == "questions":
            return stats.get("questions", 0) >= threshold
        elif condition_type == "referrals":
            return stats.get("referrals", 0) >= threshold
        elif condition_type == "jailbreaks":
            return stats.get("jailbreaks", 0) >= threshold
        elif condition_type == "multiplier":
            return stats.get("multiplier", 1) >= threshold
        elif condition_type == "streak":
            return stats.get("streak", 0) >= threshold
        else:
            return False
    
    async def get_user_achievements(
        self, 
        session: AsyncSession, 
        user_id: int
    ) -> Dict[str, Any]:
        """Get all achievements for a user"""
        try:
            result = await session.execute(
                select(Achievement)
                .where(Achievement.user_id == user_id)
                .order_by(Achievement.unlocked_at.desc())
            )
            achievements = result.scalars().all()
            
            # Group by rarity
            by_rarity = {
                "common": [],
                "rare": [],
                "epic": [],
                "legendary": []
            }
            
            for achievement in achievements:
                by_rarity[achievement.rarity].append({
                    "id": achievement.id,
                    "achievement_id": achievement.achievement_id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "rarity": achievement.rarity,
                    "icon": achievement.icon,
                    "unlocked_at": achievement.unlocked_at.isoformat()
                })
            
            return {
                "total": len(achievements),
                "by_rarity": by_rarity,
                "all": [
                    {
                        "id": a.id,
                        "achievement_id": a.achievement_id,
                        "name": a.name,
                        "description": a.description,
                        "rarity": a.rarity,
                        "icon": a.icon,
                        "unlocked_at": a.unlocked_at.isoformat()
                    }
                    for a in achievements
                ]
            }
        
        except Exception as e:
            logger.error(f"Error getting achievements for user {user_id}: {e}")
            return {"total": 0, "by_rarity": {}, "all": []}


# Create singleton instance
achievement_service = AchievementService()

