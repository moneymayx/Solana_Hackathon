#!/usr/bin/env python3
"""
Kora POC: Real Transaction Test

This POC demonstrates fee abstraction with a real transaction.
It builds a simple transfer transaction and uses Kora to pay fees.

Prerequisites:
- Kora configured and wallet funded
- ENABLE_KORA_SDK=true in .env
- KORA_PRIVATE_KEY set in .env
"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from src.services.sdk.kora_service import KoraService
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.transaction import Transaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
import base64
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_test_transaction():
    """Create a simple test transfer transaction"""
    client = AsyncClient('https://api.devnet.solana.com')
    
    # Use a test wallet (or generate new one)
    sender = Keypair()
    receiver = Pubkey.from_string("11111111111111111111111111111111")  # System program as dummy receiver
    
    # Get recent blockhash
    blockhash_resp = await client.get_latest_blockhash()
    blockhash = blockhash_resp.value.blockhash
    
    # Create transfer instruction (small amount for testing)
    transfer_ix = transfer(
        TransferParams(
            from_pubkey=sender.pubkey(),
            to_pubkey=receiver,
            lamports=1000  # Very small amount
        )
    )
    
    # Build transaction
    transaction = Transaction.new_with_payer([transfer_ix], sender.pubkey())
    transaction.recent_blockhash = blockhash
    
    # Serialize and encode
    transaction_bytes = bytes(transaction)
    transaction_base64 = base64.b64encode(transaction_bytes).decode('utf-8')
    
    await client.close()
    return transaction_base64, sender


async def test_kora_fee_abstraction():
    """Test Kora fee abstraction with real transaction"""
    
    kora_service = KoraService()
    
    if not kora_service.is_enabled():
        logger.error("❌ Kora service is disabled. Set ENABLE_KORA_SDK=true in .env")
        return
    
    logger.info("🧪 Kora Fee Abstraction POC")
    logger.info("=" * 60)
    
    # Step 1: Create test transaction
    logger.info("\n📝 Step 1: Creating test transaction...")
    try:
        transaction_base64, sender = await create_test_transaction()
        logger.info(f"✅ Transaction created")
        logger.info(f"   Sender: {sender.pubkey()}")
        logger.info(f"   Transaction length: {len(transaction_base64)} chars")
    except Exception as e:
        logger.error(f"❌ Failed to create transaction: {e}")
        return
    
    # Step 2: Estimate fee
    logger.info("\n💰 Step 2: Estimating transaction fee...")
    fee_result = await kora_service.estimate_transaction_fee(
        transaction_base64=transaction_base64
    )
    
    if fee_result.get("success"):
        logger.info("✅ Fee estimated successfully")
        logger.info(f"   Result: {fee_result.get('result')}")
    else:
        logger.warning(f"⚠️  Fee estimation failed: {fee_result.get('error')}")
        logger.info("   Continuing anyway...")
    
    # Step 3: Sign transaction with Kora (fee abstraction)
    logger.info("\n✍️  Step 3: Signing transaction with Kora (fee abstraction)...")
    sign_result = await kora_service.sign_transaction(
        transaction_base64=transaction_base64
    )
    
    if sign_result.get("success"):
        logger.info("✅ Transaction signed with fee abstraction!")
        logger.info(f"   Result: {sign_result.get('result')}")
        logger.info("\n💡 This transaction's fees will be paid by Kora wallet")
        logger.info("   User doesn't need SOL for fees!")
    else:
        logger.error(f"❌ Failed to sign transaction: {sign_result.get('error')}")
        logger.info("\n🔍 Troubleshooting:")
        logger.info("   1. Check KORA_PRIVATE_KEY is set correctly")
        logger.info("   2. Verify wallet is funded with SOL")
        logger.info("   3. Check Kora CLI is installed and accessible")
        return
    
    # Step 4: Optionally sign and send
    logger.info("\n📤 Step 4: Testing sign-and-send...")
    logger.info("   (Skipping actual send to avoid using funds in POC)")
    logger.info("   To send: await kora_service.sign_and_send_transaction(...)")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ POC Complete!")
    logger.info("\n💡 Next Steps:")
    logger.info("   1. Integrate into payment flow")
    logger.info("   2. Test with V2 payment transactions")
    logger.info("   3. Monitor wallet balance")


if __name__ == "__main__":
    asyncio.run(test_kora_fee_abstraction())

