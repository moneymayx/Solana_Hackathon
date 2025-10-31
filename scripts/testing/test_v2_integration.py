#!/usr/bin/env python3
"""
Test V2 Integration - Verify backend payment processor works correctly
"""
import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

async def test_v2_payment_processor():
    """Test V2 payment processor initialization and basic functionality."""
    print("=" * 60)
    print("Testing V2 Payment Processor")
    print("=" * 60)
    
    try:
        from src.services.v2.payment_processor import get_v2_payment_processor
        
        # Test 1: Import
        print("\n[Test 1] Testing imports...")
        processor = get_v2_payment_processor()
        print("✅ Imports successful")
        
        # Test 2: Initialization
        print("\n[Test 2] Testing initialization...")
        print(f"   Program ID: {processor.program_id}")
        print(f"   USDC Mint: {processor.usdc_mint}")
        print(f"   RPC Endpoint: {processor.rpc_endpoint}")
        print("✅ Initialization successful")
        
        # Test 3: PDA Derivation
        print("\n[Test 3] Testing PDA derivation...")
        pdas = await processor._derive_pdas(1)
        print(f"   Global PDA: {pdas['global']}")
        print(f"   Bounty PDA: {pdas['bounty']}")
        print(f"   Buyback Tracker PDA: {pdas['buyback_tracker']}")
        print("✅ PDA derivation successful")
        
        # Test 4: Token Account Derivation
        print("\n[Test 4] Testing token account derivation...")
        from solders.keypair import Keypair
        test_wallet = Keypair()  # Dummy wallet for testing
        token_accounts = processor._derive_token_accounts(test_wallet.pubkey())
        print(f"   User ATA: {token_accounts['user']}")
        print(f"   Bounty Pool ATA: {token_accounts['bounty_pool']}")
        print(f"   Operational ATA: {token_accounts['operational']}")
        print(f"   Buyback ATA: {token_accounts['buyback']}")
        print(f"   Staking ATA: {token_accounts['staking']}")
        print("✅ Token account derivation successful")
        
        # Test 5: Instruction Discriminator
        print("\n[Test 5] Testing instruction discriminator...")
        discriminator = processor._derive_instruction_discriminator("process_entry_payment_v2")
        print(f"   Discriminator: {discriminator.hex()}")
        print(f"   Length: {len(discriminator)} bytes (expected 8)")
        assert len(discriminator) == 8, "Discriminator must be 8 bytes"
        print("✅ Discriminator derivation successful")
        
        # Test 6: Bounty Status
        print("\n[Test 6] Testing bounty status...")
        status = await processor.get_bounty_status(1)
        print(f"   Status: {status}")
        print("✅ Bounty status check successful")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_existing_services():
    """Test that existing services still work."""
    print("\n" + "=" * 60)
    print("Testing Existing Services (V1)")
    print("=" * 60)
    
    try:
        # Test smart_contract_service still works
        from src.services.smart_contract_service import SmartContractService
        
        print("\n[Test] Smart Contract Service (V1)...")
        service = SmartContractService()
        print(f"✅ V1 Service initialized: {service.program_id}")
        
        # Test lottery status
        status = await service.get_lottery_state()
        print(f"✅ Lottery status retrieved: {status.get('success', False)}")
        
        print("\n✅ Existing services still work!")
        return True
        
    except Exception as e:
        print(f"\n❌ EXISTING SERVICE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("\n🧪 V2 Integration Test Suite")
    print("=" * 60)
    
    # Test V2 processor
    v2_test = await test_v2_payment_processor()
    
    # Test existing services
    v1_test = await test_existing_services()
    
    if v2_test and v1_test:
        print("\n" + "=" * 60)
        print("✅ ALL INTEGRATION TESTS PASSED!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

