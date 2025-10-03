"""
Repository layer for database operations
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from sqlalchemy.orm import selectinload
from .models import User, Conversation, AttackAttempt, Transaction, PrizePool, SecurityEvent, BountyState, BountyEntry, BlacklistedPhrase

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

class ConversationRepository:
    """Repository for conversation operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_message(self, user_id: int, message_type: str, content: str, 
                         cost: Optional[float] = None, tokens_used: Optional[int] = None,
                         model_used: Optional[str] = None) -> Conversation:
        """Add a message to the conversation"""
        conversation = Conversation(
            user_id=user_id,
            message_type=message_type,
            content=content,
            cost=cost,
            tokens_used=tokens_used,
            model_used=model_used
        )
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation
    
    async def get_user_conversation_history(self, user_id: int, limit: int = 10) -> List[Conversation]:
        """Get recent conversation history for a user"""
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.timestamp))
            .limit(limit)
        )
        return list(reversed(result.scalars().all()))  # Return in chronological order

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
        result = await self.session.execute(
            update(BlacklistedPhrase)
            .where(BlacklistedPhrase.id == phrase_id)
            .values(is_active=True)
        )
        await self.session.commit()
        return result.rowcount > 0
