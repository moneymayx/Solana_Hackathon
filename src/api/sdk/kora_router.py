"""
Kora SDK Test Router - Isolated Testing Endpoints

Provides test endpoints for Kora fee abstraction functionality.
All endpoints are prefixed with /api/sdk-test/kora/ to avoid conflicts.

Usage: Set ENABLE_KORA_SDK=true in environment to enable
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import os

from ...database import get_db
from ...services.sdk.kora_service import kora_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sdk-test/kora", tags=["SDK Test - Kora"])

# Only enable if Kora SDK is enabled
ENABLE_KORA = os.getenv("ENABLE_KORA_SDK", "false").lower() == "true"


class SignTransactionRequest(BaseModel):
    """Request model for signing transaction via Kora"""
    transaction_base64: str = Field(..., description="Base64-encoded transaction")
    options: Optional[Dict[str, Any]] = Field(None, description="Optional signing options")


class SignAndSendRequest(BaseModel):
    """Request model for signing and sending transaction"""
    transaction_base64: str = Field(..., description="Base64-encoded transaction")
    options: Optional[Dict[str, Any]] = Field(None, description="Optional send options")


class EstimateFeeRequest(BaseModel):
    """Request model for fee estimation"""
    transaction_base64: str = Field(..., description="Base64-encoded transaction")
    fee_token: Optional[str] = Field(None, description="Token to estimate fees in")




@router.get("/status")
async def get_kora_status():
    """Check if Kora SDK is enabled and configured"""
    return {
        "enabled": kora_service.is_enabled(),
        "rpc_url": kora_service.rpc_url,
        "private_key_configured": kora_service.private_key is not None,
        "cli_path": kora_service.kora_cli_path
    }


@router.post("/sign-transaction")
async def sign_transaction(
    request: SignTransactionRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Sign a transaction using Kora (as paymaster)
    
    Kora will sign the transaction and pay fees in the configured token (USDC, etc.).
    This is the main method for fee abstraction.
    """
    if not ENABLE_KORA:
        raise HTTPException(
            status_code=403,
            detail="Kora SDK is disabled. Set ENABLE_KORA_SDK=true to enable."
        )
    
    try:
        result = await kora_service.sign_transaction(
            transaction_base64=request.transaction_base64,
            options=request.options
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to sign transaction")
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error signing transaction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@router.post("/sign-and-send")
async def sign_and_send_transaction(
    request: SignAndSendRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Sign and send a transaction using Kora
    
    Kora will sign the transaction, pay fees, and send it to the network.
    """
    if not ENABLE_KORA:
        raise HTTPException(
            status_code=403,
            detail="Kora SDK is disabled. Set ENABLE_KORA_SDK=true to enable."
        )
    
    try:
        result = await kora_service.sign_and_send_transaction(
            transaction_base64=request.transaction_base64,
            options=request.options
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to sign and send transaction")
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error signing and sending transaction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@router.post("/estimate-fee")
async def estimate_transaction_fee(
    request: EstimateFeeRequest,
    session: AsyncSession = Depends(get_db)
):
    """Estimate transaction fee cost in specified token"""
    if not ENABLE_KORA:
        raise HTTPException(
            status_code=403,
            detail="Kora SDK is disabled. Set ENABLE_KORA_SDK=true to enable."
        )
    
    try:
        result = await kora_service.estimate_transaction_fee(
            transaction_base64=request.transaction_base64,
            fee_token=request.fee_token
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to estimate fee")
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error estimating fee: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@router.get("/config")
async def get_kora_config():
    """Get Kora server configuration"""
    if not ENABLE_KORA:
        raise HTTPException(
            status_code=403,
            detail="Kora SDK is disabled. Set ENABLE_KORA_SDK=true to enable."
        )
    
    try:
        return await kora_service.get_config()
    except Exception as e:
        logger.error(f"Error getting Kora config: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@router.get("/supported-tokens")
async def get_supported_tokens():
    """Get list of tokens supported for fee payment"""
    if not ENABLE_KORA:
        raise HTTPException(
            status_code=403,
            detail="Kora SDK is disabled. Set ENABLE_KORA_SDK=true to enable."
        )
    
    try:
        result = await kora_service.get_supported_tokens()
        
        if not result.get("success"):
            # Fallback to default tokens if query fails
            return {
                "supported_tokens": ["USDC", "USDT", "SOL"],
                "default_token": "USDC",
                "note": "Using fallback tokens - Kora server query failed"
            }
        
        # Return tokens from Kora server response
        tokens = result.get("result", {}).get("tokens", ["USDC", "USDT", "SOL"])
        return {
            "supported_tokens": tokens,
            "default_token": tokens[0] if tokens else "USDC"
        }
    
    except Exception as e:
        logger.error(f"Error getting supported tokens: {e}")
        # Return fallback on error
        return {
            "supported_tokens": ["USDC", "USDT", "SOL"],
            "default_token": "USDC",
            "error": str(e)
        }

