"""
Team Collaboration Service

Handles all team-related operations:
- Team creation and management
- Member invitations and joins
- Team funding and pooled resources
- Collaborative attempts
- Internal team chat
- Prize distribution
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
import secrets
import string

from .models import (
    Team, TeamMember, TeamInvitation, TeamAttempt, TeamMessage, TeamFunding,
    TeamPrizeDistribution, TeamMemberPrize, User, Winner
)


class TeamService:
    """
    Service for managing team collaboration
    """
    
    # ====================================================================
    # TEAM CREATION & MANAGEMENT
    # ====================================================================
    
    async def create_team(
        self,
        db: AsyncSession,
        leader_id: int,
        name: str,
        description: Optional[str] = None,
        max_members: int = 5,
        is_public: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new team
        
        Args:
            db: Database session
            leader_id: User ID of team leader
            name: Team name (must be unique)
            description: Optional team description
            max_members: Maximum team size (default 5)
            is_public: Whether team appears in discovery
            
        Returns:
            Dictionary with team data
        """
        # Check if team name already exists
        existing = await db.execute(
            select(Team).where(Team.name == name)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Team name '{name}' is already taken")
        
        # Generate unique invite code
        invite_code = self._generate_invite_code()
        
        # Create team
        team = Team(
            name=name,
            description=description,
            leader_id=leader_id,
            max_members=max_members,
            is_public=is_public,
            invite_code=invite_code
        )
        
        db.add(team)
        await db.flush()  # Get team ID
        
        # Add leader as first member
        leader_member = TeamMember(
            team_id=team.id,
            user_id=leader_id,
            role="leader",
            contribution_percentage=0.0
        )
        
        db.add(leader_member)
        await db.commit()
        await db.refresh(team)
        
        return {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "leader_id": team.leader_id,
            "max_members": team.max_members,
            "is_public": team.is_public,
            "invite_code": team.invite_code,
            "total_pool": team.total_pool,
            "member_count": 1,
            "created_at": team.created_at.isoformat()
        }
    
    async def get_team(
        self,
        db: AsyncSession,
        team_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get team details
        
        Args:
            db: Database session
            team_id: Team ID
            
        Returns:
            Dictionary with team data or None
        """
        query = select(Team).where(Team.id == team_id)
        result = await db.execute(query)
        team = result.scalar_one_or_none()
        
        if not team:
            return None
        
        # Get member count
        member_count_query = select(func.count(TeamMember.id)).where(
            TeamMember.team_id == team_id,
            TeamMember.is_active == True
        )
        member_count = await db.execute(member_count_query)
        
        return {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "leader_id": team.leader_id,
            "max_members": team.max_members,
            "is_public": team.is_public,
            "invite_code": team.invite_code,
            "total_pool": team.total_pool,
            "total_attempts": team.total_attempts,
            "total_spent": team.total_spent,
            "member_count": member_count.scalar(),
            "is_active": team.is_active,
            "created_at": team.created_at.isoformat(),
            "updated_at": team.updated_at.isoformat()
        }
    
    async def list_public_teams(
        self,
        db: AsyncSession,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all public teams
        
        Args:
            db: Database session
            limit: Max teams to return
            offset: Pagination offset
            
        Returns:
            List of team dictionaries
        """
        query = select(Team).where(
            Team.is_public == True,
            Team.is_active == True
        ).order_by(desc(Team.created_at)).limit(limit).offset(offset)
        
        result = await db.execute(query)
        teams = result.scalars().all()
        
        team_list = []
        for team in teams:
            # Get member count
            member_count_query = select(func.count(TeamMember.id)).where(
                TeamMember.team_id == team.id,
                TeamMember.is_active == True
            )
            member_count = await db.execute(member_count_query)
            
            team_list.append({
                "id": team.id,
                "name": team.name,
                "description": team.description,
                "leader_id": team.leader_id,
                "max_members": team.max_members,
                "total_pool": team.total_pool,
                "total_attempts": team.total_attempts,
                "member_count": member_count.scalar(),
                "created_at": team.created_at.isoformat()
            })
        
        return team_list
    
    async def update_team(
        self,
        db: AsyncSession,
        team_id: int,
        user_id: int,
        **updates
    ) -> Dict[str, Any]:
        """
        Update team settings (leader only)
        
        Args:
            db: Database session
            team_id: Team ID
            user_id: User making the update
            **updates: Fields to update
            
        Returns:
            Updated team data
        """
        # Get team
        team_query = select(Team).where(Team.id == team_id)
        result = await db.execute(team_query)
        team = result.scalar_one_or_none()
        
        if not team:
            raise ValueError("Team not found")
        
        # Verify user is leader
        if team.leader_id != user_id:
            raise PermissionError("Only team leader can update team settings")
        
        # Apply updates
        allowed_fields = ["description", "max_members", "is_public"]
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(team, field, value)
        
        team.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(team)
        
        return await self.get_team(db, team_id)
    
    # ====================================================================
    # MEMBER MANAGEMENT
    # ====================================================================
    
    async def invite_member(
        self,
        db: AsyncSession,
        team_id: int,
        inviter_user_id: int,
        invitee_user_id: Optional[int] = None,
        invitee_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invite a user to join the team
        
        Args:
            db: Database session
            team_id: Team ID
            inviter_user_id: User sending invitation
            invitee_user_id: User to invite (if registered)
            invitee_email: Email to invite (if not registered)
            
        Returns:
            Invitation data
        """
        # Verify inviter is member
        is_member = await self._is_team_member(db, team_id, inviter_user_id)
        if not is_member:
            raise PermissionError("Only team members can send invitations")
        
        # Check team capacity
        team_query = select(Team).where(Team.id == team_id)
        result = await db.execute(team_query)
        team = result.scalar_one_or_none()
        
        if not team:
            raise ValueError("Team not found")
        
        member_count_query = select(func.count(TeamMember.id)).where(
            TeamMember.team_id == team_id,
            TeamMember.is_active == True
        )
        member_count = await db.execute(member_count_query)
        
        if member_count.scalar() >= team.max_members:
            raise ValueError("Team is full")
        
        # Check if already invited
        existing_query = select(TeamInvitation).where(
            TeamInvitation.team_id == team_id,
            TeamInvitation.status == "pending"
        )
        if invitee_user_id:
            existing_query = existing_query.where(TeamInvitation.invitee_user_id == invitee_user_id)
        else:
            existing_query = existing_query.where(TeamInvitation.invitee_email == invitee_email)
        
        existing = await db.execute(existing_query)
        if existing.scalar_one_or_none():
            raise ValueError("Invitation already pending")
        
        # Create invitation
        invitation = TeamInvitation(
            team_id=team_id,
            invitee_user_id=invitee_user_id,
            invitee_email=invitee_email,
            inviter_user_id=inviter_user_id,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        db.add(invitation)
        await db.commit()
        await db.refresh(invitation)
        
        return {
            "id": invitation.id,
            "team_id": invitation.team_id,
            "invitee_user_id": invitation.invitee_user_id,
            "invitee_email": invitation.invitee_email,
            "status": invitation.status,
            "expires_at": invitation.expires_at.isoformat(),
            "created_at": invitation.created_at.isoformat()
        }
    
    async def respond_to_invitation(
        self,
        db: AsyncSession,
        invitation_id: int,
        user_id: int,
        accept: bool
    ) -> Dict[str, Any]:
        """
        Accept or decline a team invitation
        
        Args:
            db: Database session
            invitation_id: Invitation ID
            user_id: User responding
            accept: True to accept, False to decline
            
        Returns:
            Response data
        """
        # Get invitation
        invite_query = select(TeamInvitation).where(TeamInvitation.id == invitation_id)
        result = await db.execute(invite_query)
        invitation = result.scalar_one_or_none()
        
        if not invitation:
            raise ValueError("Invitation not found")
        
        # Verify user is the invitee
        if invitation.invitee_user_id != user_id:
            raise PermissionError("You cannot respond to this invitation")
        
        # Check if still valid
        if invitation.status != "pending":
            raise ValueError(f"Invitation already {invitation.status}")
        
        if datetime.utcnow() > invitation.expires_at:
            invitation.status = "expired"
            await db.commit()
            raise ValueError("Invitation has expired")
        
        # Update invitation status
        invitation.status = "accepted" if accept else "declined"
        invitation.responded_at = datetime.utcnow()
        
        # If accepted, add to team
        if accept:
            member = TeamMember(
                team_id=invitation.team_id,
                user_id=user_id,
                role="member",
                contribution_percentage=0.0
            )
            db.add(member)
        
        await db.commit()
        
        return {
            "invitation_id": invitation_id,
            "status": invitation.status,
            "accepted": accept
        }
    
    async def join_team_by_code(
        self,
        db: AsyncSession,
        invite_code: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Join a team using invite code (for public teams)
        
        Args:
            db: Database session
            invite_code: Team invite code
            user_id: User joining
            
        Returns:
            Team membership data
        """
        # Find team
        team_query = select(Team).where(Team.invite_code == invite_code)
        result = await db.execute(team_query)
        team = result.scalar_one_or_none()
        
        if not team:
            raise ValueError("Invalid invite code")
        
        if not team.is_active:
            raise ValueError("Team is not active")
        
        # Check if already member
        is_member = await self._is_team_member(db, team.id, user_id)
        if is_member:
            raise ValueError("Already a team member")
        
        # Check capacity
        member_count_query = select(func.count(TeamMember.id)).where(
            TeamMember.team_id == team.id,
            TeamMember.is_active == True
        )
        member_count = await db.execute(member_count_query)
        
        if member_count.scalar() >= team.max_members:
            raise ValueError("Team is full")
        
        # Add member
        member = TeamMember(
            team_id=team.id,
            user_id=user_id,
            role="member",
            contribution_percentage=0.0
        )
        
        db.add(member)
        await db.commit()
        await db.refresh(member)
        
        return {
            "team_id": team.id,
            "team_name": team.name,
            "user_id": user_id,
            "role": member.role,
            "joined_at": member.joined_at.isoformat()
        }
    
    async def leave_team(
        self,
        db: AsyncSession,
        team_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Leave a team
        
        Args:
            db: Database session
            team_id: Team ID
            user_id: User leaving
            
        Returns:
            Confirmation
        """
        # Get membership
        member_query = select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
            TeamMember.is_active == True
        )
        result = await db.execute(member_query)
        member = result.scalar_one_or_none()
        
        if not member:
            raise ValueError("Not a team member")
        
        # Check if leader
        team_query = select(Team).where(Team.id == team_id)
        result = await db.execute(team_query)
        team = result.scalar_one_or_none()
        
        if team.leader_id == user_id:
            raise ValueError("Team leader cannot leave. Transfer leadership or disband team first.")
        
        # Mark as inactive
        member.is_active = False
        member.left_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "team_id": team_id,
            "user_id": user_id,
            "left_at": member.left_at.isoformat()
        }
    
    async def get_team_members(
        self,
        db: AsyncSession,
        team_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get all active team members
        
        Args:
            db: Database session
            team_id: Team ID
            
        Returns:
            List of member dictionaries
        """
        query = select(TeamMember, User).join(
            User, TeamMember.user_id == User.id
        ).where(
            TeamMember.team_id == team_id,
            TeamMember.is_active == True
        ).order_by(TeamMember.joined_at)
        
        result = await db.execute(query)
        members = result.all()
        
        member_list = []
        for member, user in members:
            member_list.append({
                "user_id": member.user_id,
                "display_name": user.display_name or user.email or f"User_{user.id}",
                "role": member.role,
                "total_contributed": member.total_contributed,
                "contribution_percentage": member.contribution_percentage,
                "joined_at": member.joined_at.isoformat()
            })
        
        return member_list
    
    # ====================================================================
    # TEAM FUNDING
    # ====================================================================
    
    async def contribute_to_pool(
        self,
        db: AsyncSession,
        team_id: int,
        user_id: int,
        amount: float,
        transaction_signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Contribute funds to team pool
        
        Args:
            db: Database session
            team_id: Team ID
            user_id: Contributing user
            amount: Amount to contribute
            transaction_signature: Solana transaction signature
            
        Returns:
            Funding record
        """
        # Verify member
        is_member = await self._is_team_member(db, team_id, user_id)
        if not is_member:
            raise PermissionError("Only team members can contribute")
        
        # Create funding record
        funding = TeamFunding(
            team_id=team_id,
            user_id=user_id,
            amount=amount,
            transaction_signature=transaction_signature,
            status="completed"
        )
        
        db.add(funding)
        
        # Update team pool
        team_query = select(Team).where(Team.id == team_id)
        result = await db.execute(team_query)
        team = result.scalar_one()
        team.total_pool += amount
        
        # Update member contribution
        member_query = select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
            TeamMember.is_active == True
        )
        result = await db.execute(member_query)
        member = result.scalar_one()
        member.total_contributed += amount
        
        # Recalculate contribution percentages
        await self._recalculate_contributions(db, team_id)
        
        await db.commit()
        await db.refresh(funding)
        
        return {
            "id": funding.id,
            "team_id": team_id,
            "user_id": user_id,
            "amount": amount,
            "new_team_pool": team.total_pool,
            "user_total_contributed": member.total_contributed,
            "created_at": funding.created_at.isoformat()
        }
    
    # ====================================================================
    # TEAM ATTEMPTS
    # ====================================================================
    
    async def record_team_attempt(
        self,
        db: AsyncSession,
        team_id: int,
        user_id: int,
        conversation_id: int,
        cost: float,
        use_team_pool: bool,
        was_successful: bool,
        threat_score: float,
        ai_response: str
    ) -> Dict[str, Any]:
        """
        Record a team attempt
        
        Args:
            db: Database session
            team_id: Team ID
            user_id: Member who made the attempt
            conversation_id: Conversation ID
            cost: Query cost
            use_team_pool: Whether to use team pool for payment
            was_successful: Whether attempt succeeded
            threat_score: Threat score from AI
            ai_response: AI response text
            
        Returns:
            Attempt record
        """
        # Verify member
        is_member = await self._is_team_member(db, team_id, user_id)
        if not is_member:
            raise PermissionError("Only team members can make attempts")
        
        # Get team
        team_query = select(Team).where(Team.id == team_id)
        result = await db.execute(team_query)
        team = result.scalar_one()
        
        # Calculate funding split
        if use_team_pool:
            if team.total_pool < cost:
                raise ValueError("Insufficient team pool funds")
            funded_by_pool = cost
            funded_by_initiator = 0.0
            team.total_pool -= cost
        else:
            funded_by_pool = 0.0
            funded_by_initiator = cost
        
        # Create attempt record
        attempt = TeamAttempt(
            team_id=team_id,
            conversation_id=conversation_id,
            initiated_by=user_id,
            cost=cost,
            funded_by_pool=funded_by_pool,
            funded_by_initiator=funded_by_initiator,
            was_successful=was_successful,
            threat_score=threat_score,
            ai_response=ai_response
        )
        
        db.add(attempt)
        
        # Update team stats
        team.total_attempts += 1
        team.total_spent += cost
        
        await db.commit()
        await db.refresh(attempt)
        
        return {
            "id": attempt.id,
            "team_id": team_id,
            "initiated_by": user_id,
            "cost": cost,
            "funded_by_pool": funded_by_pool,
            "funded_by_initiator": funded_by_initiator,
            "was_successful": was_successful,
            "threat_score": threat_score,
            "created_at": attempt.created_at.isoformat()
        }
    
    # ====================================================================
    # TEAM CHAT
    # ====================================================================
    
    async def send_message(
        self,
        db: AsyncSession,
        team_id: int,
        user_id: int,
        content: str,
        message_type: str = "text",
        extra_data: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        Send a message in team chat
        
        Args:
            db: Database session
            team_id: Team ID
            user_id: User sending message
            content: Message content
            message_type: Type of message (text, system, strategy, attempt_result)
            extra_data: Optional metadata
            
        Returns:
            Message record
        """
        # Verify member
        is_member = await self._is_team_member(db, team_id, user_id)
        if not is_member:
            raise PermissionError("Only team members can send messages")
        
        # Create message
        message = TeamMessage(
            team_id=team_id,
            user_id=user_id,
            content=content,
            message_type=message_type,
            extra_data=extra_data
        )
        
        db.add(message)
        await db.commit()
        await db.refresh(message)
        
        return {
            "id": message.id,
            "team_id": team_id,
            "user_id": user_id,
            "content": content,
            "message_type": message_type,
            "created_at": message.created_at.isoformat()
        }
    
    async def get_team_messages(
        self,
        db: AsyncSession,
        team_id: int,
        user_id: int,
        limit: int = 50,
        before_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get team chat messages
        
        Args:
            db: Database session
            team_id: Team ID
            user_id: User requesting messages (must be member)
            limit: Max messages to return
            before_id: Get messages before this ID (pagination)
            
        Returns:
            List of message dictionaries
        """
        # Verify member
        is_member = await self._is_team_member(db, team_id, user_id)
        if not is_member:
            raise PermissionError("Only team members can view messages")
        
        # Build query
        query = select(TeamMessage, User).join(
            User, TeamMessage.user_id == User.id
        ).where(
            TeamMessage.team_id == team_id,
            TeamMessage.is_deleted == False
        )
        
        if before_id:
            query = query.where(TeamMessage.id < before_id)
        
        query = query.order_by(desc(TeamMessage.created_at)).limit(limit)
        
        result = await db.execute(query)
        messages = result.all()
        
        message_list = []
        for message, user in reversed(messages):  # Reverse to get chronological order
            message_list.append({
                "id": message.id,
                "user_id": message.user_id,
                "display_name": user.display_name or user.email or f"User_{user.id}",
                "content": message.content,
                "message_type": message.message_type,
                "extra_data": message.extra_data,
                "created_at": message.created_at.isoformat()
            })
        
        return message_list
    
    # ====================================================================
    # PRIZE DISTRIBUTION
    # ====================================================================
    
    async def create_prize_distribution(
        self,
        db: AsyncSession,
        team_id: int,
        winner_id: int,
        total_prize: float,
        distribution_method: str = "proportional"
    ) -> Dict[str, Any]:
        """
        Create prize distribution for team win
        
        Args:
            db: Database session
            team_id: Team ID
            winner_id: Winner record ID
            total_prize: Total prize amount
            distribution_method: How to split (proportional, equal, custom)
            
        Returns:
            Distribution record with member splits
        """
        # Get active members
        members = await self.get_team_members(db, team_id)
        
        if not members:
            raise ValueError("No active team members")
        
        # Create distribution record
        distribution = TeamPrizeDistribution(
            team_id=team_id,
            winner_id=winner_id,
            total_prize=total_prize,
            distribution_method=distribution_method,
            status="pending"
        )
        
        db.add(distribution)
        await db.flush()  # Get distribution ID
        
        # Calculate splits
        member_prizes = []
        
        if distribution_method == "equal":
            # Equal split
            per_member = total_prize / len(members)
            for member in members:
                member_prizes.append(TeamMemberPrize(
                    distribution_id=distribution.id,
                    user_id=member["user_id"],
                    amount=per_member,
                    percentage=100.0 / len(members),
                    status="pending"
                ))
        
        elif distribution_method == "proportional":
            # Proportional to contributions
            for member in members:
                member_prizes.append(TeamMemberPrize(
                    distribution_id=distribution.id,
                    user_id=member["user_id"],
                    amount=total_prize * (member["contribution_percentage"] / 100),
                    percentage=member["contribution_percentage"],
                    status="pending"
                ))
        
        # Add all member prizes
        for prize in member_prizes:
            db.add(prize)
        
        await db.commit()
        await db.refresh(distribution)
        
        # Return full distribution details
        prize_list = []
        for prize in member_prizes:
            prize_list.append({
                "user_id": prize.user_id,
                "amount": prize.amount,
                "percentage": prize.percentage,
                "status": prize.status
            })
        
        return {
            "distribution_id": distribution.id,
            "team_id": team_id,
            "total_prize": total_prize,
            "distribution_method": distribution_method,
            "member_prizes": prize_list,
            "status": distribution.status
        }
    
    # ====================================================================
    # HELPER METHODS
    # ====================================================================
    
    async def _is_team_member(
        self,
        db: AsyncSession,
        team_id: int,
        user_id: int
    ) -> bool:
        """Check if user is an active team member"""
        query = select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
            TeamMember.is_active == True
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def _recalculate_contributions(
        self,
        db: AsyncSession,
        team_id: int
    ):
        """Recalculate contribution percentages for all members"""
        # Get all active members
        query = select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.is_active == True
        )
        result = await db.execute(query)
        members = result.scalars().all()
        
        # Calculate total contributions
        total_contributed = sum(m.total_contributed for m in members)
        
        # Update percentages
        if total_contributed > 0:
            for member in members:
                member.contribution_percentage = (member.total_contributed / total_contributed) * 100
        else:
            for member in members:
                member.contribution_percentage = 100.0 / len(members)
    
    def _generate_invite_code(self, length: int = 8) -> str:
        """Generate a random invite code"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))


# Global singleton
team_service = TeamService()

