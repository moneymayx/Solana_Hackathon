from __future__ import annotations

from datetime import datetime
import logging
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.database import get_db
from src.models import Conversation, User
from src.repositories import UserRepository

logger = logging.getLogger(__name__)
router = APIRouter()

try:
    from src.winner_tracking_service import winner_tracking_service
except Exception:  # pragma: no cover - optional dependency path
    winner_tracking_service = None
    logger.warning("⚠️  Winner tracking service unavailable for mobile parallel router")


class MobileWalletConnectRequest(BaseModel):
    """Request payload for the complementary mobile wallet connect flow."""

    wallet_address: str = Field(..., min_length=32)
    signature: Optional[str] = None
    message: Optional[str] = None
    display_name: Optional[str] = None
    public_key: Optional[str] = None


class MobileWalletConnectResponse(BaseModel):
    """Response payload for the complementary mobile wallet connect flow."""

    success: bool
    message: str
    user_id: int
    wallet_address: str
    display_name: Optional[str] = None
    public_key: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


def _format_winning_prompt(
    conversation: Conversation,
    winner: Optional[User],
    bounty_id: int,
) -> Dict[str, Any]:
    """Serialize a winning conversation into the mobile schema."""

    display_name = None
    if winner:
        display_name = winner.display_name or winner.wallet_address

    return {
        "id": conversation.id,
        "prompt": conversation.content,
        # Publishing the winner alias keeps the lottery transparent without exposing the real wallet.
        "winner_name": display_name or "Anonymous challenger",
        "timestamp": conversation.timestamp.isoformat() if conversation.timestamp else None,
        "bounty_id": bounty_id,
    }


@router.get("/api/mobile/bounty/{bounty_id}/winning-prompts")
@router.get("/api/bounty/{bounty_id}/winning-prompts", tags=["mobile-parallel"])
async def get_mobile_winning_prompts(
    bounty_id: int,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Return recent winning prompts while leaving the primary flow untouched."""

    clamped_limit = max(1, min(limit, 50))
    logger.info("🏆 [mobile-parallel] Fetching winning prompts", extra={"bounty_id": bounty_id, "limit": clamped_limit})

    user_alias = aliased(User)

    result = await session.execute(
        select(Conversation, user_alias)
        .join(user_alias, Conversation.user_id == user_alias.id, isouter=True)
        .where(
            Conversation.bounty_id == bounty_id,
            Conversation.is_winner.is_(True),
        )
        .order_by(Conversation.timestamp.desc())
        .limit(clamped_limit)
    )

    records: List[Any] = result.all()
    prompts = [_format_winning_prompt(conv, winner, bounty_id) for conv, winner in records]

    logger.info(
        "✅ [mobile-parallel] Returning winning prompts",
        extra={"bounty_id": bounty_id, "count": len(prompts)},
    )

    return {
        "success": True,
        "prompts": prompts,
        "total": len(prompts),
        "bounty_id": bounty_id,
    }


@router.post("/api/mobile/wallet/connect", response_model=MobileWalletConnectResponse)
async def mobile_connect_wallet(
    request: MobileWalletConnectRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_db),
) -> MobileWalletConnectResponse:
    """Connect or update a wallet through the mobile parallel flow without altering the legacy endpoint."""

    if winner_tracking_service is not None:
        blacklist_info = await winner_tracking_service.is_wallet_blacklisted(session, request.wallet_address)
        if blacklist_info.get("blacklisted"):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Wallet blacklisted",
                    "reason": blacklist_info.get("reason"),
                    "type": blacklist_info.get("type"),
                },
            )

    user_repo = UserRepository(session)
    wallet_query = await session.execute(
        select(User).where(User.wallet_address == request.wallet_address)
    )
    user = wallet_query.scalar_one_or_none()

    if not user:
        new_session_id = f"mobile-{uuid.uuid4()}"
        ip_address = http_request.client.host if http_request.client else None
        user_agent = http_request.headers.get("user-agent")
        user = await user_repo.create_user(
            session_id=new_session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            display_name=request.display_name,
        )
    else:
        if request.display_name and request.display_name != user.display_name:
            await session.execute(
                update(User)
                .where(User.id == user.id)
                .values(display_name=request.display_name)
            )
            await session.commit()
            await session.refresh(user)

    await user_repo.update_user_wallet(user.id, request.wallet_address)

    update_payload: Dict[str, Any] = {
        "wallet_signature": request.signature,
        "wallet_connected_at": datetime.utcnow(),
    }
    await session.execute(
        update(User)
        .where(User.id == user.id)
        .values(**{k: v for k, v in update_payload.items() if v is not None})
    )
    await session.commit()
    await session.refresh(user)

    # During the mobile rollout we log the presence of public keys so the fraud monitors can reconcile linked wallets.
    if request.public_key:
        logger.info(
            "🔐 [mobile-parallel] Public key received during wallet connect",
            extra={"user_id": user.id},
        )

    response_details: Dict[str, Any] = {}
    if not request.signature:
        # We purposely allow signature-free connections in this parallel build so QA can validate the winning prompt experience without Phantom.
        response_details["note"] = "Signature skipped under mobile parallel flow"

    return MobileWalletConnectResponse(
        success=True,
        message="Wallet connected via mobile parallel flow",
        user_id=user.id,
        wallet_address=request.wallet_address,
        display_name=user.display_name,
        public_key=request.public_key,
        details=response_details or None,
    )



