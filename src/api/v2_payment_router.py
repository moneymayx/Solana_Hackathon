"""
V2 Payment API Router - ACTIVE (Production)

Handles V2 smart contract payment processing.
This router provides API endpoints for V2 smart contract payments.

✅ ACTIVE: All payments flow through V2 smart contracts on-chain.
Backend only provides API endpoints - no fund routing in backend code.

See ARCHITECTURE.md for system architecture.
See docs/V2_INTEGRATION_GUIDE.md for integration guide.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import os

from ..database import get_db
from ..services.v2.payment_processor import get_v2_payment_processor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["V2 Payments"])

# Check if V2 is enabled
USE_V2 = os.getenv("USE_CONTRACT_V2", "false").lower() == "true"


class ProcessPaymentRequest(BaseModel):
    """Request model for processing V2 entry payment"""
    user_wallet_address: str = Field(..., description="User's wallet address (base58)")
    bounty_id: int = Field(default=1, description="Bounty ID (typically 1)")
    entry_amount_usdc: float = Field(..., description="Payment amount in USDC (e.g., 15.0)")


class ProcessPaymentResponse(BaseModel):
    """Response model for payment processing"""
    success: bool
    transaction_signature: Optional[str] = None
    explorer_url: Optional[str] = None
    bounty_id: int
    amount: int  # Amount in smallest unit
    error: Optional[str] = None


class BountyStatusResponse(BaseModel):
    """Response model for bounty status"""
    success: bool
    bounty_id: int
    bounty_pda: Optional[str] = None
    error: Optional[str] = None


@router.get("/bounty/{bounty_id}/status", response_model=BountyStatusResponse)
async def get_bounty_status(bounty_id: int):
    """
    Get status of a V2 bounty.
    
    Note: This endpoint works regardless of USE_CONTRACT_V2 flag.
    """
    try:
        processor = get_v2_payment_processor()
        result = await processor.get_bounty_status(bounty_id)
        
        return BountyStatusResponse(
            success=result.get("success", False),
            bounty_id=bounty_id,
            bounty_pda=result.get("bounty_pda"),
            error=result.get("error"),
        )
    except Exception as e:
        logger.error(f"Error getting bounty status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payment/process", response_model=ProcessPaymentResponse)
async def process_v2_payment(
    request: ProcessPaymentRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Process V2 entry payment.
    
    ⚠️ NOTE: This endpoint requires user authentication and keypair retrieval.
    Currently returns a placeholder response indicating integration is ready.
    
    In production, you would:
    1. Authenticate the user
    2. Retrieve their keypair from secure storage or session
    3. Call processor.process_entry_payment()
    
    Args:
        request: Payment request with wallet address, bounty_id, and amount
        db: Database session
    
    Returns:
        Payment result with transaction signature
    """
    if not USE_V2:
        raise HTTPException(
            status_code=503,
            detail="V2 contract is not enabled. Set USE_CONTRACT_V2=true to enable."
        )
    
    try:
        processor = get_v2_payment_processor()
        
        # Convert USDC to smallest unit (6 decimals)
        entry_amount = int(request.entry_amount_usdc * 1_000_000)
        
        logger.info(
            f"🔄 V2 Payment Request: "
            f"Wallet={request.user_wallet_address}, "
            f"Bounty={request.bounty_id}, "
            f"Amount={entry_amount}"
        )
        
        # TODO: In production, implement user keypair retrieval
        # For now, return a placeholder indicating the integration is ready
        # 
        # Example implementation:
        # from solders.pubkey import Pubkey
        # from solders.keypair import Keypair
        # 
        # # Get user keypair from secure storage (implementation depends on your auth system)
        # user_keypair = await get_user_keypair_from_auth(request.user_wallet_address)
        # 
        # if not user_keypair:
        #     raise HTTPException(status_code=401, detail="User not authenticated")
        # 
        # result = await processor.process_entry_payment(
        #     user_keypair=user_keypair,
        #     bounty_id=request.bounty_id,
        #     entry_amount=entry_amount,
        # )
        # 
        # if not result.get("success"):
        #     raise HTTPException(status_code=400, detail=result.get("error", "Payment failed"))
        # 
        # return ProcessPaymentResponse(
        #     success=True,
        #     transaction_signature=result["transaction_signature"],
        #     explorer_url=result["explorer_url"],
        #     bounty_id=request.bounty_id,
        #     amount=entry_amount,
        # )
        
        return ProcessPaymentResponse(
            success=False,
            bounty_id=request.bounty_id,
            amount=entry_amount,
            error="User keypair retrieval not implemented. See endpoint documentation.",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing V2 payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_v2_config() -> Dict[str, Any]:
    """
    Get V2 contract configuration (public info only).
    
    This endpoint returns public configuration that can be used by frontend.
    """
    processor = get_v2_payment_processor()
    
    return {
        "success": True,
        "enabled": USE_V2,
        "program_id": str(processor.program_id),
        "usdc_mint": str(processor.usdc_mint),
        "bounty_pool_wallet": str(processor.bounty_pool_wallet),
        "operational_wallet": str(processor.operational_wallet),
        "buyback_wallet": str(processor.buyback_wallet),
        "staking_wallet": str(processor.staking_wallet),
        "rpc_endpoint": processor.rpc_endpoint,
    }

