#!/usr/bin/env python3
"""
Example: Attestations KYC Verification Integration

This example shows how to integrate Attestations KYC verification into your payment flow.
Check wallet attestations before allowing payments.

Prerequisites:
1. SAS program ID found and set in .env
2. ENABLE_ATTESTATIONS_SDK=true in .env
3. ATTESTATIONS_PROGRAM_ID_DEVNET or ATTESTATIONS_PROGRAM_ID_MAINNET set

Usage:
    python examples/sdk/attestations_kyc_example.py
"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from src.services.sdk.attestations_service import AttestationsService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_kyc_verification():
    """
    Example: Verify KYC attestation before allowing payment
    
    This replaces the need for MoonPay or other KYC providers.
    Instead, check on-chain attestations.
    """
    
    # Initialize service
    attestations_service = AttestationsService()
    
    if not attestations_service.is_enabled():
        logger.error("❌ Attestations service is disabled. Set ENABLE_ATTESTATIONS_SDK=true in .env")
        return
    
    # Check if program ID is configured
    program_id_str = str(attestations_service.program_id)
    if program_id_str == "SASProgram111111111111111111111111111111" or \
       program_id_str == "11111111111111111111111111111111":
        logger.error("❌ SAS program ID not configured")
        logger.info("💡 Run: python scripts/sdk/find_attestations_program.py")
        logger.info("   Then set ATTESTATIONS_PROGRAM_ID_DEVNET in .env")
        return
    
    logger.info(f"✅ Attestations service enabled")
    logger.info(f"   SAS Program: {program_id_str}")
    
    # Example: Verify KYC for a wallet
    example_wallet = "11111111111111111111111111111111"  # Replace with actual wallet
    
    logger.info(f"\n🔍 Checking KYC attestation for wallet: {example_wallet}")
    
    result = await attestations_service.verify_kyc_attestation(
        wallet_address=example_wallet
    )
    
    if result.get("success"):
        if result.get("kyc_verified"):
            logger.info("✅ KYC verified via Attestations")
            logger.info(f"   Attestation account: {result.get('attestation_account')}")
            logger.info(f"   Parsed data: {result.get('parsed_data')}")
            
            # Allow payment
            logger.info("   ✅ Payment allowed - KYC verified")
        else:
            logger.info("❌ KYC not verified")
            logger.info(f"   Message: {result.get('message')}")
            
            # Block payment or show KYC required message
            logger.info("   ❌ Payment blocked - KYC required")
    else:
        logger.error(f"❌ Error checking KYC: {result.get('error')}")


async def example_payment_with_kyc_check():
    """
    Example: Payment flow with KYC check
    
    This shows how to integrate KYC verification into your payment endpoint.
    """
    
    attestations_service = AttestationsService()
    
    if not attestations_service.is_enabled():
        logger.warning("⚠️  Attestations disabled - skipping KYC check")
        # Continue with payment (fallback behavior)
        return True
    
    # Example wallet from payment request
    user_wallet = "user_wallet_address_here"
    
    logger.info(f"\n🔐 Payment Flow with KYC Check:")
    logger.info(f"   1. User requests payment: {user_wallet}")
    
    # Step 1: Verify KYC
    logger.info("   2. Checking KYC attestation...")
    kyc_result = await attestations_service.verify_kyc_attestation(user_wallet)
    
    if not kyc_result.get("success"):
        logger.error(f"   ❌ KYC check failed: {kyc_result.get('error')}")
        return False
    
    if not kyc_result.get("kyc_verified"):
        logger.warning(f"   ❌ KYC not verified - payment blocked")
        logger.info("   💡 User needs to complete KYC via Attestations")
        return False
    
    logger.info("   ✅ KYC verified")
    
    # Step 2: Proceed with payment
    logger.info("   3. Processing payment...")
    # Process payment here
    
    logger.info("   ✅ Payment processed")
    return True


async def example_geographic_restriction():
    """
    Example: Check geographic restrictions
    
    Some regions may be restricted. Check geographic attestations.
    """
    
    attestations_service = AttestationsService()
    
    if not attestations_service.is_enabled():
        return
    
    user_wallet = "user_wallet_address_here"
    allowed_countries = ["US", "CA", "GB", "EU"]
    
    logger.info(f"\n🌍 Checking Geographic Restrictions:")
    logger.info(f"   Wallet: {user_wallet}")
    logger.info(f"   Allowed: {allowed_countries}")
    
    result = await attestations_service.verify_geographic_attestation(
        wallet_address=user_wallet,
        allowed_countries=allowed_countries
    )
    
    if result.get("success") and result.get("geographic_verified"):
        logger.info(f"   ✅ Geographic check passed")
        logger.info(f"   Country: {result.get('country')}")
        return True
    else:
        logger.warning(f"   ❌ Geographic restriction - not in allowed countries")
        return False


async def example_get_all_attestations():
    """
    Example: Get all attestations for a wallet
    
    Useful for showing user their verification status.
    """
    
    attestations_service = AttestationsService()
    
    if not attestations_service.is_enabled():
        return
    
    user_wallet = "user_wallet_address_here"
    
    logger.info(f"\n📋 Getting All Attestations:")
    logger.info(f"   Wallet: {user_wallet}")
    
    result = await attestations_service.get_all_attestations(user_wallet)
    
    if result.get("success"):
        attestations = result.get("attestations", [])
        logger.info(f"   Found {len(attestations)} attestations:")
        
        for att in attestations:
            logger.info(f"   - {att.get('type')}: {att.get('status')}")
    else:
        logger.error(f"   Error: {result.get('error')}")


if __name__ == "__main__":
    print("=" * 60)
    print("Attestations KYC Integration Examples")
    print("=" * 60)
    
    asyncio.run(example_kyc_verification())
    asyncio.run(example_payment_with_kyc_check())
    asyncio.run(example_geographic_restriction())
    asyncio.run(example_get_all_attestations())
    
    print("\n" + "=" * 60)
    print("💡 Integration Points:")
    print("   - Backend: Add KYC check before payment processing")
    print("   - Frontend: Show KYC status and requirements")
    print("   - User Flow: Guide users to get attestations if needed")
    print("=" * 60)

