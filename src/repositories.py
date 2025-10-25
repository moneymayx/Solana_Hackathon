"""
Repository layer for database operations
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from sqlalchemy.orm import selectinload
from .models import User, Conversation, AttackAttempt, Transaction, PrizePool, SecurityEvent, BountyState, BountyEntry, BlacklistedPhrase, Bounty, FreeQuestionUsage

class UserRepository:
    """Repository for user operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_user(self, session_id: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None, 
                         email: Optional[str] = None, password_hash: Optional[str] = None, 
                         display_name: Optional[str] = None) -> User:
        """Create a new user"""
        user = User(
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            email=email,
            password_hash=password_hash,
            display_name=display_name
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_user_by_session(self, session_id: str) -> Optional[User]:
        """Get user by session ID"""
        result = await self.session.execute(
            select(User).where(User.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def update_user_activity(self, user_id: int, increment_attempts: bool = False) -> None:
        """Update user's last activity and optionally increment attempts"""
        update_data = {"last_active": datetime.utcnow()}
        if increment_attempts:
            update_data["total_attempts"] = User.total_attempts + 1
        
        await self.session.execute(
            update(User).where(User.id == user_id).values(**update_data)
        )
        await self.session.commit()
    
    async def get_user_attempt_count(self, user_id: int) -> int:
        """Get the total number of attempts for a user"""
        result = await self.session.execute(
            select(User.total_attempts).where(User.id == user_id)
        )
        return result.scalar_one_or_none() or 0
    
    async def update_user_wallet(self, user_id: int, wallet_address: str) -> None:
        """Update user's wallet address"""
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                wallet_address=wallet_address,
                wallet_connected_at=datetime.utcnow()
            )
        )
        await self.session.commit()
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()


class AttackAttemptRepository:
    """Repository for attack attempt operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def log_attack_attempt(self, user_id: int, attempt_type: str, message_content: str,
                                ai_response: str, threat_score: float = 0.0,
                                was_successful: bool = False, ip_address: Optional[str] = None) -> AttackAttempt:
        """Log a potential attack attempt"""
        attack = AttackAttempt(
            user_id=user_id,
            attempt_type=attempt_type,
            message_content=message_content,
            ai_response=ai_response,
            threat_score=threat_score,
            was_successful=was_successful,
            ip_address=ip_address
        )
        self.session.add(attack)
        await self.session.commit()
        await self.session.refresh(attack)
        return attack
    
    async def get_recent_attacks(self, limit: int = 50) -> List[AttackAttempt]:
        """Get recent attack attempts"""
        result = await self.session.execute(
            select(AttackAttempt)
            .order_by(desc(AttackAttempt.timestamp))
            .limit(limit)
        )
        return result.scalars().all()

class PrizePoolRepository:
    """Repository for prize pool operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_current_prize_pool(self) -> Optional[PrizePool]:
        """Get the current prize pool status"""
        result = await self.session.execute(
            select(PrizePool).order_by(desc(PrizePool.last_updated)).limit(1)
        )
        return result.scalar_one_or_none()
    
    async def initialize_prize_pool(self) -> PrizePool:
        """Initialize the prize pool if it doesn't exist"""
        prize_pool = PrizePool()
        self.session.add(prize_pool)
        await self.session.commit()
        await self.session.refresh(prize_pool)
        return prize_pool
    
    async def update_prize_pool(self, contribution: float) -> PrizePool:
        """Update the prize pool with a new contribution"""
        prize_pool = await self.get_current_prize_pool()
        if not prize_pool:
            prize_pool = await self.initialize_prize_pool()
        
        prize_pool.current_amount += contribution
        prize_pool.total_contributions += contribution
        prize_pool.total_queries += 1
        prize_pool.last_updated = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(prize_pool)
        return prize_pool
    
    async def calculate_next_query_cost(self) -> float:
        """Calculate the cost for the next query"""
        prize_pool = await self.get_current_prize_pool()
        if not prize_pool:
            return 10.0  # Base cost
        
        # Calculate escalated cost: base * (1 + escalation_rate) ^ total_queries
        escalated_cost = prize_pool.base_query_cost * ((1 + prize_pool.escalation_rate) ** prize_pool.total_queries)
        return min(escalated_cost, prize_pool.max_query_cost)

class SecurityEventRepository:
    """Repository for security event operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def log_security_event(self, event_type: str, severity: str, description: str,
                                ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                                session_id: Optional[str] = None, additional_data: Optional[str] = None) -> SecurityEvent:
        """Log a security event"""
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            additional_data=additional_data
        )
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

class BlacklistedPhraseRepository:
    """Repository for managing blacklisted phrases"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_blacklisted_phrase(self, phrase: str, original_message: str, successful_user_id: int) -> BlacklistedPhrase:
        """Add a new blacklisted phrase"""
        blacklisted_phrase = BlacklistedPhrase(
            phrase=phrase,
            original_message=original_message,
            successful_user_id=successful_user_id
        )
        self.session.add(blacklisted_phrase)
        await self.session.commit()
        await self.session.refresh(blacklisted_phrase)
        return blacklisted_phrase
    
    async def is_phrase_blacklisted(self, message: str) -> bool:
        """Check if a message contains any blacklisted phrases"""
        # Get all active blacklisted phrases
        result = await self.session.execute(
            select(BlacklistedPhrase.phrase)
            .where(BlacklistedPhrase.is_active == True)
        )
        blacklisted_phrases = result.scalars().all()
        
        # Check if message contains any blacklisted phrase
        message_lower = message.lower()
        for phrase in blacklisted_phrases:
            if phrase.lower() in message_lower:
                return True
        return False
    
    async def get_all_blacklisted_phrases(self) -> List[BlacklistedPhrase]:
        """Get all active blacklisted phrases"""
        result = await self.session.execute(
            select(BlacklistedPhrase)
            .where(BlacklistedPhrase.is_active == True)
            .order_by(BlacklistedPhrase.created_at.desc())
        )
        return result.scalars().all()
    
    async def deactivate_phrase(self, phrase_id: int) -> bool:
        """Deactivate a blacklisted phrase"""
        result = await self.session.execute(
            update(BlacklistedPhrase)
            .where(BlacklistedPhrase.id == phrase_id)
            .values(is_active=False)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def reactivate_phrase(self, phrase_id: int) -> bool:
        """Reactivate a blacklisted phrase"""
        result =         await self.session.execute(
            update(BlacklistedPhrase)
            .where(BlacklistedPhrase.id == phrase_id)
            .values(is_active=True)
        )
        await self.session.commit()
        return result.rowcount > 0

class BountyRepository:
    """Repository for bounty operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_bounties(self) -> List[Bounty]:
        """Get all active bounties"""
        result = await self.session.execute(
            select(Bounty).where(Bounty.is_active == True).order_by(Bounty.created_at)
        )
        return list(result.scalars().all())
    
    async def get_bounty_by_id(self, bounty_id: int) -> Optional[Bounty]:
        """Get bounty by ID"""
        result = await self.session.execute(
            select(Bounty).where(Bounty.id == bounty_id)
        )
        return result.scalar_one_or_none()
    
    async def get_bounty_by_provider(self, llm_provider: str) -> Optional[Bounty]:
        """Get bounty by LLM provider"""
        result = await self.session.execute(
            select(Bounty).where(Bounty.llm_provider == llm_provider, Bounty.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def update_bounty_pool(self, bounty_id: int, new_pool: float) -> bool:
        """Update bounty pool amount"""
        result = await self.session.execute(
            update(Bounty)
            .where(Bounty.id == bounty_id)
            .values(current_pool=new_pool, updated_at=datetime.utcnow())
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def increment_bounty_entries(self, bounty_id: int) -> bool:
        """Increment total entries for a bounty"""
        result = await self.session.execute(
            update(Bounty)
            .where(Bounty.id == bounty_id)
            .values(total_entries=Bounty.total_entries + 1, updated_at=datetime.utcnow())
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def update_bounty_win_rate(self, bounty_id: int, win_rate: float) -> bool:
        """Update bounty win rate"""
        result = await self.session.execute(
            update(Bounty)
            .where(Bounty.id == bounty_id)
            .values(win_rate=win_rate, updated_at=datetime.utcnow())
        )
        await self.session.commit()
        return result.rowcount > 0

class ConversationRepository:
    """Repository for conversation operations with bounty support"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_message(self, user_id: int, message_type: str, content: str, 
                         bounty_id: Optional[int] = None, cost: Optional[float] = None, 
                         tokens_used: Optional[int] = None, model_used: Optional[str] = None,
                         is_public: bool = True, is_winner: bool = False) -> Conversation:
        """Add a message to the conversation"""
        conversation = Conversation(
            user_id=user_id,
            bounty_id=bounty_id,
            message_type=message_type,
            content=content,
            cost=cost,
            tokens_used=tokens_used,
            model_used=model_used,
            is_public=is_public,
            is_winner=is_winner
        )
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation
    
    async def get_public_messages(self, bounty_id: Optional[int] = None, limit: int = 100) -> List[Conversation]:
        """Get public messages for global chat visibility"""
        query = select(Conversation).where(Conversation.is_public == True)
        
        if bounty_id:
            query = query.where(Conversation.bounty_id == bounty_id)
        
        query = query.order_by(desc(Conversation.timestamp)).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_user_messages(self, user_id: int, bounty_id: Optional[int] = None, limit: int = 50) -> List[Conversation]:
        """Get messages for a specific user"""
        query = select(Conversation).where(Conversation.user_id == user_id)
        
        if bounty_id:
            query = query.where(Conversation.bounty_id == bounty_id)
        
        query = query.order_by(desc(Conversation.timestamp)).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_winner_messages(self, limit: int = 20) -> List[Conversation]:
        """Get recent winning messages"""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.is_winner == True)
            .order_by(desc(Conversation.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def mark_as_winner(self, conversation_id: int) -> bool:
        """Mark a conversation as a winner"""
        result = await self.session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(is_winner=True)
        )
        await self.session.commit()
        return result.rowcount > 0

class FreeQuestionUsageRepository:
    """Repository for free question usage tracking"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_or_create_usage(self, wallet_address: str, ip_address: Optional[str] = None) -> FreeQuestionUsage:
        """Get or create free question usage record for a wallet"""
        try:
            # Check if usage record exists
            query = select(FreeQuestionUsage).where(FreeQuestionUsage.wallet_address == wallet_address)
            result = await self.session.execute(query)
            usage = result.scalar_one_or_none()
            
            if usage:
                return usage
            
            # Create new usage record
            usage = FreeQuestionUsage(
                wallet_address=wallet_address,
                questions_used=0,
                questions_remaining=2,
                ip_address=ip_address
            )
            self.session.add(usage)
            await self.session.commit()
            await self.session.refresh(usage)
            return usage
            
        except Exception as e:
            await self.session.rollback()
            print(f"Error getting/creating free question usage: {e}")
            raise
    
    async def use_question(self, wallet_address: str) -> Optional[FreeQuestionUsage]:
        """Use one free question for a wallet"""
        try:
            usage = await self.get_or_create_usage(wallet_address)
            
            if usage.questions_remaining > 0:
                usage.questions_used += 1
                usage.questions_remaining -= 1
                usage.updated_at = datetime.utcnow()
                
                await self.session.commit()
                await self.session.refresh(usage)
                return usage
            
            return None  # No questions remaining
            
        except Exception as e:
            await self.session.rollback()
            print(f"Error using free question: {e}")
            raise
    
    async def add_referral_questions(self, wallet_address: str, questions: int = 5) -> bool:
        """Add referral questions to a wallet"""
        try:
            usage = await self.get_or_create_usage(wallet_address)
            usage.questions_remaining += questions
            usage.updated_at = datetime.utcnow()
            
            await self.session.commit()
            return True
            
        except Exception as e:
            await self.session.rollback()
            print(f"Error adding referral questions: {e}")
            return False
    
    async def update_email_and_referral_code(self, wallet_address: str, email: str) -> str:
        """Update email and generate referral code"""
        try:
            usage = await self.get_or_create_usage(wallet_address)
            
            # Generate referral code from email
            email_prefix = email.split('@')[0]
            referral_code = f"billionsbounty.com/{email_prefix}"
            
            usage.email = email
            usage.referral_code = referral_code
            usage.updated_at = datetime.utcnow()
            
            await self.session.commit()
            return referral_code
            
        except Exception as e:
            await self.session.rollback()
            print(f"Error updating email and referral code: {e}")
            raise
    
    async def check_ip_usage(self, ip_address: str) -> bool:
        """Check if IP address has already been used"""
        try:
            query = select(FreeQuestionUsage).where(FreeQuestionUsage.ip_address == ip_address)
            result = await self.session.execute(query)
            usage = result.scalar_one_or_none()
            
            return usage is not None
            
        except Exception as e:
            print(f"Error checking IP usage: {e}")
            return False
