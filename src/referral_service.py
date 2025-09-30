"""
Referral Service - Research Funding Referral System
Implements the referral system for research funding
"""
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from .models import User, ReferralCode, Referral, FreeQuestions, PaymentTransaction

class ReferralService:
    """Service for managing the referral system"""
    
    def __init__(self):
        self.free_questions_per_referral = 5
        self.referral_code_length = 6
    
    def _generate_referral_code(self) -> str:
        """Generate a unique referral code"""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(self.referral_code_length))
    
    async def get_or_create_referral_code(self, session: AsyncSession, user_id: int) -> ReferralCode:
        """Get or create a referral code for a user"""
        # Check if user already has a referral code
        result = await session.execute(
            select(ReferralCode).where(ReferralCode.user_id == user_id)
        )
        referral_code = result.scalar_one_or_none()
        
        if not referral_code:
            # Generate unique referral code
            while True:
                code = self._generate_referral_code()
                # Check if code already exists
                existing = await session.execute(
                    select(ReferralCode).where(ReferralCode.referral_code == code)
                )
                if not existing.scalar_one_or_none():
                    break
            
            # Create new referral code
            referral_code = ReferralCode(
                user_id=user_id,
                referral_code=code,
                is_active=True
            )
            session.add(referral_code)
            await session.commit()
            await session.refresh(referral_code)
        
        return referral_code
    
    async def get_referral_code_by_code(self, session: AsyncSession, code: str) -> Optional[ReferralCode]:
        """Get referral code by code string"""
        result = await session.execute(
            select(ReferralCode).where(
                and_(
                    ReferralCode.referral_code == code,
                    ReferralCode.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def process_referral_signup(self, session: AsyncSession, referee_user_id: int, 
                                    referral_code: str, wallet_address: Optional[str] = None,
                                    email: Optional[str] = None) -> Dict[str, Any]:
        """Process a referral signup when a new user makes their first deposit"""
        
        # Get the referral code
        ref_code = await self.get_referral_code_by_code(session, referral_code)
        if not ref_code:
            return {
                "success": False,
                "error": "Invalid referral code"
            }
        
        # Check if referee is trying to refer themselves
        if ref_code.user_id == referee_user_id:
            return {
                "success": False,
                "error": "Cannot refer yourself"
            }
        
        # Check if this referee has already been referred
        existing_referral = await session.execute(
            select(Referral).where(Referral.referee_id == referee_user_id)
        )
        if existing_referral.scalar_one_or_none():
            return {
                "success": False,
                "error": "User has already been referred"
            }
        
        # Check for wallet/email conflicts
        conflict_check = await self._check_referral_conflicts(session, ref_code.user_id, wallet_address, email)
        if conflict_check["has_conflict"]:
            return {
                "success": False,
                "error": conflict_check["reason"]
            }
        
        # Create referral record
        referral = Referral(
            referrer_id=ref_code.user_id,
            referee_id=referee_user_id,
            referral_code_id=ref_code.id,
            is_valid=True
        )
        session.add(referral)
        await session.commit()
        await session.refresh(referral)
        
        # Award free questions to both referrer and referee
        await self._award_referral_questions(session, ref_code.user_id, referee_user_id, referral.id)
        
        return {
            "success": True,
            "referral_id": referral.id,
            "referrer_id": ref_code.user_id,
            "referee_id": referee_user_id,
            "free_questions_awarded": self.free_questions_per_referral
        }
    
    async def _check_referral_conflicts(self, session: AsyncSession, referrer_id: int, 
                                      wallet_address: Optional[str], email: Optional[str]) -> Dict[str, Any]:
        """Check for wallet or email conflicts between referrer and referee"""
        
        # Get referrer's wallet address
        referrer_result = await session.execute(
            select(User).where(User.id == referrer_id)
        )
        referrer = referrer_result.scalar_one_or_none()
        
        if not referrer:
            return {"has_conflict": True, "reason": "Referrer not found"}
        
        # Check wallet address conflict
        if wallet_address and referrer.wallet_address == wallet_address:
            return {"has_conflict": True, "reason": "Cannot refer wallet connected to your account"}
        
        # Check email conflict (if email is provided and we have a way to track it)
        # This would need to be implemented based on your email tracking system
        # For now, we'll skip email conflict checking
        
        return {"has_conflict": False, "reason": None}
    
    async def _award_referral_questions(self, session: AsyncSession, referrer_id: int, 
                                      referee_id: int, referral_id: int) -> None:
        """Award free questions to both referrer and referee"""
        
        # Award questions to referrer
        referrer_questions = FreeQuestions(
            user_id=referrer_id,
            source="referral_bonus",
            referral_id=referral_id,
            questions_earned=self.free_questions_per_referral,
            questions_remaining=self.free_questions_per_referral
        )
        session.add(referrer_questions)
        
        # Award questions to referee
        referee_questions = FreeQuestions(
            user_id=referee_id,
            source="referral_signup",
            referral_id=referral_id,
            questions_earned=self.free_questions_per_referral,
            questions_remaining=self.free_questions_per_referral
        )
        session.add(referee_questions)
        
        await session.commit()
    
    async def get_user_free_questions(self, session: AsyncSession, user_id: int) -> int:
        """Get total free questions available for a user"""
        result = await session.execute(
            select(FreeQuestions).where(
                and_(
                    FreeQuestions.user_id == user_id,
                    FreeQuestions.questions_remaining > 0,
                    or_(
                        FreeQuestions.expires_at.is_(None),
                        FreeQuestions.expires_at > datetime.utcnow()
                    )
                )
            )
        )
        free_questions = result.scalars().all()
        
        total_remaining = sum(fq.questions_remaining for fq in free_questions)
        return total_remaining
    
    async def use_free_question(self, session: AsyncSession, user_id: int) -> bool:
        """Use one free question for a user"""
        # Get available free questions
        result = await session.execute(
            select(FreeQuestions).where(
                and_(
                    FreeQuestions.user_id == user_id,
                    FreeQuestions.questions_remaining > 0,
                    or_(
                        FreeQuestions.expires_at.is_(None),
                        FreeQuestions.expires_at > datetime.utcnow()
                    )
                )
            ).order_by(FreeQuestions.created_at.asc())
        )
        free_question = result.scalar_one_or_none()
        
        if not free_question:
            return False
        
        # Use one question
        free_question.questions_used += 1
        free_question.questions_remaining -= 1
        
        await session.commit()
        return True
    
    async def get_referral_stats(self, session: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Get referral statistics for a user"""
        # Get referral code
        referral_code_result = await session.execute(
            select(ReferralCode).where(ReferralCode.user_id == user_id)
        )
        referral_code = referral_code_result.scalar_one_or_none()
        
        if not referral_code:
            return {
                "referral_code": None,
                "total_referrals": 0,
                "total_free_questions_earned": 0,
                "total_free_questions_used": 0,
                "free_questions_remaining": 0
            }
        
        # Get referral count
        referrals_result = await session.execute(
            select(Referral).where(Referral.referrer_id == user_id)
        )
        referrals = referrals_result.scalars().all()
        
        # Get free questions stats
        free_questions_result = await session.execute(
            select(FreeQuestions).where(FreeQuestions.user_id == user_id)
        )
        free_questions = free_questions_result.scalars().all()
        
        total_earned = sum(fq.questions_earned for fq in free_questions)
        total_used = sum(fq.questions_used for fq in free_questions)
        total_remaining = sum(fq.questions_remaining for fq in free_questions)
        
        return {
            "referral_code": referral_code.referral_code,
            "total_referrals": len(referrals),
            "total_free_questions_earned": total_earned,
            "total_free_questions_used": total_used,
            "free_questions_remaining": total_remaining
        }
    
    async def get_referral_leaderboard(self, session: AsyncSession, limit: int = 50) -> List[Dict[str, Any]]:
        """Get referral leaderboard"""
        result = await session.execute(
            select(
                User.id,
                User.wallet_address,
                User.display_name,
                ReferralCode.referral_code,
                FreeQuestions.questions_earned.label('total_questions_earned')
            )
            .join(ReferralCode, User.id == ReferralCode.user_id)
            .join(FreeQuestions, User.id == FreeQuestions.user_id)
            .where(FreeQuestions.source == "referral_bonus")
            .group_by(User.id, User.wallet_address, User.display_name, ReferralCode.referral_code)
            .order_by(FreeQuestions.questions_earned.desc())
            .limit(limit)
        )
        
        leaderboard = []
        for row in result.all():
            leaderboard.append({
                "user_id": row.id,
                "wallet_address": row.wallet_address,
                "display_name": row.display_name or f"Researcher {row.wallet_address[:8]}...",
                "referral_code": row.referral_code,
                "total_questions_earned": row.total_questions_earned
            })
        
        return leaderboard
