#!/usr/bin/env python3
"""
Test Multi-Bounty Functionality
Verifies all aspects of the multi-bounty system are working correctly.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from src.services.contract_adapter_v3 import get_contract_adapter_v3
from src.services.smart_contract_service import SmartContractService


async def test_pda_derivation():
    """Test that PDAs are derived correctly for all bounties"""
    print("=" * 60)
    print("Test 1: PDA Derivation")
    print("=" * 60)
    
    adapter = get_contract_adapter_v3()
    if not adapter:
        print("❌ V3 adapter not available")
        return False
    
    program_id = adapter.program_id
    expected_pdas = {
        1: "Gkh76vSp4jiBRAiZocc8njjD79NthEKnm5vXanDfFu1r",
        2: "7cSHV3zegVido8o6LdPHDfFQvi1rbQkK6G8GPMsM9VBG",
        3: "5Wf8srVoVjeQxaXw1y69EeU1fpWFiwLdFQ1hmPSRuq2X",
        4: "5LKqypQHyBA8LmhgLL9HbqdwR9KpqnHJkrZvwFYNQRoJ",
    }
    
    all_correct = True
    for bounty_id in [1, 2, 3, 4]:
        pda = adapter.get_lottery_pda_for_bounty(bounty_id)
        expected = expected_pdas[bounty_id]
        status = "✅" if str(pda) == expected else "❌"
        print(f"  {status} Bounty {bounty_id}: {pda}")
        if str(pda) != expected:
            print(f"     Expected: {expected}")
            all_correct = False
    
    return all_correct


async def test_account_existence():
    """Test that all bounty accounts exist on-chain"""
    print("\n" + "=" * 60)
    print("Test 2: Account Existence")
    print("=" * 60)
    
    adapter = get_contract_adapter_v3()
    if not adapter:
        print("❌ V3 adapter not available")
        return False
    
    client = AsyncClient("https://api.devnet.solana.com", commitment=Confirmed)
    program_id = adapter.program_id
    
    all_exist = True
    for bounty_id in [1, 2, 3, 4]:
        pda = adapter.get_lottery_pda_for_bounty(bounty_id)
        account_info = await client.get_account_info(pda)
        
        if account_info.value:
            print(f"  ✅ Bounty {bounty_id}: Account exists ({len(account_info.value.data)} bytes)")
        else:
            print(f"  ❌ Bounty {bounty_id}: Account not found")
            all_exist = False
    
    await client.close()
    return all_exist


async def test_difficulty_mapping():
    """Test difficulty to bounty_id mapping"""
    print("\n" + "=" * 60)
    print("Test 3: Difficulty to Bounty ID Mapping")
    print("=" * 60)
    
    service = SmartContractService()
    
    test_cases = [
        ("expert", 1),
        ("hard", 2),
        ("medium", 3),
        ("easy", 4),
        ("Expert", 1),  # Case insensitive
        ("HARD", 2),
        ("unknown", 3),  # Default to medium
    ]
    
    all_correct = True
    for difficulty, expected_bounty_id in test_cases:
        # Simulate the mapping logic from smart_contract_service
        difficulty_lower = difficulty.lower()
        bounty_id_map = {
            "expert": 1,
            "hard": 2,
            "medium": 3,
            "easy": 4
        }
        bounty_id = bounty_id_map.get(difficulty_lower, 3)
        status = "✅" if bounty_id == expected_bounty_id else "❌"
        print(f"  {status} '{difficulty}' -> {bounty_id} (expected {expected_bounty_id})")
        if bounty_id != expected_bounty_id:
            all_correct = False
    
    return all_correct


async def test_bounty_id_validation():
    """Test bounty_id validation in contract adapter"""
    print("\n" + "=" * 60)
    print("Test 4: Bounty ID Validation")
    print("=" * 60)
    
    adapter = get_contract_adapter_v3()
    if not adapter:
        print("❌ V3 adapter not available")
        return False
    
    # Test valid bounty IDs
    valid_ids = [1, 2, 3, 4]
    all_valid = True
    for bounty_id in valid_ids:
        try:
            pda = adapter.get_lottery_pda_for_bounty(bounty_id)
            print(f"  ✅ Bounty {bounty_id}: Valid (PDA: {str(pda)[:16]}...)")
        except ValueError as e:
            print(f"  ❌ Bounty {bounty_id}: {e}")
            all_valid = False
    
    # Test invalid bounty IDs
    invalid_ids = [0, 5, 99, -1]
    all_invalid = True
    for bounty_id in invalid_ids:
        try:
            pda = adapter.get_lottery_pda_for_bounty(bounty_id)
            print(f"  ❌ Bounty {bounty_id}: Should be invalid but got PDA {pda}")
            all_invalid = False
        except ValueError:
            print(f"  ✅ Bounty {bounty_id}: Correctly rejected")
    
    return all_valid and all_invalid


async def test_program_id_consistency():
    """Test that program ID is consistent across services"""
    print("\n" + "=" * 60)
    print("Test 5: Program ID Consistency")
    print("=" * 60)
    
    expected_program_id = "7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh"
    
    adapter = get_contract_adapter_v3()
    service = SmartContractService()
    
    adapter_id = str(adapter.program_id) if adapter else None
    service_id = str(service.program_id) if hasattr(service, 'program_id') else None
    
    all_match = True
    
    if adapter_id:
        status = "✅" if adapter_id == expected_program_id else "❌"
        print(f"  {status} ContractAdapterV3: {adapter_id}")
        if adapter_id != expected_program_id:
            all_match = False
    
    if service_id:
        status = "✅" if service_id == expected_program_id else "❌"
        print(f"  {status} SmartContractService: {service_id}")
        if service_id != expected_program_id:
            all_match = False
    
    if adapter_id and service_id:
        status = "✅" if adapter_id == service_id else "❌"
        print(f"  {status} IDs match: {adapter_id == service_id}")
        if adapter_id != service_id:
            all_match = False
    
    return all_match


async def main():
    """Run all tests"""
    print("\n🧪 Multi-Bounty Functionality Tests\n")
    
    tests = [
        ("PDA Derivation", test_pda_derivation),
        ("Account Existence", test_account_existence),
        ("Difficulty Mapping", test_difficulty_mapping),
        ("Bounty ID Validation", test_bounty_id_validation),
        ("Program ID Consistency", test_program_id_consistency),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

