"""
Research Service - Fixed-Cost Rollover Research Fund Logic
Implements the $10,000 research fund system for AI security research
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from .models import BountyState, BountyEntry, User
import pytz

# Research Fund Constants
RESEARCH_FUND_FLOOR_USD = 10000.00
RESEARCH_FEE_USD = 10.00
RESEARCH_FUND_CONTRIBUTION_RATE = 0.80
OPERATIONAL_FEE_RATE = 0.20

class ResearchService:
    """Service for managing the fixed-cost rollover research fund system"""
    
    def __init__(self):
        self.research_fee = RESEARCH_FEE_USD
        self.fund_contribution = RESEARCH_FEE_USD * RESEARCH_FUND_CONTRIBUTION_RATE  # $8.00
        self.operational_fee = RESEARCH_FEE_USD * OPERATIONAL_FEE_RATE  # $2.00
        self.research_fund_floor = RESEARCH_FUND_FLOOR_USD
        
    async def get_or_create_research_state(self, session: AsyncSession) -> BountyState:
        """Get or create the research fund state"""
        result = await session.execute(select(BountyState).where(BountyState.is_active == True))
        research_state = result.scalar_one_or_none()
        
        if not research_state:
            # Create initial research fund state
            research_state = BountyState(
                current_jackpot_usd=self.research_fund_floor,
                total_entries_this_period=0,
                last_rollover_at=datetime.utcnow(),
                next_rollover_at=self._calculate_next_reset(),
                is_active=True
            )
            session.add(research_state)
            await session.commit()
            await session.refresh(research_state)
        
        return research_state
    
    def _calculate_next_reset(self) -> datetime:
        """Calculate the next research cycle reset time (Wednesday or Saturday at 11pm EST)"""
        est = pytz.timezone('US/Eastern')
        now = datetime.now(est)
        
        # Find next Wednesday or Saturday at 11pm EST
        days_ahead = 0
        for i in range(7):  # Check next 7 days
            check_date = now + timedelta(days=i)
            if check_date.weekday() in [2, 5]:  # Wednesday=2, Saturday=5
                target_time = check_date.replace(hour=23, minute=0, second=0, microsecond=0)
                if target_time > now:
                    return target_time.astimezone(pytz.UTC).replace(tzinfo=None)
        
        # If no valid day found in next 7 days, go to next Wednesday
        days_until_wednesday = (2 - now.weekday()) % 7
        if days_until_wednesday == 0:
            days_until_wednesday = 7
        next_wednesday = now + timedelta(days=days_until_wednesday)
        return next_wednesday.replace(hour=23, minute=0, second=0, microsecond=0).astimezone(pytz.UTC).replace(tzinfo=None)
    
    async def process_research_attempt(self, session: AsyncSession, user_id: int, 
                          message_content: str, ai_response: str) -> Dict[str, Any]:
        """Process a research attempt (user pays $10, $8 goes to research fund)"""
        # Get current research fund state
        research_state = await self.get_or_create_research_state(session)
        
        # Check if we need to reset (past reset time)
        await self._check_and_reset(session, research_state)
        
        # Create research attempt entry
        entry = BountyEntry(
            user_id=user_id,
            entry_fee_usd=self.research_fee,
            pool_contribution=self.fund_contribution,
            operational_fee=self.operational_fee,
            message_content=message_content,
            ai_response=ai_response,
            is_winner=False
        )
        session.add(entry)
        
        # Update research fund state
        research_state.current_jackpot_usd += self.fund_contribution
        research_state.total_entries_this_period += 1
        research_state.last_participant_id = user_id  # Track last person who asked
        research_state.last_question_at = datetime.utcnow()  # Track when last question was asked
        research_state.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(entry)
        await session.refresh(research_state)
        
        return {
            "success": True,
            "entry_id": entry.id,
            "research_fee": self.research_fee,
            "fund_contribution": self.fund_contribution,
            "new_research_fund": research_state.current_jackpot_usd,
            "total_attempts": research_state.total_entries_this_period
        }
    
    async def _check_and_reset(self, session: AsyncSession, research_state: BountyState):
        """Check if research cycle reset is needed and execute escape plan if so"""
        now = datetime.utcnow()
        
        if research_state.next_rollover_at and now >= research_state.next_rollover_at:
            # Check if 24 hours have passed since last question
            if research_state.last_question_at:
                time_since_last_question = now - research_state.last_question_at
                if time_since_last_question.total_seconds() >= 24 * 60 * 60:  # 24 hours
                    # Execute escape plan - distribute funds
                    await self._execute_escape_plan(session, research_state)
                    return
            
            # Regular reset - no successful research found, fund resets
            research_state.last_rollover_at = now
            research_state.next_rollover_at = self._calculate_next_reset()
            research_state.total_entries_this_period = 0
            # Research fund stays the same (resets to floor)
            research_state.updated_at = now
            
            await session.commit()
    
    async def _execute_escape_plan(self, session: AsyncSession, research_state: BountyState):
        """Execute the escape plan: 80% distributed equally among participants, 20% to last participant"""
        from sqlalchemy import select, func
        
        # Get all unique participants from this period
        participants_result = await session.execute(
            select(BountyEntry.user_id)
            .where(BountyEntry.created_at >= research_state.last_rollover_at)
            .distinct()
        )
        participants = [row[0] for row in participants_result.fetchall()]
        
        if not participants:
            # No participants, just reset normally
            research_state.last_rollover_at = datetime.utcnow()
            research_state.next_rollover_at = self._calculate_next_reset()
            research_state.total_entries_this_period = 0
            research_state.updated_at = datetime.utcnow()
            await session.commit()
            return
        
        total_jackpot = research_state.current_jackpot_usd
        last_participant_share = total_jackpot * 0.20  # 20% to last participant
        community_share = total_jackpot * 0.80  # 80% to community
        equal_share_per_participant = community_share / len(participants)
        
        # Log the escape plan execution
        print(f"🚨 ESCAPE PLAN TRIGGERED! 🚨")
        print(f"Total jackpot: ${total_jackpot:,.2f}")
        print(f"Last participant gets: ${last_participant_share:,.2f}")
        print(f"Each participant gets: ${equal_share_per_participant:,.2f}")
        print(f"Total participants: {len(participants)}")
        
        # TODO: Here you would integrate with your smart contract service
        # to actually distribute the funds via the execute_time_escape_plan function
        # For now, we'll just log and reset the state
        
        # Reset the research fund state
        research_state.current_jackpot_usd = self.research_fund_floor
        research_state.total_entries_this_period = 0
        research_state.last_rollover_at = datetime.utcnow()
        research_state.next_rollover_at = self._calculate_next_reset()
        research_state.last_participant_id = None
        research_state.last_question_at = None
        research_state.updated_at = datetime.utcnow()
        
        await session.commit()
    
    async def determine_research_success(self, session: AsyncSession, user_id: int, 
                             entry_id: int, should_transfer: bool) -> Dict[str, Any]:
        """Determine if research attempt was successful and handle grant payout"""
        research_state = await self.get_or_create_research_state(session)
        
        if should_transfer:
            # Research success! Pay out the research grant
            grant_payout = research_state.current_jackpot_usd
            
            # Update research entry as successful
            await session.execute(
                update(BountyEntry)
                .where(BountyEntry.id == entry_id)
                .values(is_winner=True, prize_payout=grant_payout)
            )
            
            # Reset research fund state
            research_state.current_jackpot_usd = self.research_fund_floor  # Reset to $10K floor
            research_state.total_entries_this_period = 0
            research_state.last_winner_id = user_id
            research_state.last_rollover_at = datetime.utcnow()
            research_state.next_rollover_at = self._calculate_next_reset()
            research_state.updated_at = datetime.utcnow()
            
            await session.commit()
            
            return {
                "is_winner": True,
                "grant_payout": grant_payout,
                "new_research_fund": self.research_fund_floor,
                "message": f"🎉 RESEARCH SUCCESS! You earned a ${grant_payout:,.2f} research grant!"
            }
        else:
            # No success - research fund continues to grow
            return {
                "is_winner": False,
                "current_research_fund": research_state.current_jackpot_usd,
                "message": f"Research fund continues to grow! Current fund: ${research_state.current_jackpot_usd:,.2f}"
            }
    
    async def get_research_status(self, session: AsyncSession) -> Dict[str, Any]:
        """Get current research fund status for display"""
        research_state = await self.get_or_create_research_state(session)
        
        # Check if reset is needed
        await self._check_and_reset(session, research_state)
        
        # Calculate time until next reset
        now = datetime.utcnow()
        if research_state.next_rollover_at:
            time_until_reset = research_state.next_rollover_at - now
            hours_until = int(time_until_reset.total_seconds() // 3600)
            minutes_until = int((time_until_reset.total_seconds() % 3600) // 60)
            time_display = f"{hours_until}h {minutes_until}m"
        else:
            time_display = "Calculating..."
        
        # Check escape plan status
        escape_plan_status = await self._check_escape_plan_status(session, research_state)
        
        return {
            "current_research_fund": research_state.current_jackpot_usd,
            "current_jackpot_usd": research_state.current_jackpot_usd,  # Alias for compatibility
            "total_attempts_this_period": research_state.total_entries_this_period,
            "time_until_reset": time_display,
            "next_reset_at": research_state.next_rollover_at.isoformat() if research_state.next_rollover_at else None,
            "research_fee": self.research_fee,
            "entry_fee": self.research_fee,  # Alias for compatibility
            "fund_contribution": self.fund_contribution,
            "pool_contribution": self.fund_contribution,  # Alias for compatibility
            "last_successful_researcher_id": research_state.last_winner_id,
            "escape_plan": escape_plan_status
        }
    
    async def _check_escape_plan_status(self, session: AsyncSession, research_state: BountyState) -> Dict[str, Any]:
        """Check the status of the escape plan (24-hour timeout)"""
        now = datetime.utcnow()
        
        if not research_state.last_question_at:
            return {
                "is_active": False,
                "time_since_last_question": None,
                "time_until_escape": None,
                "message": "No questions asked yet"
            }
        
        time_since_last_question = now - research_state.last_question_at
        hours_since = time_since_last_question.total_seconds() / 3600
        
        if hours_since >= 24:
            return {
                "is_active": True,
                "time_since_last_question": f"{int(hours_since)}h {int((time_since_last_question.total_seconds() % 3600) / 60)}m",
                "time_until_escape": "0h 0m",
                "message": "🚨 ESCAPE PLAN READY! No questions for 24+ hours",
                "should_trigger": True
            }
        else:
            hours_until_escape = 24 - hours_since
            return {
                "is_active": True,
                "time_since_last_question": f"{int(hours_since)}h {int((time_since_last_question.total_seconds() % 3600) / 60)}m",
                "time_until_escape": f"{int(hours_until_escape)}h {int((hours_until_escape % 1) * 60)}m",
                "message": f"Escape plan in {int(hours_until_escape)}h {int((hours_until_escape % 1) * 60)}m if no questions",
                "should_trigger": False
            }
    
    async def create_research_success_card(self, user: User, entry: BountyEntry, 
                                    total_spent: float) -> Dict[str, Any]:
        """Create a success card for the researcher showing ROI and stats"""
        roi_percentage = ((entry.prize_payout - total_spent) / total_spent) * 100 if total_spent > 0 else 0
        
        return {
            "type": "research_success_card",
            "title": "🎉 RESEARCH SUCCESS! 🎉",
            "researcher": {
                "username": user.display_name or f"Researcher #{user.id}",
                "wallet_address": user.wallet_address or "Not connected"
            },
            "stats": {
                "grant_earned": entry.prize_payout,
                "total_invested": total_spent,
                "roi_percentage": roi_percentage,
                "attempts_made": 1,  # Could be calculated from user's total attempts
                "successful_technique": entry.message_content[:100] + "..." if len(entry.message_content or "") > 100 else entry.message_content
            },
            "timestamp": entry.created_at.isoformat(),
            "style": {
                "background": "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                "border": "3px solid #06b6d4",
                "text_color": "#ffffff"
            }
        }
    
    async def get_bounty_status(self, session: AsyncSession) -> Dict[str, Any]:
        """Get current bounty status (alias for get_research_status for compatibility)"""
        return await self.get_research_status(session)