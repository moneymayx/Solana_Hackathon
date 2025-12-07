"""
Points Service for Gamification System

Calculates and manages user points based on:
- Questions asked: 1 point per question
- Referrals: 2 points per successful referral
- Successful jailbreaks: 10x multiplier on total points

Author: Billions Bounty
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import User, Conversation, Referral, AttackAttempt
import logging

logger = logging.getLogger(__name__)


class PointsService:
    """Service for managing the gamification points system"""
    
    def __init__(self):
        self.POINTS_PER_QUESTION = 1
        self.POINTS_PER_REFERRAL = 2
        self.JAILBREAK_MULTIPLIER = 10
    
    async def calculate_user_points(
        self, 
        session: AsyncSession, 
        user_id: int
    ) -> Dict[str, int]:
        """
        Calculate all points for a user
        
        Returns:
            Dict containing:
            - question_points: Points from questions
            - referral_points: Points from referrals
            - base_points: Sum of question and referral points
            - jailbreak_count: Number of successful jailbreaks
            - total_points: Final points after multiplier
        """
        try:
            # Count questions (user messages in conversations)
            question_count_result = await session.execute(
                select(func.count(Conversation.id))
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Conversation.message_type == 'user'
                    )
                )
            )
            question_count = question_count_result.scalar() or 0
            
            # Count successful referrals (where user is the referrer)
            referral_count_result = await session.execute(
                select(func.count(Referral.id))
                .where(
                    and_(
                        Referral.referrer_id == user_id,
                        Referral.is_valid == True
                    )
                )
            )
            referral_count = referral_count_result.scalar() or 0
            
            # Count successful jailbreaks
            jailbreak_count_result = await session.execute(
                select(func.count(AttackAttempt.id))
                .where(
                    and_(
                        AttackAttempt.user_id == user_id,
                        AttackAttempt.was_successful == True
                    )
                )
            )
            jailbreak_count = jailbreak_count_result.scalar() or 0
            
            # Calculate points
            question_points = question_count * self.POINTS_PER_QUESTION
            referral_points = referral_count * self.POINTS_PER_REFERRAL
            base_points = question_points + referral_points
            
            # Apply jailbreak multiplier (each jailbreak multiplies total by 10)
            # If they have 1 jailbreak: points * 10
            # If they have 2 jailbreaks: points * 10 * 10 = points * 100
            total_points = base_points * (self.JAILBREAK_MULTIPLIER ** jailbreak_count) if jailbreak_count > 0 else base_points
            
            return {
                'question_count': question_count,
                'question_points': question_points,
                'referral_count': referral_count,
                'referral_points': referral_points,
                'base_points': base_points,
                'jailbreak_count': jailbreak_count,
                'total_points': total_points,
                'multiplier_applied': self.JAILBREAK_MULTIPLIER ** jailbreak_count if jailbreak_count > 0 else 1
            }
        
        except Exception as e:
            logger.error(f"Error calculating points for user {user_id}: {e}")
            return {
                'question_count': 0,
                'question_points': 0,
                'referral_count': 0,
                'referral_points': 0,
                'base_points': 0,
                'jailbreak_count': 0,
                'total_points': 0,
                'multiplier_applied': 1
            }
    
    async def update_user_points(
        self, 
        session: AsyncSession, 
        user_id: int
    ) -> Dict[str, Any]:
        """
        Calculate and update user's points in database
        
        Returns:
            Updated points breakdown
        """
        try:
            # Get user
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error(f"User {user_id} not found")
                return None
            
            # Calculate new points
            points_data = await self.calculate_user_points(session, user_id)
            
            # Update user record
            user.question_points = points_data['question_points']
            user.referral_points = points_data['referral_points']
            user.total_points = points_data['total_points']
            user.jailbreak_multiplier_applied = points_data['jailbreak_count']
            user.last_points_update = datetime.utcnow()
            
            await session.commit()
            
            logger.info(f"✅ Updated points for user {user_id}: {points_data['total_points']} total points")
            
            return points_data
        
        except Exception as e:
            logger.error(f"Error updating points for user {user_id}: {e}")
            await session.rollback()
            return None
    
    async def get_leaderboard(
        self, 
        session: AsyncSession, 
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get points leaderboard
        
        Args:
            limit: Number of users to return
            offset: Offset for pagination
        
        Returns:
            List of users with their points, ranked
        """
        try:
            # Get top users by total points
            result = await session.execute(
                select(User)
                .where(User.total_points > 0)
                .order_by(User.total_points.desc())
                .limit(limit)
                .offset(offset)
            )
            users = result.scalars().all()
            
            leaderboard = []
            for rank, user in enumerate(users, start=offset + 1):
                # Recalculate points to ensure freshness
                points_data = await self.calculate_user_points(session, user.id)
                
                leaderboard.append({
                    'rank': rank,
                    'user_id': user.id,
                    'wallet_address': user.wallet_address,
                    'display_name': user.display_name or f"Player {user.wallet_address[:8]}..." if user.wallet_address else f"User {user.id}",
                    'total_points': points_data['total_points'],
                    'question_points': points_data['question_points'],
                    'question_count': points_data['question_count'],
                    'referral_points': points_data['referral_points'],
                    'referral_count': points_data['referral_count'],
                    'jailbreak_count': points_data['jailbreak_count'],
                    'multiplier_applied': points_data['multiplier_applied'],
                    'tier': self._get_user_tier(points_data['total_points']),
                    'last_updated': user.last_points_update.isoformat() if user.last_points_update else None
                })
            
            return leaderboard
        
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def get_user_rank(
        self, 
        session: AsyncSession, 
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a user's current rank and position details
        
        Returns:
            Dict with rank, percentile, and points above/below surrounding users
        """
        try:
            # Get user
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            # Calculate current points
            points_data = await self.calculate_user_points(session, user_id)
            user_points = points_data['total_points']
            
            # Get user's rank
            rank_result = await session.execute(
                select(func.count(User.id))
                .where(User.total_points > user_points)
            )
            rank = rank_result.scalar() + 1
            
            # Get total users with points
            total_result = await session.execute(
                select(func.count(User.id))
                .where(User.total_points > 0)
            )
            total_users = total_result.scalar()
            
            # Calculate percentile
            percentile = ((total_users - rank + 1) / total_users * 100) if total_users > 0 else 0
            
            # Get user above (next rank)
            above_result = await session.execute(
                select(User)
                .where(User.total_points > user_points)
                .order_by(User.total_points.asc())
                .limit(1)
            )
            user_above = above_result.scalar_one_or_none()
            
            # Get user below (previous rank)
            below_result = await session.execute(
                select(User)
                .where(User.total_points < user_points)
                .order_by(User.total_points.desc())
                .limit(1)
            )
            user_below = below_result.scalar_one_or_none()
            
            return {
                'user_id': user_id,
                'rank': rank,
                'total_users': total_users,
                'percentile': round(percentile, 2),
                'points': points_data,
                'tier': self._get_user_tier(user_points),
                'points_to_next_rank': (user_above.total_points - user_points) if user_above else 0,
                'points_above_previous': (user_points - user_below.total_points) if user_below else 0,
                'next_rank_user': {
                    'display_name': user_above.display_name or f"Player {user_above.wallet_address[:8]}..." if user_above and user_above.wallet_address else None,
                    'points': user_above.total_points if user_above else None
                } if user_above else None,
                'previous_rank_user': {
                    'display_name': user_below.display_name or f"Player {user_below.wallet_address[:8]}..." if user_below and user_below.wallet_address else None,
                    'points': user_below.total_points if user_below else None
                } if user_below else None
            }
        
        except Exception as e:
            logger.error(f"Error getting user rank for {user_id}: {e}")
            return None
    
    def _get_user_tier(self, total_points: int) -> str:
        """
        Determine user tier based on total points
        
        Tiers:
        - Legendary: 10,000+ points
        - Diamond: 5,000-9,999 points
        - Platinum: 1,000-4,999 points
        - Gold: 500-999 points
        - Silver: 100-499 points
        - Bronze: 10-99 points
        - Beginner: 0-9 points
        """
        if total_points >= 10000:
            return "legendary"
        elif total_points >= 5000:
            return "diamond"
        elif total_points >= 1000:
            return "platinum"
        elif total_points >= 500:
            return "gold"
        elif total_points >= 100:
            return "silver"
        elif total_points >= 10:
            return "bronze"
        else:
            return "beginner"
    
    async def recalculate_all_user_points(
        self, 
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Recalculate points for all users (admin/maintenance function)
        
        Returns:
            Summary of recalculation
        """
        try:
            # Get all users
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            updated_count = 0
            errors = []
            
            for user in users:
                try:
                    await self.update_user_points(session, user.id)
                    updated_count += 1
                except Exception as e:
                    logger.error(f"Error updating points for user {user.id}: {e}")
                    errors.append({'user_id': user.id, 'error': str(e)})
            
            return {
                'total_users': len(users),
                'updated': updated_count,
                'errors': len(errors),
                'error_details': errors[:10]  # Limit error details to first 10
            }
        
        except Exception as e:
            logger.error(f"Error recalculating all user points: {e}")
            return {
                'total_users': 0,
                'updated': 0,
                'errors': 1,
                'error_details': [str(e)]
            }


# Create singleton instance
points_service = PointsService()

