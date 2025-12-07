"""
Streak Service for Daily Activity Tracking

Tracks consecutive days of user activity and awards bonus points for maintaining streaks.

Author: Billions Bounty
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import User, Milestone
import logging

logger = logging.getLogger(__name__)


class StreakService:
    """Service for managing daily activity streaks"""
    
    def __init__(self):
        # Streak bonus points configuration
        self.STREAK_BONUSES = {
            3: {"points": 5, "name": "3-Day Streak"},
            7: {"points": 15, "name": "Week Warrior"},
            30: {"points": 100, "name": "Monthly Master"},
            100: {"points": 500, "name": "Centurion"}
        }
    
    async def record_activity(
        self, 
        session: AsyncSession, 
        user_id: int
    ) -> Dict[str, Any]:
        """
        Record user activity for today and update streak
        
        Returns:
            Dict with streak info and any bonuses earned
        """
        try:
            # Get user
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            today = date.today()
            last_activity = user.last_activity_date.date() if user.last_activity_date else None
            
            # Check if this is a new day
            if last_activity == today:
                # Already recorded today, return current streak
                return {
                    "current_streak": user.current_streak,
                    "longest_streak": user.longest_streak,
                    "bonus_earned": 0,
                    "bonus_name": None
                }
            
            # Calculate new streak
            if last_activity is None:
                # First activity ever
                new_streak = 1
            elif last_activity == today - timedelta(days=1):
                # Consecutive day - increment streak
                new_streak = user.current_streak + 1
            else:
                # Streak broken - reset to 1
                new_streak = 1
                logger.info(f"Streak broken for user {user_id}. Previous streak: {user.current_streak}")
            
            # Update user
            user.current_streak = new_streak
            user.last_activity_date = datetime.utcnow()
            
            # Update longest streak if needed
            if new_streak > user.longest_streak:
                user.longest_streak = new_streak
            
            # Check for streak bonuses
            bonus_points = 0
            bonus_name = None
            
            if new_streak in self.STREAK_BONUSES:
                bonus_info = self.STREAK_BONUSES[new_streak]
                bonus_points = bonus_info["points"]
                bonus_name = bonus_info["name"]
                
                # Add bonus to user's points
                user.streak_bonus_points += bonus_points
                user.total_points += bonus_points
                
                # Create milestone for celebration
                milestone = Milestone(
                    user_id=user_id,
                    milestone_type="streak",
                    milestone_name=bonus_name,
                    description=f"Maintained a {new_streak}-day streak!",
                    value=new_streak,
                    celebration_shown=False
                )
                session.add(milestone)
                
                logger.info(f"🎉 User {user_id} earned {bonus_points} bonus points for {bonus_name}!")
            
            await session.commit()
            
            return {
                "current_streak": new_streak,
                "longest_streak": user.longest_streak,
                "bonus_earned": bonus_points,
                "bonus_name": bonus_name,
                "milestone_created": bonus_points > 0
            }
        
        except Exception as e:
            logger.error(f"Error recording activity for user {user_id}: {e}")
            await session.rollback()
            return None
    
    async def get_streak_info(
        self, 
        session: AsyncSession, 
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get current streak information for a user"""
        try:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            today = date.today()
            last_activity = user.last_activity_date.date() if user.last_activity_date else None
            
            # Check if streak is still valid
            is_streak_active = False
            if last_activity:
                if last_activity == today:
                    is_streak_active = True
                elif last_activity == today - timedelta(days=1):
                    is_streak_active = True
            
            # Calculate days until next bonus
            next_bonus = None
            next_bonus_days = None
            for streak_days in sorted(self.STREAK_BONUSES.keys()):
                if user.current_streak < streak_days:
                    next_bonus = self.STREAK_BONUSES[streak_days]
                    next_bonus_days = streak_days - user.current_streak
                    break
            
            return {
                "current_streak": user.current_streak if is_streak_active else 0,
                "longest_streak": user.longest_streak,
                "total_bonus_points": user.streak_bonus_points,
                "is_active": is_streak_active,
                "last_activity_date": user.last_activity_date.isoformat() if user.last_activity_date else None,
                "next_bonus": next_bonus,
                "days_until_next_bonus": next_bonus_days
            }
        
        except Exception as e:
            logger.error(f"Error getting streak info for user {user_id}: {e}")
            return None


# Create singleton instance
streak_service = StreakService()

