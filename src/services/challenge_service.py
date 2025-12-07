"""
Challenge Service for Quest/Challenge System

Manages challenges, tracks user progress, and awards rewards upon completion.

Author: Billions Bounty
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import User, Challenge, ChallengeProgress, Conversation, Referral, AttackAttempt, Milestone
import logging

logger = logging.getLogger(__name__)


class ChallengeService:
    """Service for managing challenges and quests"""
    
    async def get_active_challenges(
        self, 
        session: AsyncSession,
        challenge_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all active challenges
        
        Args:
            challenge_type: Optional filter by type ('daily', 'weekly', 'event')
        """
        try:
            query = select(Challenge).where(
                and_(
                    Challenge.is_active == True,
                    or_(
                        Challenge.end_date == None,
                        Challenge.end_date > datetime.utcnow()
                    )
                )
            )
            
            if challenge_type:
                query = query.where(Challenge.challenge_type == challenge_type)
            
            result = await session.execute(query.order_by(Challenge.start_date.desc()))
            challenges = result.scalars().all()
            
            return [
                {
                    "id": c.id,
                    "challenge_type": c.challenge_type,
                    "name": c.name,
                    "description": c.description,
                    "objective_type": c.objective_type,
                    "objective_target": c.objective_target,
                    "reward_points": c.reward_points,
                    "start_date": c.start_date.isoformat(),
                    "end_date": c.end_date.isoformat() if c.end_date else None,
                    "time_remaining": (c.end_date - datetime.utcnow()).total_seconds() if c.end_date else None
                }
                for c in challenges
            ]
        
        except Exception as e:
            logger.error(f"Error getting active challenges: {e}")
            return []
    
    async def get_user_challenges(
        self, 
        session: AsyncSession, 
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get all challenges with user's progress
        
        Returns:
            Dict with active challenges and user progress
        """
        try:
            # Get active challenges
            active_challenges = await self.get_active_challenges(session)
            
            # Get user progress for all challenges
            progress_result = await session.execute(
                select(ChallengeProgress)
                .where(ChallengeProgress.user_id == user_id)
                .where(ChallengeProgress.completed_at == None)  # Only incomplete
            )
            user_progress = {p.challenge_id: p for p in progress_result.scalars().all()}
            
            # Combine challenges with progress
            challenges_with_progress = []
            for challenge in active_challenges:
                progress = user_progress.get(challenge["id"])
                
                challenges_with_progress.append({
                    **challenge,
                    "progress": {
                        "current": progress.current_progress if progress else 0,
                        "target": challenge["objective_target"],
                        "percentage": round(
                            (progress.current_progress / challenge["objective_target"] * 100) 
                            if progress else 0, 
                            1
                        ),
                        "completed": progress.completed_at is not None if progress else False,
                        "reward_claimed": progress.reward_claimed if progress else False
                    }
                })
            
            return {
                "challenges": challenges_with_progress,
                "total_active": len(challenges_with_progress)
            }
        
        except Exception as e:
            logger.error(f"Error getting user challenges for {user_id}: {e}")
            return {"challenges": [], "total_active": 0}
    
    async def update_challenge_progress(
        self, 
        session: AsyncSession, 
        user_id: int,
        activity_type: str,  # 'question', 'referral', 'jailbreak', 'points'
        amount: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Update progress on all relevant challenges for a user activity
        
        Returns:
            List of completed challenges with rewards
        """
        try:
            # Map activity types to challenge objective types
            activity_mapping = {
                "question": "questions",
                "referral": "referrals",
                "jailbreak": "jailbreaks",
                "points": "points"
            }
            
            objective_type = activity_mapping.get(activity_type)
            if not objective_type:
                return []
            
            # Get active challenges matching this activity
            result = await session.execute(
                select(Challenge).where(
                    and_(
                        Challenge.is_active == True,
                        Challenge.objective_type == objective_type,
                        or_(
                            Challenge.end_date == None,
                            Challenge.end_date > datetime.utcnow()
                        )
                    )
                )
            )
            relevant_challenges = result.scalars().all()
            
            completed_challenges = []
            
            for challenge in relevant_challenges:
                # Get or create progress
                progress_result = await session.execute(
                    select(ChallengeProgress).where(
                        and_(
                            ChallengeProgress.challenge_id == challenge.id,
                            ChallengeProgress.user_id == user_id
                        )
                    )
                )
                progress = progress_result.scalar_one_or_none()
                
                if not progress:
                    progress = ChallengeProgress(
                        challenge_id=challenge.id,
                        user_id=user_id,
                        current_progress=0,
                        target=challenge.objective_target
                    )
                    session.add(progress)
                
                # Skip if already completed
                if progress.completed_at:
                    continue
                
                # Update progress
                progress.current_progress += amount
                progress.updated_at = datetime.utcnow()
                
                # Check if completed
                if progress.current_progress >= challenge.objective_target:
                    progress.completed_at = datetime.utcnow()
                    
                    # Award points
                    user_result = await session.execute(
                        select(User).where(User.id == user_id)
                    )
                    user = user_result.scalar_one_or_none()
                    
                    if user:
                        user.total_points += challenge.reward_points
                        
                        # Create milestone for celebration
                        milestone = Milestone(
                            user_id=user_id,
                            milestone_type="challenge_complete",
                            milestone_name=challenge.name,
                            description=f"Completed: {challenge.description}",
                            value=challenge.reward_points,
                            celebration_shown=False
                        )
                        session.add(milestone)
                        
                        completed_challenges.append({
                            "challenge_id": challenge.id,
                            "challenge_name": challenge.name,
                            "reward_points": challenge.reward_points,
                            "milestone_created": True
                        })
                        
                        logger.info(f"🎉 User {user_id} completed challenge '{challenge.name}' and earned {challenge.reward_points} points!")
            
            await session.commit()
            return completed_challenges
        
        except Exception as e:
            logger.error(f"Error updating challenge progress for user {user_id}: {e}")
            await session.rollback()
            return []
    
    async def create_daily_challenges(
        self, 
        session: AsyncSession
    ) -> List[Challenge]:
        """
        Create daily challenges (should be called daily via cron)
        
        Returns:
            List of created challenges
        """
        try:
            # Check if daily challenges already exist for today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            existing = await session.execute(
                select(Challenge).where(
                    and_(
                        Challenge.challenge_type == "daily",
                        Challenge.start_date >= today_start,
                        Challenge.start_date < today_end
                    )
                )
            )
            
            if existing.scalars().first():
                logger.info("Daily challenges already created for today")
                return []
            
            # Create daily challenges
            daily_challenges = [
                Challenge(
                    challenge_type="daily",
                    name="Ask 5 Questions",
                    description="Ask 5 questions today",
                    objective_type="questions",
                    objective_target=5,
                    reward_points=10,
                    start_date=today_start,
                    end_date=today_end,
                    is_active=True
                ),
                Challenge(
                    challenge_type="daily",
                    name="Refer a Friend",
                    description="Refer 1 friend today",
                    objective_type="referrals",
                    objective_target=1,
                    reward_points=5,
                    start_date=today_start,
                    end_date=today_end,
                    is_active=True
                ),
                Challenge(
                    challenge_type="daily",
                    name="Jailbreak Attempt",
                    description="Attempt a jailbreak today",
                    objective_type="jailbreaks",
                    objective_target=1,
                    reward_points=3,
                    start_date=today_start,
                    end_date=today_end,
                    is_active=True
                )
            ]
            
            for challenge in daily_challenges:
                session.add(challenge)
            
            await session.commit()
            
            logger.info(f"Created {len(daily_challenges)} daily challenges")
            return daily_challenges
        
        except Exception as e:
            logger.error(f"Error creating daily challenges: {e}")
            await session.rollback()
            return []


# Create singleton instance
challenge_service = ChallengeService()

