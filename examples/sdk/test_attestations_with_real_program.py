#!/usr/bin/env python3
"""
Test Attestations Service with Real Program ID

This script tests the Attestations service with the actual SAS program ID
to verify it can query attestation accounts on-chain.
"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from src.services.sdk.attestations_service import AttestationsService
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_pda_derivation():
    """Test PDA derivation with real program ID"""
    print("\n🔍 Test 1: PDA Derivation")
    print("-" * 60)
    
    service = AttestationsService()
    
    if not service.is_enabled():
        print("❌ Attestations service is disabled")
        return False
    
    # Test with a known wallet
    test_wallet = Pubkey.from_string("11111111111111111111111111111111")
    
    # Derive PDA
    pda = service._derive_attestation_pda(test_wallet)
    
    print(f"✅ PDA Derived Successfully")
    print(f"   Wallet: {test_wallet}")
    print(f"   PDA: {pda}")
    print(f"   Program ID: {service.program_id}")
    
    return True


async def test_query_account():
    """Test querying an attestation account"""
    print("\n🔍 Test 2: Query Attestation Account")
    print("-" * 60)
    
    service = AttestationsService()
    client = AsyncClient('https://api.devnet.solana.com')
    
    # Derive PDA for a test wallet
    test_wallet = Pubkey.from_string("11111111111111111111111111111111")
    pda = service._derive_attestation_pda(test_wallet)
    
    print(f"Querying PDA: {pda}")
    
    # Query the account
    account_data = await service._query_attestation_account(pda)
    
    if account_data:
        print(f"✅ Account found!")
        print(f"   Owner: {account_data.get('owner')}")
        print(f"   Lamports: {account_data.get('lamports')}")
        print(f"   Has data: {bool(account_data.get('data'))}")
        
        if account_data.get('data'):
            # Parse the data
            parsed = service._parse_attestation_account_data(account_data.get('data'))
            print(f"   Parsed data: {parsed}")
    else:
        print(f"ℹ️  Account not found (no attestation for this wallet)")
        print(f"   This is expected for a placeholder wallet")
    
    await client.close()
    return account_data is not None


async def test_kyc_verification():
    """Test KYC verification endpoint"""
    print("\n🔍 Test 3: KYC Verification")
    print("-" * 60)
    
    service = AttestationsService()
    
    # Test with placeholder wallet (unlikely to have attestation)
    test_wallet = "11111111111111111111111111111111"
    
    result = await service.verify_kyc_attestation(test_wallet)
    
    if result.get("success"):
        if result.get("kyc_verified"):
            print(f"✅ KYC Verified!")
            print(f"   Wallet: {test_wallet}")
            print(f"   Attestation account: {result.get('attestation_account')}")
        else:
            print(f"ℹ️  No KYC attestation (expected)")
            print(f"   Message: {result.get('message')}")
            print(f"   PDA: {result.get('attestation_account')}")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    return result.get("success", False)


async def test_program_accounts():
    """Try to find accounts owned by SAS program"""
    print("\n🔍 Test 4: Finding SAS Program Accounts")
    print("-" * 60)
    
    service = AttestationsService()
    client = AsyncClient('https://api.devnet.solana.com')
    
    program_id = service.program_id
    
    print(f"Program ID: {program_id}")
    print(f"Attempting to query program accounts...")
    
    try:
        # Get program accounts (may be slow/large)
        # Get a few accounts to verify program has attestations
        response = await client.get_program_accounts(
            program_id,
            encoding="base64"
        )
        
        accounts = response.value
        print(f"✅ Found {len(accounts)} accounts owned by SAS program")
        
        for i, account in enumerate(accounts[:3], 1):
            pubkey = account.account.owner
            print(f"   Account {i}: {pubkey}")
        
        if len(accounts) > 0:
            print(f"\n💡 These are attestation accounts!")
            print(f"   You can query one to see the structure")
    except Exception as e:
        print(f"⚠️  Could not query program accounts: {e}")
        print(f"   This is normal - program may have many accounts")
    
    await client.close()


async def main():
    print("=" * 60)
    print("Attestations Service - Real Program ID Test")
    print("=" * 60)
    
    # Test 1: PDA Derivation
    test1 = await test_pda_derivation()
    
    # Test 2: Query Account
    test2 = await test_query_account()
    
    # Test 3: KYC Verification
    test3 = await test_kyc_verification()
    
    # Test 4: Program Accounts
    await test_program_accounts()
    
    print("\n" + "=" * 60)
    print("✅ Tests Complete!")
    print("\n💡 Next Steps:")
    print("   1. Find a wallet with a real attestation")
    print("   2. Query its attestation account")
    print("   3. Parse the account data structure")
    print("   4. Update _parse_attestation_account_data with correct structure")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

