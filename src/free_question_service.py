"""
Free Question Service - Handles anonymous and referral-based free questions
"""
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from .models import User, FreeQuestions, Referral, ReferralCode
from .repositories import UserRepository

class FreeQuestionService:
    """Service for managing free question allocation and usage"""
    
    # Constants
    ANONYMOUS_FREE_QUESTIONS = 2
    REFERRAL_FREE_QUESTIONS = 5
    MAX_ANONYMOUS_QUESTIONS = 2
    
    def __init__(self):
        self.user_repo = None
    
    async def check_user_question_eligibility(
        self, 
        session: AsyncSession, 
        user_id: int, 
        is_anonymous: bool = False,
        referral_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check if user can ask questions and what type"""
        
        user = await self._get_user(session, user_id)
        if not user:
            return {"eligible": False, "error": "User not found"}
        
        # Check if user is anonymous (no email, no wallet)
        is_anonymous_user = not user.email and not user.wallet_address
        
        if is_anonymous_user:
            return await self._check_anonymous_eligibility(session, user)
        else:
            return await self._check_registered_eligibility(session, user, referral_code)
    
    async def _check_anonymous_eligibility(self, session: AsyncSession, user: User) -> Dict[str, Any]:
        """Check eligibility for anonymous users"""
        
        # Check if user has already used their 2 free questions
        if user.anonymous_free_questions_used >= self.MAX_ANONYMOUS_QUESTIONS:
            return {
                "eligible": False,
                "type": "signup_required",
                "message": "You've used your 2 free questions. Please sign up to continue.",
                "questions_used": user.anonymous_free_questions_used,
                "questions_remaining": 0
            }
        
        # Check if user has used anonymous questions before
        if user.has_used_anonymous_questions:
            return {
                "eligible": False,
                "type": "signup_required", 
                "message": "You've already used your free questions. Please sign up to continue.",
                "questions_used": user.anonymous_free_questions_used,
                "questions_remaining": 0
            }
        
        # User can ask questions
        remaining = self.MAX_ANONYMOUS_QUESTIONS - user.anonymous_free_questions_used
        return {
            "eligible": True,
            "type": "anonymous",
            "message": f"You have {remaining} free questions remaining.",
            "questions_used": user.anonymous_free_questions_used,
            "questions_remaining": remaining
        }
    
    async def _check_registered_eligibility(self, session: AsyncSession, user: User, referral_code: Optional[str] = None) -> Dict[str, Any]:
        """Check eligibility for registered users"""
        
        # Get user's free questions
        free_questions = await self._get_user_free_questions(session, user.id)
        
        if free_questions and free_questions.questions_remaining > 0:
            return {
                "eligible": True,
                "type": "free_questions",
                "message": f"You have {free_questions.questions_remaining} free questions remaining.",
                "questions_used": free_questions.questions_used,
                "questions_remaining": free_questions.questions_remaining,
                "source": free_questions.source
            }
        
        # Check if this is a referral signup
        if referral_code:
            referral_code_obj = await self._get_referral_code(session, referral_code)
            if referral_code_obj and referral_code_obj.is_active:
                return {
                    "eligible": True,
                    "type": "referral_signup",
                    "message": "Welcome! You have 5 free questions from your referral.",
                    "questions_remaining": self.REFERRAL_FREE_QUESTIONS,
                    "referral_code": referral_code
                }
        
        # No free questions available
        return {
            "eligible": False,
            "type": "payment_required",
            "message": "No free questions available. Please pay $10 for your next question or refer friends to earn free questions.",
            "questions_remaining": 0
        }
    
    async def use_free_question(
        self, 
        session: AsyncSession, 
        user_id: int, 
        question_type: str = "anonymous"
    ) -> Dict[str, Any]:
        """Use a free question"""
        
        user = await self._get_user(session, user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        if question_type == "anonymous":
            return await self._use_anonymous_question(session, user)
        else:
            return await self._use_registered_question(session, user)
    
    async def _use_anonymous_question(self, session: AsyncSession, user: User) -> Dict[str, Any]:
        """Use an anonymous free question"""
        
        if user.anonymous_free_questions_used >= self.MAX_ANONYMOUS_QUESTIONS:
            return {
                "success": False,
                "error": "No anonymous questions remaining",
                "requires_signup": True
            }
        
        # Update user's anonymous question count
        await session.execute(
            update(User)
            .where(User.id == user.id)
            .values(
                anonymous_free_questions_used=User.anonymous_free_questions_used + 1,
                has_used_anonymous_questions=True,
                last_active=datetime.utcnow()
            )
        )
        await session.commit()
        
        remaining = self.MAX_ANONYMOUS_QUESTIONS - (user.anonymous_free_questions_used + 1)
        
        return {
            "success": True,
            "questions_remaining": remaining,
            "requires_signup": remaining == 0,
            "message": f"Question used. {remaining} anonymous questions remaining." if remaining > 0 else "All anonymous questions used. Please sign up to continue."
        }
    
    async def _use_registered_question(self, session: AsyncSession, user: User) -> Dict[str, Any]:
        """Use a registered user's free question"""
        
        free_questions = await self._get_user_free_questions(session, user.id)
        if not free_questions or free_questions.questions_remaining <= 0:
            return {
                "success": False,
                "error": "No free questions remaining",
                "requires_payment": True
            }
        
        # Update free questions
        await session.execute(
            update(FreeQuestions)
            .where(FreeQuestions.id == free_questions.id)
            .values(
                questions_used=FreeQuestions.questions_used + 1,
                questions_remaining=FreeQuestions.questions_remaining - 1,
                last_used=datetime.utcnow()
            )
        )
        await session.commit()
        
        return {
            "success": True,
            "questions_remaining": free_questions.questions_remaining - 1,
            "message": f"Question used. {free_questions.questions_remaining - 1} free questions remaining."
        }
    
    async def grant_referral_questions(
        self, 
        session: AsyncSession, 
        user_id: int, 
        referral_id: int
    ) -> Dict[str, Any]:
        """Grant 5 free questions to a user from a referral"""
        
        # Check if user already has free questions from this referral
        existing = await session.execute(
            select(FreeQuestions)
            .where(
                and_(
                    FreeQuestions.user_id == user_id,
                    FreeQuestions.referral_id == referral_id
                )
            )
        )
        if existing.scalar_one_or_none():
            return {"success": False, "error": "User already has questions from this referral"}
        
        # Create free questions record
        free_questions = FreeQuestions(
            user_id=user_id,
            source="referral_signup",
            referral_id=referral_id,
            questions_earned=self.REFERRAL_FREE_QUESTIONS,
            questions_remaining=self.REFERRAL_FREE_QUESTIONS
        )
        session.add(free_questions)
        await session.commit()
        
        return {
            "success": True,
            "questions_granted": self.REFERRAL_FREE_QUESTIONS,
            "message": f"Granted {self.REFERRAL_FREE_QUESTIONS} free questions from referral"
        }
    
    async def grant_referrer_questions(
        self, 
        session: AsyncSession, 
        referrer_id: int, 
        referral_id: int
    ) -> Dict[str, Any]:
        """Grant 5 free questions to referrer when someone uses their code"""
        
        # Create free questions record for referrer
        free_questions = FreeQuestions(
            user_id=referrer_id,
            source="referral_bonus",
            referral_id=referral_id,
            questions_earned=self.REFERRAL_FREE_QUESTIONS,
            questions_remaining=self.REFERRAL_FREE_QUESTIONS
        )
        session.add(free_questions)
        await session.commit()
        
        return {
            "success": True,
            "questions_granted": self.REFERRAL_FREE_QUESTIONS,
            "message": f"Granted {self.REFERRAL_FREE_QUESTIONS} free questions for successful referral"
        }
    
    async def _get_user(self, session: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def _get_user_free_questions(self, session: AsyncSession, user_id: int) -> Optional[FreeQuestions]:
        """Get user's active free questions"""
        result = await session.execute(
            select(FreeQuestions)
            .where(
                and_(
                    FreeQuestions.user_id == user_id,
                    FreeQuestions.questions_remaining > 0
                )
            )
            .order_by(FreeQuestions.created_at.desc())
        )
        return result.scalar_one_or_none()
    
    async def _get_referral_code(self, session: AsyncSession, code: str) -> Optional[ReferralCode]:
        """Get referral code by code string"""
        result = await session.execute(
            select(ReferralCode)
            .where(
                and_(
                    ReferralCode.referral_code == code,
                    ReferralCode.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()

# Global instance
free_question_service = FreeQuestionService()
