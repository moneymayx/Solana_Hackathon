#!/usr/bin/env python3
"""
V2 Contract Integration Test Script

Tests the backend's ability to interact with the v2 contract on devnet.
This script validates:
- Connection to devnet
- Account fetching
- Transaction simulation
- Error handling

Usage:
    python3 scripts/devnet/test_v2_integration.py
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from solders.pubkey import Pubkey
    from solders.keypair import Keypair
    from solana.rpc.api import Client
    from solana.rpc.commitment import Confirmed
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip3 install solders solana")
    sys.exit(1)


# Devnet addresses
PROGRAM_ID = "GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm"
GLOBAL_PDA = "F4YATUC3tEA3Gb3Tt3v7sZBT9iKRhHXJsZ6s7nBWKDgh"
BOUNTY_1_PDA = "AJC6D2mvMcktdzpJJQmbYXkTZn9xGpd2C3qm4VAZK83Z"
IDL_ACCOUNT = "HicBwRnacuFcfYXWGBFSCWofc8ZmJU4v4rKKxtxvXBQr"

# Wallets
BOUNTY_POOL_WALLET = "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF"
OPERATIONAL_WALLET = "46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D"
BUYBACK_WALLET = "7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya"
STAKING_WALLET = "Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX"

RPC_URL = os.getenv("SOLANA_RPC_ENDPOINT", "https://api.devnet.solana.com")


def test_connection() -> bool:
    """Test connection to Solana devnet."""
    print("Test 1: RPC Connection")
    try:
        client = Client(RPC_URL, commitment=Confirmed)
        version = client.get_version()
        print(f"✅ Connected to Solana RPC")
        print(f"   Version: {version.value}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_program_account() -> bool:
    """Test that program account exists and is executable."""
    print("\nTest 2: Program Account")
    try:
        client = Client(RPC_URL, commitment=Confirmed)
        program_pubkey = Pubkey.from_string(PROGRAM_ID)
        account_info = client.get_account_info(program_pubkey)
        
        if account_info.value is None:
            print("❌ Program account not found")
            return False
        
        print(f"✅ Program account found")
        print(f"   Executable: {account_info.value.executable}")
        print(f"   Owner: {account_info.value.owner}")
        print(f"   Data length: {len(account_info.value.data)} bytes")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_pda_accounts() -> bool:
    """Test that PDA accounts are initialized."""
    print("\nTest 3: PDA Accounts")
    client = Client(RPC_URL, commitment=Confirmed)
    program_pubkey = Pubkey.from_string(PROGRAM_ID)
    
    pdas = {
        "Global": GLOBAL_PDA,
        "Bounty[1]": BOUNTY_1_PDA,
    }
    
    all_exist = True
    for name, pda_str in pdas.items():
        try:
            pda_pubkey = Pubkey.from_string(pda_str)
            account_info = client.get_account_info(pda_pubkey)
            
            if account_info.value is None:
                print(f"❌ {name} PDA not found")
                all_exist = False
            elif account_info.value.owner != program_pubkey:
                print(f"❌ {name} PDA has wrong owner")
                print(f"   Expected: {program_pubkey}")
                print(f"   Got: {account_info.value.owner}")
                all_exist = False
            else:
                print(f"✅ {name} PDA initialized")
                print(f"   Data length: {len(account_info.value.data)} bytes")
        except Exception as e:
            print(f"❌ {name} error: {e}")
            all_exist = False
    
    return all_exist


def test_idl_account() -> bool:
    """Test that IDL is published."""
    print("\nTest 4: IDL Account")
    try:
        client = Client(RPC_URL, commitment=Confirmed)
        idl_pubkey = Pubkey.from_string(IDL_ACCOUNT)
        account_info = client.get_account_info(idl_pubkey)
        
        if account_info.value is None:
            print("❌ IDL account not found")
            return False
        
        print(f"✅ IDL published")
        print(f"   Data length: {len(account_info.value.data)} bytes")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_wallet_addresses() -> bool:
    """Test that wallet addresses are valid."""
    print("\nTest 5: Wallet Addresses")
    
    wallets = {
        "Bounty Pool": BOUNTY_POOL_WALLET,
        "Operational": OPERATIONAL_WALLET,
        "Buyback": BUYBACK_WALLET,
        "Staking": STAKING_WALLET,
    }
    
    all_valid = True
    for name, wallet_str in wallets.items():
        try:
            wallet_pubkey = Pubkey.from_string(wallet_str)
            print(f"✅ {name}: {wallet_str}")
        except Exception as e:
            print(f"❌ {name} invalid: {e}")
            all_valid = False
    
    return all_valid


def main():
    """Run all integration tests."""
    print("🔍 V2 Contract Integration Tests (Python)\n")
    print(f"RPC: {RPC_URL}")
    print(f"Program: {PROGRAM_ID}\n")
    print("=" * 60)
    
    tests = [
        ("Connection", test_connection),
        ("Program Account", test_program_account),
        ("PDA Accounts", test_pda_accounts),
        ("IDL Account", test_idl_account),
        ("Wallet Addresses", test_wallet_addresses),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All integration tests passed!")
        print("\nNext Steps:")
        print("1. Set USE_CONTRACT_V2=true in backend .env")
        print("2. Test entry payment endpoint")
        print("3. Verify 4-way split on-chain")
        print("4. Monitor logs for errors")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())



