"""
bounty Service - Fixed-Cost Rollover bounty Logic
Implements the $10,000 budget rollover bounty system
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from .models import BountyState, BountyEntry, User
import pytz

# bounty Constants
PRIZE_FLOOR_USD = 10000.00
ENTRY_FEE_USD = 10.00
PRIZE_POOL_CONTRIBUTION_RATE = 0.80
OPERATIONAL_FEE_RATE = 0.20

class BountyService:
    """Service for managing the fixed-cost rollover bounty system"""
    
    def __init__(self):
        self.entry_fee = ENTRY_FEE_USD
        self.pool_contribution = ENTRY_FEE_USD * PRIZE_POOL_CONTRIBUTION_RATE  # $8.00
        self.operational_fee = ENTRY_FEE_USD * OPERATIONAL_FEE_RATE  # $2.00
        self.prize_floor = PRIZE_FLOOR_USD
        
    async def get_or_create_bounty_state(self, session: AsyncSession) -> BountyState:
        """Get or create the bounty state"""
        result = await session.execute(select(BountyState).where(BountyState.is_active == True))
        bounty_state = result.scalar_one_or_none()
        
        if not bounty_state:
            # Create initial bounty state
            bounty_state = BountyState(
                current_jackpot_usd=self.prize_floor,
                total_entries_this_period=0,
                last_rollover_at=datetime.utcnow(),
                next_rollover_at=self._calculate_next_rollover(),
                is_active=True
            )
            session.add(bounty_state)
            await session.commit()
            await session.refresh(bounty_state)
        
        return bounty_state
    
    def _calculate_next_rollover(self) -> datetime:
        """Calculate the next rollover time (Wednesday or Saturday at 11pm EST)"""
        est = pytz.timezone('US/Eastern')
        now = datetime.now(est)
        
        # Find next Wednesday or Saturday at 11pm EST
        days_ahead = 0
        for i in range(7):  # Check next 7 days
            check_date = now + timedelta(days=i)
            if check_date.weekday() in [2, 5]:  # Wednesday=2, Saturday=5
                target_time = check_date.replace(hour=23, minute=0, second=0, microsecond=0)
                if target_time > now:
                    return target_time.astimezone(pytz.UTC)
        
        # If no valid day found in next 7 days, go to next Wednesday
        days_until_wednesday = (2 - now.weekday()) % 7
        if days_until_wednesday == 0:
            days_until_wednesday = 7
        next_wednesday = now + timedelta(days=days_until_wednesday)
        return next_wednesday.replace(hour=23, minute=0, second=0, microsecond=0).astimezone(pytz.UTC)
    
    async def process_entry(self, session: AsyncSession, user_id: int, 
                          message_content: str, ai_response: str) -> Dict[str, Any]:
        """Process a bounty entry (user pays $10, $8 goes to pool)"""
        # Get current bounty state
        bounty_state = await self.get_or_create_bounty_state(session)
        
        # Check if we need to rollover (past rollover time)
        await self._check_and_rollover(session, bounty_state)
        
        # Create bounty entry
        entry = BountyEntry(
            user_id=user_id,
            entry_fee_usd=self.entry_fee,
            pool_contribution=self.pool_contribution,
            operational_fee=self.operational_fee,
            message_content=message_content,
            ai_response=ai_response,
            is_winner=False
        )
        session.add(entry)
        
        # Update bounty state
        bounty_state.current_jackpot_usd += self.pool_contribution
        bounty_state.total_entries_this_period += 1
        bounty_state.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(entry)
        await session.refresh(bounty_state)
        
        return {
            "success": True,
            "entry_id": entry.id,
            "entry_fee": self.entry_fee,
            "pool_contribution": self.pool_contribution,
            "new_jackpot": bounty_state.current_jackpot_usd,
            "total_entries": bounty_state.total_entries_this_period
        }
    
    async def _check_and_rollover(self, session: AsyncSession, bounty_state: BountyState):
        """Check if rollover is needed and execute if so"""
        now = datetime.utcnow()
        
        if bounty_state.next_rollover_at and now >= bounty_state.next_rollover_at:
            # Time for rollover - no winner found, pool rolls over
            bounty_state.last_rollover_at = now
            bounty_state.next_rollover_at = self._calculate_next_rollover()
            bounty_state.total_entries_this_period = 0
            # Jackpot stays the same (rolls over)
            bounty_state.updated_at = now
            
            await session.commit()
    
    async def determine_winner(self, session: AsyncSession, user_id: int, 
                             entry_id: int, should_transfer: bool) -> Dict[str, Any]:
        """Determine if user wins and handle prize payout"""
        bounty_state = await self.get_or_create_bounty_state(session)
        
        if should_transfer:
            # Winner found! Pay out the jackpot
            prize_payout = bounty_state.current_jackpot_usd
            
            # Update bounty entry as winner
            await session.execute(
                update(BountyEntry)
                .where(BountyEntry.id == entry_id)
                .values(is_winner=True, prize_payout=prize_payout)
            )
            
            # Reset bounty state
            bounty_state.current_jackpot_usd = self.prize_floor  # Reset to $10K floor
            bounty_state.total_entries_this_period = 0
            bounty_state.last_winner_id = user_id
            bounty_state.last_rollover_at = datetime.utcnow()
            bounty_state.next_rollover_at = self._calculate_next_rollover()
            bounty_state.updated_at = datetime.utcnow()
            
            await session.commit()
            
            return {
                "is_winner": True,
                "prize_payout": prize_payout,
                "new_jackpot": self.prize_floor,
                "message": f"🎉 WINNER! You won ${prize_payout:,.2f}!"
            }
        else:
            # No winner - pool continues to grow
            return {
                "is_winner": False,
                "current_jackpot": bounty_state.current_jackpot_usd,
                "message": f"Pool continues to grow! Current jackpot: ${bounty_state.current_jackpot_usd:,.2f}"
            }
    
    async def get_bounty_status(self, session: AsyncSession) -> Dict[str, Any]:
        """Get current bounty status for display"""
        bounty_state = await self.get_or_create_bounty_state(session)
        
        # Check if rollover is needed
        await self._check_and_rollover(session, bounty_state)
        
        # Calculate time until next rollover
        now = datetime.utcnow()
        if bounty_state.next_rollover_at:
            time_until_rollover = bounty_state.next_rollover_at - now
            hours_until = int(time_until_rollover.total_seconds() // 3600)
            minutes_until = int((time_until_rollover.total_seconds() % 3600) // 60)
            time_display = f"{hours_until}h {minutes_until}m"
        else:
            time_display = "Calculating..."
        
        return {
            "current_jackpot": bounty_state.current_jackpot_usd,
            "total_entries_this_period": bounty_state.total_entries_this_period,
            "time_until_rollover": time_display,
            "next_rollover_at": bounty_state.next_rollover_at.isoformat() if bounty_state.next_rollover_at else None,
            "entry_fee": self.entry_fee,
            "pool_contribution": self.pool_contribution,
            "last_winner_id": bounty_state.last_winner_id
        }
    
    async def create_winner_flex_card(self, user: User, entry: BountyEntry, 
                                    total_spent: float) -> Dict[str, Any]:
        """Create a flex card for the winner showing ROI and stats"""
        roi_percentage = ((entry.prize_payout - total_spent) / total_spent) * 100 if total_spent > 0 else 0
        
        return {
            "type": "winner_flex_card",
            "title": "🎉 JACKPOT WINNER! 🎉",
            "winner": {
                "username": user.username or f"User #{user.id}",
                "wallet_address": user.wallet_address or "Not connected"
            },
            "stats": {
                "prize_won": entry.prize_payout,
                "total_spent": total_spent,
                "roi_percentage": roi_percentage,
                "entries_made": 1,  # Could be calculated from user's total entries
                "winning_message": entry.message_content[:100] + "..." if len(entry.message_content or "") > 100 else entry.message_content
            },
            "timestamp": entry.created_at.isoformat(),
            "style": {
                "background": "linear-gradient(135deg, #ffd700 0%, #ffed4e 100%)",
                "border": "3px solid #ff6b35",
                "text_color": "#1a1a1a"
            }
        }
