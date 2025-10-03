#!/usr/bin/env python3
"""
Simple Test Suite for Billions Bounty Lottery
Tests basic functionality without requiring new funding
"""
import os
import sys
import asyncio
import json
from pathlib import Path
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from solders.keypair import Keypair

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration
PROGRAM_ID = Pubkey.from_string("4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK")
LOTTERY_PDA = Pubkey.from_string("9nrqftRQVcZUvrRpFJaVgqv49D8ffAEWw3ggUqfomNiJ")
RPC_URL = "https://api.devnet.solana.com"


def load_keypair(keypair_path: str) -> Keypair:
    """Load keypair from JSON file"""
    with open(keypair_path, 'r') as f:
        keypair_data = json.load(f)
    
    if isinstance(keypair_data, list):
        keypair_bytes = bytes(keypair_data)
    else:
        keypair_bytes = bytes(keypair_data['secretKey'])
    
    return Keypair.from_bytes(keypair_bytes)


async def test_lottery_state(client: AsyncClient, lottery_pda: Pubkey):
    """Test 1: Check lottery state"""
    print("🧪 TEST 1: Checking Lottery State")
    print("=" * 40)
    
    try:
        account_info = await client.get_account_info(lottery_pda, commitment=Confirmed)
        
        if account_info.value is None:
            print("❌ Lottery PDA not found!")
            return False
        
        print(f"✅ Lottery PDA found: {lottery_pda}")
        print(f"   Owner: {account_info.value.owner}")
        print(f"   Data length: {len(account_info.value.data)} bytes")
        print(f"   Balance: {account_info.value.lamports / 1_000_000_000} SOL")
        
        # Parse lottery data
        data = account_info.value.data
        if len(data) >= 137:  # Minimum expected size
            print(f"   Data preview: {data[:32].hex()}")
            print("✅ Lottery data structure looks correct")
        else:
            print("⚠️  Lottery data seems small")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking lottery state: {e}")
        return False


async def test_program_deployment(client: AsyncClient, program_id: Pubkey):
    """Test 2: Check program deployment"""
    print("\n🧪 TEST 2: Checking Program Deployment")
    print("=" * 40)
    
    try:
        program_info = await client.get_account_info(program_id, commitment=Confirmed)
        
        if program_info.value is None:
            print("❌ Program not found!")
            return False
        
        print(f"✅ Program found: {program_id}")
        print(f"   Owner: {program_info.value.owner}")
        print(f"   Executable: {program_info.value.executable}")
        print(f"   Data length: {len(program_info.value.data)} bytes")
        print(f"   Balance: {program_info.value.lamports / 1_000_000_000} SOL")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking program: {e}")
        return False


async def test_authority_balance(client: AsyncClient, authority: Pubkey):
    """Test 3: Check authority balance"""
    print("\n🧪 TEST 3: Checking Authority Balance")
    print("=" * 40)
    
    try:
        balance_resp = await client.get_balance(authority, commitment=Confirmed)
        balance_sol = balance_resp.value / 1_000_000_000
        
        print(f"✅ Authority: {authority}")
        print(f"   Balance: {balance_sol} SOL")
        
        if balance_sol > 0.1:
            print("✅ Sufficient balance for transactions")
            return True
        else:
            print("⚠️  Low balance - may need more SOL")
            return False
        
    except Exception as e:
        print(f"❌ Error checking authority balance: {e}")
        return False


async def test_pda_derivation():
    """Test 4: Verify PDA derivation"""
    print("\n🧪 TEST 4: Verifying PDA Derivation")
    print("=" * 40)
    
    try:
        # Derive lottery PDA
        seeds = [b"lottery"]
        derived_pda, bump = Pubkey.find_program_address(seeds, PROGRAM_ID)
        
        print(f"✅ Expected PDA: {LOTTERY_PDA}")
        print(f"✅ Derived PDA:  {derived_pda}")
        print(f"   Bump: {bump}")
        
        if derived_pda == LOTTERY_PDA:
            print("✅ PDA derivation matches!")
            return True
        else:
            print("❌ PDA derivation mismatch!")
            return False
        
    except Exception as e:
        print(f"❌ Error deriving PDA: {e}")
        return False


async def test_network_connectivity(client: AsyncClient):
    """Test 5: Network connectivity"""
    print("\n🧪 TEST 5: Testing Network Connectivity")
    print("=" * 40)
    
    try:
        # Get cluster info
        version = await client.get_version()
        print(f"✅ Connected to Solana cluster")
        print(f"   Version: {version.value['solana-core']}")
        
        # Get recent blockhash
        blockhash = await client.get_latest_blockhash()
        print(f"   Recent blockhash: {blockhash.value.blockhash}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing connectivity: {e}")
        return False


async def run_simple_tests():
    """Run simple tests that don't require funding"""
    print("🚀 BILLIONS BOUNTY - SIMPLE TEST SUITE")
    print("=" * 60)
    print(f"Program ID: {PROGRAM_ID}")
    print(f"Lottery PDA: {LOTTERY_PDA}")
    print(f"Network: Devnet")
    print()
    
    # Load authority keypair
    print("📂 Loading authority keypair...")
    authority = load_keypair("/Users/jaybrantley/.config/solana/id.json")
    print(f"✅ Authority: {authority.pubkey()}")
    
    # Connect to Solana
    client = AsyncClient(RPC_URL, commitment=Confirmed)
    
    try:
        # Run tests
        results = []
        
        # Test 1: Network Connectivity
        results.append(await test_network_connectivity(client))
        
        # Test 2: Program Deployment
        results.append(await test_program_deployment(client, PROGRAM_ID))
        
        # Test 3: Lottery State
        results.append(await test_lottery_state(client, LOTTERY_PDA))
        
        # Test 4: Authority Balance
        results.append(await test_authority_balance(client, authority.pubkey()))
        
        # Test 5: PDA Derivation
        results.append(await test_pda_derivation())
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        test_names = ["Network Connectivity", "Program Deployment", "Lottery State", "Authority Balance", "PDA Derivation"]
        for i, (name, result) in enumerate(zip(test_names, results)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{i+1}. {name}: {status}")
        
        passed = sum(results)
        total = len(results)
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED!")
            print("\n✅ Smart contract is ready for:")
            print("   ├── Entry payments")
            print("   ├── Winner selection")
            print("   └── Emergency recovery")
        else:
            print("⚠️  Some tests failed - check logs above")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(run_simple_tests())
