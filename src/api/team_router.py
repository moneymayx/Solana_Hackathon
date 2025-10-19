"""
Phase 3 API: Team Collaboration

Endpoints for team creation, management, funding, attempts, chat, and prize distribution
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from ..database import get_db
from ..team_service import TeamService

router = APIRouter(prefix="/api/teams", tags=["Team Collaboration"])

# Initialize service
team_service = TeamService()


# ===========================
# Request/Response Models
# ===========================

class CreateTeamRequest(BaseModel):
    leader_id: int
    name: str
    description: Optional[str] = None
    max_members: int = 5
    is_public: bool = True


class UpdateTeamRequest(BaseModel):
    description: Optional[str] = None
    max_members: Optional[int] = None
    is_public: Optional[bool] = None


class InviteMemberRequest(BaseModel):
    team_id: int
    inviter_user_id: int
    invitee_user_id: Optional[int] = None
    invitee_email: Optional[EmailStr] = None


class RespondInvitationRequest(BaseModel):
    user_id: int
    accept: bool


class JoinTeamRequest(BaseModel):
    invite_code: str
    user_id: int


class LeaveTeamRequest(BaseModel):
    user_id: int


class ContributeRequest(BaseModel):
    user_id: int
    amount: float
    transaction_signature: Optional[str] = None


class RecordAttemptRequest(BaseModel):
    user_id: int
    conversation_id: int
    cost: float
    use_team_pool: bool
    was_successful: bool
    threat_score: float
    ai_response: str


class SendMessageRequest(BaseModel):
    user_id: int
    content: str
    message_type: str = "text"
    extra_data: Optional[Dict[str, Any]] = None


class CreatePrizeDistributionRequest(BaseModel):
    winner_id: int
    total_prize: float
    distribution_method: str = "proportional"  # proportional or equal


# ===========================
# Team CRUD Endpoints
# ===========================

@router.post("/create")
async def create_team(
    request: CreateTeamRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new team
    
    Returns team data including unique invite code
    """
    try:
        team = await team_service.create_team(
            db=db,
            leader_id=request.leader_id,
            name=request.name,
            description=request.description,
            max_members=request.max_members,
            is_public=request.is_public
        )
        
        return {
            "success": True,
            "team": team
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}")
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get team details
    """
    try:
        team = await team_service.get_team(db=db, team_id=team_id)
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return team
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_public_teams(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Browse all public teams
    
    Useful for team discovery
    """
    try:
        teams = await team_service.list_public_teams(
            db=db,
            limit=limit,
            offset=offset
        )
        
        return {
            "total": len(teams),
            "teams": teams,
            "limit": limit,
            "offset": offset
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{team_id}")
async def update_team(
    team_id: int,
    user_id: int,
    request: UpdateTeamRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update team settings (leader only)
    """
    try:
        updates = request.dict(exclude_unset=True)
        
        team = await team_service.update_team(
            db=db,
            team_id=team_id,
            user_id=user_id,
            **updates
        )
        
        return {
            "success": True,
            "team": team
        }
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Member Management Endpoints
# ===========================

@router.post("/{team_id}/invite")
async def invite_member(
    team_id: int,
    request: InviteMemberRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Invite a user to join the team
    
    Can invite by user_id (registered) or email (non-registered)
    """
    try:
        if not request.invitee_user_id and not request.invitee_email:
            raise HTTPException(
                status_code=400,
                detail="Must provide either invitee_user_id or invitee_email"
            )
        
        invitation = await team_service.invite_member(
            db=db,
            team_id=team_id,
            inviter_user_id=request.inviter_user_id,
            invitee_user_id=request.invitee_user_id,
            invitee_email=request.invitee_email
        )
        
        return {
            "success": True,
            "invitation": invitation
        }
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invitations/{invitation_id}/respond")
async def respond_to_invitation(
    invitation_id: int,
    request: RespondInvitationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Accept or decline a team invitation
    """
    try:
        response = await team_service.respond_to_invitation(
            db=db,
            invitation_id=invitation_id,
            user_id=request.user_id,
            accept=request.accept
        )
        
        return {
            "success": True,
            "response": response
        }
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/join")
async def join_team_by_code(
    request: JoinTeamRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Join a team using invite code
    
    Works for public teams
    """
    try:
        membership = await team_service.join_team_by_code(
            db=db,
            invite_code=request.invite_code,
            user_id=request.user_id
        )
        
        return {
            "success": True,
            "membership": membership
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{team_id}/leave")
async def leave_team(
    team_id: int,
    request: LeaveTeamRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Leave a team (non-leaders only)
    """
    try:
        result = await team_service.leave_team(
            db=db,
            team_id=team_id,
            user_id=request.user_id
        )
        
        return {
            "success": True,
            "result": result
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}/members")
async def get_team_members(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all active team members
    """
    try:
        members = await team_service.get_team_members(
            db=db,
            team_id=team_id
        )
        
        return {
            "team_id": team_id,
            "member_count": len(members),
            "members": members
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Team Funding Endpoints
# ===========================

@router.post("/{team_id}/contribute")
async def contribute_to_pool(
    team_id: int,
    request: ContributeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Contribute funds to team pool
    
    Increases team's shared pool and your contribution percentage
    """
    try:
        funding = await team_service.contribute_to_pool(
            db=db,
            team_id=team_id,
            user_id=request.user_id,
            amount=request.amount,
            transaction_signature=request.transaction_signature
        )
        
        return {
            "success": True,
            "funding": funding
        }
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}/pool")
async def get_team_pool(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get current team pool balance
    """
    try:
        team = await team_service.get_team(db=db, team_id=team_id)
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return {
            "team_id": team_id,
            "total_pool": team["total_pool"],
            "total_spent": team["total_spent"],
            "remaining": team["total_pool"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Team Attempts Endpoints
# ===========================

@router.post("/{team_id}/attempts")
async def record_team_attempt(
    team_id: int,
    request: RecordAttemptRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Record a team attempt
    
    Can be funded by team pool or individual wallet
    """
    try:
        attempt = await team_service.record_team_attempt(
            db=db,
            team_id=team_id,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            cost=request.cost,
            use_team_pool=request.use_team_pool,
            was_successful=request.was_successful,
            threat_score=request.threat_score,
            ai_response=request.ai_response
        )
        
        return {
            "success": True,
            "attempt": attempt
        }
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}/attempts")
async def get_team_attempts(
    team_id: int,
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get team's attempt history
    """
    try:
        from ..models import TeamAttempt
        from sqlalchemy import select, desc
        
        query = select(TeamAttempt).where(
            TeamAttempt.team_id == team_id
        ).order_by(desc(TeamAttempt.created_at)).limit(limit)
        
        result = await db.execute(query)
        attempts = result.scalars().all()
        
        attempt_list = []
        for attempt in attempts:
            attempt_list.append({
                "id": attempt.id,
                "initiated_by": attempt.initiated_by,
                "cost": attempt.cost,
                "funded_by_pool": attempt.funded_by_pool,
                "funded_by_initiator": attempt.funded_by_initiator,
                "was_successful": attempt.was_successful,
                "threat_score": attempt.threat_score,
                "created_at": attempt.created_at.isoformat()
            })
        
        return {
            "team_id": team_id,
            "total_attempts": len(attempt_list),
            "attempts": attempt_list
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Team Chat Endpoints
# ===========================

@router.post("/{team_id}/messages")
async def send_message(
    team_id: int,
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message in team chat
    
    Message types:
    - text: Regular chat
    - system: System notifications
    - strategy: Strategy discussions
    - attempt_result: Attempt results
    """
    try:
        message = await team_service.send_message(
            db=db,
            team_id=team_id,
            user_id=request.user_id,
            content=request.content,
            message_type=request.message_type,
            extra_data=request.extra_data
        )
        
        return {
            "success": True,
            "message": message
        }
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}/messages")
async def get_team_messages(
    team_id: int,
    user_id: int,
    limit: int = Query(default=50, le=200),
    before_id: Optional[int] = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get team chat messages
    
    Supports pagination with before_id
    """
    try:
        messages = await team_service.get_team_messages(
            db=db,
            team_id=team_id,
            user_id=user_id,
            limit=limit,
            before_id=before_id
        )
        
        return {
            "team_id": team_id,
            "total_messages": len(messages),
            "messages": messages
        }
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Prize Distribution Endpoints
# ===========================

@router.post("/{team_id}/prizes/distribute")
async def create_prize_distribution(
    team_id: int,
    request: CreatePrizeDistributionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create prize distribution for team win
    
    Distribution methods:
    - proportional: Based on contribution percentage
    - equal: Split evenly among all members
    """
    try:
        if request.distribution_method not in ["proportional", "equal"]:
            raise HTTPException(
                status_code=400,
                detail="Distribution method must be 'proportional' or 'equal'"
            )
        
        distribution = await team_service.create_prize_distribution(
            db=db,
            team_id=team_id,
            winner_id=request.winner_id,
            total_prize=request.total_prize,
            distribution_method=request.distribution_method
        )
        
        return {
            "success": True,
            "distribution": distribution
        }
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}/prizes")
async def get_team_prize_distributions(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all prize distributions for a team
    """
    try:
        from ..models import TeamPrizeDistribution
        from sqlalchemy import select, desc
        
        query = select(TeamPrizeDistribution).where(
            TeamPrizeDistribution.team_id == team_id
        ).order_by(desc(TeamPrizeDistribution.created_at))
        
        result = await db.execute(query)
        distributions = result.scalars().all()
        
        distribution_list = []
        for dist in distributions:
            distribution_list.append({
                "id": dist.id,
                "winner_id": dist.winner_id,
                "total_prize": dist.total_prize,
                "distribution_method": dist.distribution_method,
                "status": dist.status,
                "created_at": dist.created_at.isoformat(),
                "distributed_at": dist.distributed_at.isoformat() if dist.distributed_at else None
            })
        
        return {
            "team_id": team_id,
            "total_distributions": len(distribution_list),
            "distributions": distribution_list
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/prizes")
async def get_user_team_prizes(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all prize shares for a user across all teams
    """
    try:
        from ..models import TeamMemberPrize
        from sqlalchemy import select, desc
        
        query = select(TeamMemberPrize).where(
            TeamMemberPrize.user_id == user_id
        ).order_by(desc(TeamMemberPrize.created_at))
        
        result = await db.execute(query)
        prizes = result.scalars().all()
        
        prize_list = []
        for prize in prizes:
            prize_list.append({
                "id": prize.id,
                "distribution_id": prize.distribution_id,
                "amount": prize.amount,
                "percentage": prize.percentage,
                "status": prize.status,
                "created_at": prize.created_at.isoformat(),
                "paid_at": prize.paid_at.isoformat() if prize.paid_at else None
            })
        
        return {
            "user_id": user_id,
            "total_prizes": len(prize_list),
            "total_earned": sum(p["amount"] for p in prize_list if p["status"] == "paid"),
            "prizes": prize_list
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Team Statistics
# ===========================

@router.get("/{team_id}/stats")
async def get_team_statistics(
    team_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive team statistics
    """
    try:
        # Get team data
        team = await team_service.get_team(db=db, team_id=team_id)
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Get members
        members = await team_service.get_team_members(db=db, team_id=team_id)
        
        # Calculate success rate
        from ..models import TeamAttempt
        from sqlalchemy import select, func
        
        total_attempts_query = select(func.count(TeamAttempt.id)).where(
            TeamAttempt.team_id == team_id
        )
        result = await db.execute(total_attempts_query)
        total_attempts = result.scalar() or 0
        
        successful_attempts_query = select(func.count(TeamAttempt.id)).where(
            TeamAttempt.team_id == team_id,
            TeamAttempt.was_successful == True
        )
        result = await db.execute(successful_attempts_query)
        successful_attempts = result.scalar() or 0
        
        success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            "team_id": team_id,
            "name": team["name"],
            "member_count": len(members),
            "total_pool": team["total_pool"],
            "total_attempts": total_attempts,
            "successful_attempts": successful_attempts,
            "success_rate": success_rate,
            "total_spent": team["total_spent"],
            "avg_cost_per_attempt": team["total_spent"] / total_attempts if total_attempts > 0 else 0,
            "created_at": team["created_at"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Health & Status
# ===========================

@router.get("/health")
async def team_health():
    """
    Check health of team collaboration services
    """
    return {
        "team_service_active": True,
        "features": {
            "team_creation": True,
            "member_management": True,
            "team_funding": True,
            "collaborative_attempts": True,
            "team_chat": True,
            "prize_distribution": True
        }
    }

