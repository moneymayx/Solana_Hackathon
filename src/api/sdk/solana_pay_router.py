"""
Solana Pay SDK Test Router - Isolated Testing Endpoints

Provides test endpoints for Solana Pay protocol functionality.
All endpoints are prefixed with /api/sdk-test/solana-pay/ to avoid conflicts.

Usage: Set ENABLE_SOLANA_PAY_SDK=true in environment to enable
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import os

from ...database import get_db
from ...services.sdk.solana_pay_service import solana_pay_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sdk-test/solana-pay", tags=["SDK Test - Solana Pay"])

# Only enable if Solana Pay SDK is enabled
ENABLE_SOLANA_PAY = os.getenv("ENABLE_SOLANA_PAY_SDK", "false").lower() == "true"


class CreateTransferRequestRequest(BaseModel):
    """Request model for creating Solana Pay Transfer Request URL
    
    Following official Solana Pay specification:
    https://launch.solana.com/docs/solana-pay
    """
    recipient: str = Field(..., description="Recipient wallet address (base58, required)")
    amount: Optional[float] = Field(None, description="Payment amount in SOL or token units")
    label: Optional[str] = Field(None, description="Merchant or payment label")
    message: Optional[str] = Field(None, description="Payment message/description")
    spl_token: Optional[str] = Field(None, description="SPL token mint address (optional, defaults to SOL)")
    reference: Optional[str] = Field(None, description="Reference pubkey for payment tracking")


class VerifyPaymentRequest(BaseModel):
    """Request model for verifying payment"""
    transaction_signature: str = Field(..., description="Transaction signature to verify")
    expected_amount: Optional[float] = Field(None, description="Expected payment amount")
    expected_recipient: Optional[str] = Field(None, description="Expected recipient")
    expected_token: Optional[str] = Field(None, description="Expected token mint")


@router.get("/status")
async def get_solana_pay_status():
    """Check if Solana Pay SDK is enabled and configured"""
    compatibility = solana_pay_service.check_v2_compatibility()
    
    return {
        "enabled": solana_pay_service.is_enabled(),
        "rpc_endpoint": solana_pay_service.rpc_endpoint,
        "v2_compatibility": compatibility
    }


@router.post("/create-transfer-request")
async def create_transfer_request_url(
    request: CreateTransferRequestRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Create a Solana Pay Transfer Request URL
    
    Generates a transfer request URL following official Solana Pay specification.
    This creates a non-interactive payment URL for simple SOL or SPL token transfers.
    
    Format: solana:<recipient>?amount=<amount>&label=<label>&message=<message>&spl-token=<mint>&reference=<reference>
    
    Example: solana:recipient?amount=0.01&label=Coffee%20Shop&message=Grande%20Latte
    
    Note: This is for simple transfer payments. Your V2 contract requires custom
    instructions with PDAs and multi-recipient splits, so use custom instructions
    for contract entry payments.
    
    Reference: https://launch.solana.com/docs/solana-pay
    """
    if not ENABLE_SOLANA_PAY:
        raise HTTPException(
            status_code=403,
            detail="Solana Pay SDK is disabled. Set ENABLE_SOLANA_PAY_SDK=true to enable."
        )
    
    try:
        result = solana_pay_service.create_transfer_request_url(
            recipient=request.recipient,
            amount=request.amount,
            label=request.label,
            message=request.message,
            spl_token=request.spl_token,
            reference=request.reference
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to create payment URL")
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error creating Solana Pay URL: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@router.post("/verify-payment")
async def verify_payment(
    request: VerifyPaymentRequest,
    session: AsyncSession = Depends(get_db)
):
    """Verify a Solana Pay payment transaction"""
    if not ENABLE_SOLANA_PAY:
        raise HTTPException(
            status_code=403,
            detail="Solana Pay SDK is disabled. Set ENABLE_SOLANA_PAY_SDK=true to enable."
        )
    
    try:
        result = await solana_pay_service.verify_payment_transaction(
            transaction_signature=request.transaction_signature,
            expected_amount=request.expected_amount,
            expected_recipient=request.expected_recipient,
            expected_token=request.expected_token
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to verify payment")
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@router.get("/v2-compatibility")
async def check_v2_compatibility():
    """Check Solana Pay compatibility with V2 contract"""
    if not ENABLE_SOLANA_PAY:
        raise HTTPException(
            status_code=403,
            detail="Solana Pay SDK is disabled. Set ENABLE_SOLANA_PAY_SDK=true to enable."
        )
    
    return solana_pay_service.check_v2_compatibility()

