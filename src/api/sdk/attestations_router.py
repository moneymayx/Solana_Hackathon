"""
Attestations SDK Test Router - Isolated Testing Endpoints

Provides test endpoints for Attestations verifiable credentials functionality.
All endpoints are prefixed with /api/sdk-test/attestations/ to avoid conflicts.

Usage: Set ENABLE_ATTESTATIONS_SDK=true in environment to enable
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import os

from ...database import get_db
from ...services.sdk.attestations_service import attestations_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sdk-test/attestations", tags=["SDK Test - Attestations"])

# Only enable if Attestations SDK is enabled
ENABLE_ATTESTATIONS = os.getenv("ENABLE_ATTESTATIONS_SDK", "false").lower() == "true"


class VerifyKycRequest(BaseModel):
    """Request model for KYC verification"""
    wallet_address: str = Field(..., description="Wallet address to verify")


class VerifyKycResponse(BaseModel):
    """Response model for KYC verification"""
    success: bool
    wallet_address: str
    kyc_verified: bool
    attestation_data: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
    error: Optional[str] = None


class VerifyGeoRequest(BaseModel):
    """Request model for geographic verification"""
    wallet_address: str = Field(..., description="Wallet address to verify")
    allowed_countries: Optional[List[str]] = Field(None, description="List of allowed country codes")


class VerifyAccreditationRequest(BaseModel):
    """Request model for accreditation verification"""
    wallet_address: str = Field(..., description="Wallet address to verify")
    accreditation_type: Optional[str] = Field(default="investor", description="Type of accreditation")


@router.get("/status")
async def get_attestations_status():
    """Check if Attestations SDK is enabled and configured"""
    return {
        "enabled": attestations_service.is_enabled(),
        "rpc_endpoint": attestations_service.rpc_endpoint,
        "program_id": str(attestations_service.program_id)
    }


@router.post("/verify-kyc", response_model=VerifyKycResponse)
async def verify_kyc_attestation(
    request: VerifyKycRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Verify if a wallet has valid KYC attestation
    
    This endpoint tests the Attestations protocol as a replacement for
    expensive KYC providers like MoonPay.
    """
    if not ENABLE_ATTESTATIONS:
        raise HTTPException(
            status_code=403,
            detail="Attestations SDK is disabled. Set ENABLE_ATTESTATIONS_SDK=true to enable."
        )
    
    try:
        result = await attestations_service.verify_kyc_attestation(
            wallet_address=request.wallet_address
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to verify KYC attestation")
            )
        
        return VerifyKycResponse(
            success=True,
            wallet_address=request.wallet_address,
            kyc_verified=result.get("kyc_verified", False),
            attestation_data=result.get("attestation_data"),
            provider=result.get("provider", "attestations")
        )
    
    except Exception as e:
        logger.error(f"Error verifying KYC attestation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@router.post("/verify-geographic")
async def verify_geographic_attestation(
    request: VerifyGeoRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Verify if a wallet has geographic attestation matching allowed countries
    
    Useful for geographic restrictions or compliance requirements.
    """
    if not ENABLE_ATTESTATIONS:
        raise HTTPException(
            status_code=403,
            detail="Attestations SDK is disabled. Set ENABLE_ATTESTATIONS_SDK=true to enable."
        )
    
    try:
        result = await attestations_service.verify_geographic_attestation(
            wallet_address=request.wallet_address,
            allowed_countries=request.allowed_countries
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to verify geographic attestation")
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error verifying geographic attestation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@router.post("/verify-accreditation")
async def verify_accreditation(
    request: VerifyAccreditationRequest,
    session: AsyncSession = Depends(get_db)
):
    """Verify if a wallet has specific accreditation (e.g., accredited investor)"""
    if not ENABLE_ATTESTATIONS:
        raise HTTPException(
            status_code=403,
            detail="Attestations SDK is disabled. Set ENABLE_ATTESTATIONS_SDK=true to enable."
        )
    
    try:
        result = await attestations_service.verify_accreditation(
            wallet_address=request.wallet_address,
            accreditation_type=request.accreditation_type
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to verify accreditation")
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error verifying accreditation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@router.get("/all/{wallet_address}")
async def get_all_attestations(
    wallet_address: str,
    session: AsyncSession = Depends(get_db)
):
    """Get all attestations for a wallet address"""
    if not ENABLE_ATTESTATIONS:
        raise HTTPException(
            status_code=403,
            detail="Attestations SDK is disabled. Set ENABLE_ATTESTATIONS_SDK=true to enable."
        )
    
    try:
        result = await attestations_service.get_all_attestations(wallet_address)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to get attestations")
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting all attestations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )

