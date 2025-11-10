#!/usr/bin/env python3
"""
Example: Kora Fee Abstraction Integration

This example shows how to integrate Kora fee abstraction into your V2 payment flow.
Users can pay transaction fees in USDC instead of requiring SOL.

Prerequisites:
1. Kora server running (kora rpc)
2. ENABLE_KORA_SDK=true in .env
3. KORA_RPC_URL set to Kora server endpoint

Usage:
    python examples/sdk/kora_fee_abstraction_example.py
"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from src.services.sdk.kora_service import KoraService
# V2 moved to smart_contract directory
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from smart_contract.v2_implementation.backend.services.payment_processor import V2PaymentProcessor
from solders.keypair import Keypair
from solders.pubkey import Pubkey
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_kora_fee_abstraction():
    """
    Example: Process V2 payment with Kora fee abstraction
    
    This replaces the standard flow where users must have SOL for fees.
    Instead, Kora pays fees in USDC (or other configured tokens).
    """
    
    # Initialize services
    kora_service = KoraService()
    
    if not kora_service.is_enabled():
        logger.error("❌ Kora service is disabled. Set ENABLE_KORA_SDK=true in .env")
        return
    
    # Check Kora server connection
    logger.info("🔍 Checking Kora server connection...")
    config_result = await kora_service.get_config()
    
    if not config_result.get("success"):
        logger.error(f"❌ Cannot connect to Kora server: {config_result.get('error')}")
        logger.info("💡 Make sure Kora server is running: kora rpc")
        return
    
    logger.info("✅ Kora server connected")
    logger.info(f"   Config: {config_result.get('result')}")
    
    # Get supported fee tokens
    tokens_result = await kora_service.get_supported_tokens()
    if tokens_result.get("success"):
        logger.info(f"✅ Supported fee tokens: {tokens_result.get('result')}")
    
    # Example: Build V2 payment transaction
    # (This is a placeholder - you would build your actual transaction here)
    logger.info("\n📝 Example V2 Payment Flow with Fee Abstraction:")
    logger.info("   1. Build V2 payment transaction (custom instruction)")
    logger.info("   2. Serialize transaction to base64")
    logger.info("   3. Send to Kora for fee abstraction")
    logger.info("   4. Get signed transaction back")
    logger.info("   5. Send to network (fees paid in USDC)")
    
    # Example transaction (placeholder - replace with actual transaction building)
    # transaction = build_v2_payment_transaction(...)
    # transaction_base64 = base64.b64encode(transaction.serialize()).decode('utf-8')
    
    # Example: Estimate fee in USDC
    # fee_estimate = await kora_service.estimate_transaction_fee(
    #     transaction_base64=transaction_base64,
    #     fee_token="USDC"
    # )
    # logger.info(f"💰 Estimated fee in USDC: {fee_estimate.get('result')}")
    
    # Example: Sign transaction with Kora (fee abstraction)
    # sign_result = await kora_service.sign_transaction(
    #     transaction_base64=transaction_base64
    # )
    # if sign_result.get("success"):
    #     signed_transaction_base64 = sign_result.get("result").get("transaction")
    #     logger.info("✅ Transaction signed with fee abstraction")
    #     
    #     # Send transaction
    #     # await send_transaction(signed_transaction_base64)
    
    logger.info("\n💡 Integration Points:")
    logger.info("   - Frontend: paymentProcessor.ts - Replace fee payer with Kora")
    logger.info("   - Backend: payment_processor.py - Add Kora option")
    logger.info("   - User Flow: Show USDC fee option instead of requiring SOL")


async def example_estimate_fees():
    """Example: Estimate transaction fees in different tokens"""
    
    kora_service = KoraService()
    
    if not kora_service.is_enabled():
        return
    
    logger.info("\n💰 Fee Estimation Examples:")
    
    # Example: Estimate in USDC
    # fee_usdc = await kora_service.estimate_transaction_fee(
    #     transaction_base64=transaction_base64,
    #     fee_token="USDC"
    # )
    # logger.info(f"   USDC: {fee_usdc.get('result')}")
    
    # Example: Estimate in SOL (default)
    # fee_sol = await kora_service.estimate_transaction_fee(
    #     transaction_base64=transaction_base64,
    #     fee_token="SOL"
    # )
    # logger.info(f"   SOL: {fee_sol.get('result')}")
    
    logger.info("   (Transaction required for actual estimation)")


if __name__ == "__main__":
    asyncio.run(example_kora_fee_abstraction())
    asyncio.run(example_estimate_fees())

