"""
Power-Up Service for Temporary Boosts

Manages power-ups, boosts, and temporary bonuses that users can activate.

Author: Billions Bounty
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import User, PowerUp
import logging

logger = logging.getLogger(__name__)


class PowerUpService:
    """Service for managing power-ups and boosts"""
    
    # Power-up definitions
    POWER_UP_TYPES = {
        "double_points": {
            "name": "Double Points",
            "description": "Earn 2x points for 1 hour",
            "multiplier": 2.0,
            "duration_minutes": 60,
            "icon": "⚡"
        },
        "streak_shield": {
            "name": "Streak Shield",
            "description": "Protect your streak for 24 hours",
            "multiplier": 1.0,
            "duration_minutes": 1440,  # 24 hours
            "icon": "🛡️"
        },
        "referral_boost": {
            "name": "Referral Boost",
            "description": "Next 3 referrals worth 3x points",
            "multiplier": 3.0,
            "duration_minutes": 0,  # Uses count instead
            "icon": "🚀",
            "uses_remaining": 3
        },
        "lucky_multiplier": {
            "name": "Lucky Multiplier",
            "description": "Random 2x-5x multiplier on next jailbreak",
            "multiplier": 0,  # Random between 2-5
            "duration_minutes": 0,  # Single use
            "icon": "🍀"
        },
        "question_rush": {
            "name": "Question Rush",
            "description": "Questions worth 2x points for 30 minutes",
            "multiplier": 2.0,
            "duration_minutes": 30,
            "icon": "💨"
        }
    }
    
    async def create_power_up(
        self, 
        session: AsyncSession, 
        user_id: int,
        power_up_type: str,
        source: str = "earned"  # 'earned', 'purchased', 'gifted', 'challenge'
    ) -> Optional[PowerUp]:
        """
        Create a power-up for a user
        
        Returns:
            Created PowerUp object
        """
        try:
            if power_up_type not in self.POWER_UP_TYPES:
                logger.error(f"Invalid power-up type: {power_up_type}")
                return None
            
            power_up_def = self.POWER_UP_TYPES[power_up_type]
            
            power_up = PowerUp(
                user_id=user_id,
                power_up_type=power_up_type,
                name=power_up_def["name"],
                description=power_up_def["description"],
                multiplier=power_up_def["multiplier"],
                duration_minutes=power_up_def["duration_minutes"],
                source=source,
                is_active=False,
                is_used=False
            )
            
            session.add(power_up)
            await session.commit()
            
            logger.info(f"Created {power_up_type} power-up for user {user_id}")
            return power_up
        
        except Exception as e:
            logger.error(f"Error creating power-up for user {user_id}: {e}")
            await session.rollback()
            return None
    
    async def activate_power_up(
        self, 
        session: AsyncSession, 
        user_id: int,
        power_up_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Activate a power-up
        
        Returns:
            Dict with activation info
        """
        try:
            # Get power-up
            result = await session.execute(
                select(PowerUp).where(
                    and_(
                        PowerUp.id == power_up_id,
                        PowerUp.user_id == user_id,
                        PowerUp.is_used == False
                    )
                )
            )
            power_up = result.scalar_one_or_none()
            
            if not power_up:
                return None
            
            # Check if user already has an active power-up of this type
            if power_up.duration_minutes > 0:  # Time-based power-ups
                active_result = await session.execute(
                    select(PowerUp).where(
                        and_(
                            PowerUp.user_id == user_id,
                            PowerUp.power_up_type == power_up.power_up_type,
                            PowerUp.is_active == True,
                            PowerUp.expires_at > datetime.utcnow()
                        )
                    )
                )
                if active_result.scalar_one_or_none():
                    return {"error": "You already have an active power-up of this type"}
            
            # Activate power-up
            power_up.is_active = True
            power_up.activated_at = datetime.utcnow()
            
            if power_up.duration_minutes > 0:
                power_up.expires_at = datetime.utcnow() + timedelta(minutes=power_up.duration_minutes)
            else:
                # Single-use power-ups (like lucky_multiplier)
                power_up.expires_at = datetime.utcnow() + timedelta(days=365)  # Long expiry for single-use
            
            await session.commit()
            
            logger.info(f"User {user_id} activated power-up {power_up_id}")
            
            return {
                "power_up_id": power_up.id,
                "power_up_type": power_up.power_up_type,
                "name": power_up.name,
                "expires_at": power_up.expires_at.isoformat(),
                "duration_minutes": power_up.duration_minutes
            }
        
        except Exception as e:
            logger.error(f"Error activating power-up {power_up_id}: {e}")
            await session.rollback()
            return None
    
    async def get_active_power_ups(
        self, 
        session: AsyncSession, 
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Get all active power-ups for a user"""
        try:
            result = await session.execute(
                select(PowerUp).where(
                    and_(
                        PowerUp.user_id == user_id,
                        PowerUp.is_active == True,
                        or_(
                            PowerUp.expires_at == None,
                            PowerUp.expires_at > datetime.utcnow()
                        )
                    )
                )
            )
            power_ups = result.scalars().all()
            
            return [
                {
                    "id": p.id,
                    "power_up_type": p.power_up_type,
                    "name": p.name,
                    "description": p.description,
                    "multiplier": p.multiplier,
                    "expires_at": p.expires_at.isoformat() if p.expires_at else None,
                    "time_remaining": (p.expires_at - datetime.utcnow()).total_seconds() if p.expires_at else None
                }
                for p in power_ups
            ]
        
        except Exception as e:
            logger.error(f"Error getting active power-ups for user {user_id}: {e}")
            return []
    
    async def get_user_power_ups(
        self, 
        session: AsyncSession, 
        user_id: int,
        include_used: bool = False
    ) -> Dict[str, Any]:
        """Get all power-ups for a user (active and inactive)"""
        try:
            query = select(PowerUp).where(PowerUp.user_id == user_id)
            
            if not include_used:
                query = query.where(PowerUp.is_used == False)
            
            result = await session.execute(query.order_by(PowerUp.created_at.desc()))
            power_ups = result.scalars().all()
            
            active = []
            inactive = []
            
            for p in power_ups:
                power_up_data = {
                    "id": p.id,
                    "power_up_type": p.power_up_type,
                    "name": p.name,
                    "description": p.description,
                    "multiplier": p.multiplier,
                    "source": p.source,
                    "is_active": p.is_active,
                    "is_used": p.is_used,
                    "expires_at": p.expires_at.isoformat() if p.expires_at else None,
                    "created_at": p.created_at.isoformat()
                }
                
                if p.is_active and (not p.expires_at or p.expires_at > datetime.utcnow()):
                    active.append(power_up_data)
                else:
                    inactive.append(power_up_data)
            
            return {
                "active": active,
                "inactive": inactive,
                "total": len(power_ups)
            }
        
        except Exception as e:
            logger.error(f"Error getting power-ups for user {user_id}: {e}")
            return {"active": [], "inactive": [], "total": 0}
    
    async def check_and_deactivate_expired(
        self, 
        session: AsyncSession, 
        user_id: int
    ) -> int:
        """
        Check for expired power-ups and deactivate them
        
        Returns:
            Number of power-ups deactivated
        """
        try:
            result = await session.execute(
                select(PowerUp).where(
                    and_(
                        PowerUp.user_id == user_id,
                        PowerUp.is_active == True,
                        PowerUp.expires_at <= datetime.utcnow()
                    )
                )
            )
            expired = result.scalars().all()
            
            count = 0
            for power_up in expired:
                power_up.is_active = False
                power_up.is_used = True
                count += 1
            
            if count > 0:
                await session.commit()
                logger.info(f"Deactivated {count} expired power-ups for user {user_id}")
            
            return count
        
        except Exception as e:
            logger.error(f"Error deactivating expired power-ups: {e}")
            await session.rollback()
            return 0
    
    async def get_points_multiplier(
        self, 
        session: AsyncSession, 
        user_id: int,
        activity_type: str  # 'question', 'referral', 'jailbreak'
    ) -> float:
        """
        Get current points multiplier for a user based on active power-ups
        
        Returns:
            Multiplier value (1.0 = no multiplier)
        """
        try:
            multiplier = 1.0
            
            # Get active power-ups
            active = await self.get_active_power_ups(session, user_id)
            
            for power_up in active:
                power_up_type = power_up["power_up_type"]
                
                if power_up_type == "double_points":
                    multiplier *= power_up["multiplier"]
                elif power_up_type == "question_rush" and activity_type == "question":
                    multiplier *= power_up["multiplier"]
                elif power_up_type == "referral_boost" and activity_type == "referral":
                    multiplier *= power_up["multiplier"]
                elif power_up_type == "lucky_multiplier" and activity_type == "jailbreak":
                    # Random multiplier between 2-5
                    import random
                    multiplier *= random.uniform(2.0, 5.0)
            
            return multiplier
        
        except Exception as e:
            logger.error(f"Error getting points multiplier for user {user_id}: {e}")
            return 1.0


# Create singleton instance
powerup_service = PowerUpService()

