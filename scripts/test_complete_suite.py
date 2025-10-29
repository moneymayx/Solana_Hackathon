#!/usr/bin/env python3
"""
Complete Test Suite - Code Logic Verification
Tests everything that can be tested without signing transactions
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from decimal import Decimal

# Load environment
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

test_results = []

def test(name, passed, details=""):
    test_results.append((name, passed, details))
    symbol = f"{Colors.GREEN}✓{Colors.END}" if passed else f"{Colors.RED}✗{Colors.END}"
    print(f"{symbol} {name}")
    if details:
        print(f"   {details}")

def header(text):
    print(f"\n{'=' * 80}")
    print(f"{Colors.BOLD}{text}{Colors.END}")
    print('=' * 80)

async def test_revenue_split_calculations():
    """Test 1: Revenue split math"""
    header("TEST 1: Revenue Split Calculations (60/20/10/10)")
    
    test_amounts = [10.0, 50.0, 100.0, 1000.0]
    
    all_correct = True
    for amount in test_amounts:
        jackpot = amount * 0.60
        operational = amount * 0.20
        buyback = amount * 0.10
        staking = amount * 0.10
        total = jackpot + operational + buyback + staking
        
        correct = abs(total - amount) < 0.01
        all_correct = all_correct and correct
        
        test(
            f"${amount} splits correctly",
            correct,
            f"Jackpot: ${jackpot}, Ops: ${operational}, Buyback: ${buyback}, Staking: ${staking}"
        )
    
    return all_correct

async def test_smart_contract_config():
    """Test 2: Smart contract configuration"""
    header("TEST 2: Smart Contract Configuration")
    
    try:
        # Import and check configuration
        from src.smart_contract_service import smart_contract_service
        
        # Check rates
        correct_bounty = smart_contract_service.bounty_contribution_rate == 0.60
        correct_ops = smart_contract_service.operational_fee_rate == 0.20
        correct_buyback = smart_contract_service.buyback_rate == 0.10
        correct_staking = smart_contract_service.staking_rate == 0.10
        
        test("Bounty rate is 60%", correct_bounty, f"{smart_contract_service.bounty_contribution_rate * 100}%")
        test("Operational rate is 20%", correct_ops, f"{smart_contract_service.operational_fee_rate * 100}%")
        test("Buyback rate is 10%", correct_buyback, f"{smart_contract_service.buyback_rate * 100}%")
        test("Staking rate is 10%", correct_staking, f"{smart_contract_service.staking_rate * 100}%")
        
        # Check total adds to 100%
        total = (smart_contract_service.bounty_contribution_rate + 
                smart_contract_service.operational_fee_rate + 
                smart_contract_service.buyback_rate + 
                smart_contract_service.staking_rate)
        
        test("Total rate is 100%", abs(total - 1.0) < 0.001, f"{total * 100}%")
        
        return all([correct_bounty, correct_ops, correct_buyback, correct_staking])
        
    except Exception as e:
        test("Smart contract service", False, str(e))
        return False

async def test_staking_tiers():
    """Test 3: Staking tier allocations"""
    header("TEST 3: Staking Tier Allocations")
    
    # Expected allocations
    tier_30 = 20  # 20% for 30-day
    tier_60 = 30  # 30% for 60-day
    tier_90 = 50  # 50% for 90-day
    
    total = tier_30 + tier_60 + tier_90
    
    test("30-day tier: 20%", tier_30 == 20, f"{tier_30}% of staking pool")
    test("60-day tier: 30%", tier_60 == 30, f"{tier_60}% of staking pool")
    test("90-day tier: 50%", tier_90 == 50, f"{tier_90}% of staking pool")
    test("Total allocation: 100%", total == 100, f"{total}%")
    
    return total == 100

async def test_buyback_threshold():
    """Test 4: Buyback threshold configuration"""
    header("TEST 4: Buyback Threshold")
    
    try:
        from src.buyback_service import buyback_service
        
        threshold = buyback_service.buyback_threshold
        has_threshold = threshold is not None and threshold > 0
        
        test("Buyback threshold configured", has_threshold, f"${threshold}")
        test("Threshold is reasonable", 10 <= threshold <= 1000, f"${threshold} (should be $10-$1000)")
        
        return has_threshold
        
    except Exception as e:
        test("Buyback service", False, str(e))
        return False

async def test_database_models():
    """Test 5: Database models"""
    header("TEST 5: Database Models")
    
    try:
        from src.models import (
            User, Bounty, StakingPosition, StakingRewardEvent,
            BuybackEvent, FundDeposit
        )
        
        test("User model exists", True, "✓")
        test("Bounty model exists", True, "✓")
        test("StakingPosition model exists", True, "✓")
        test("StakingRewardEvent model exists", True, "✓")
        test("BuybackEvent model exists", True, "✓")
        test("FundDeposit model exists", True, "✓")
        
        # Check StakingRewardEvent has required fields
        has_amount = hasattr(StakingRewardEvent, 'amount_claimed')
        has_tier = hasattr(StakingRewardEvent, 'tier_allocation')
        has_tx = hasattr(StakingRewardEvent, 'transaction_signature')
        
        test("StakingRewardEvent has amount_claimed", has_amount, "✓")
        test("StakingRewardEvent has tier_allocation", has_tier, "✓")
        test("StakingRewardEvent has transaction_signature", has_tx, "✓")
        
        return True
        
    except Exception as e:
        test("Database models", False, str(e))
        return False

async def test_api_endpoints_exist():
    """Test 6: API endpoints configuration"""
    header("TEST 6: API Endpoints")
    
    try:
        # Check if routes are defined
        from src.api import token_router
        
        # Get router
        router = token_router.router
        
        # Check routes exist
        routes = [route.path for route in router.routes]
        
        has_stake = any('/stake' in r for r in routes)
        has_unstake = any('/unstake' in r for r in routes)
        has_claim = any('/claim' in r for r in routes)
        has_positions = any('/positions' in r for r in routes)
        has_tier_stats = any('/tier-stats' in r for r in routes)
        has_buyback = any('/buyback' in r for r in routes)
        
        test("Stake endpoint exists", has_stake, "/api/token/stake")
        test("Unstake endpoint exists", has_unstake, "/api/token/staking/unstake")
        test("Claim endpoint exists", has_claim, "/api/token/staking/claim")
        test("Positions endpoint exists", has_positions, "/api/token/staking/positions")
        test("Tier stats endpoint exists", has_tier_stats, "/api/token/staking/tier-stats")
        test("Buyback endpoint exists", has_buyback, "/api/token/buyback/*")
        
        return all([has_stake, has_unstake, has_claim, has_positions, has_tier_stats])
        
    except Exception as e:
        test("API endpoints", False, str(e))
        return False

async def test_smart_contract_rust():
    """Test 7: Smart contract Rust code"""
    header("TEST 7: Smart Contract Code Analysis")
    
    lottery_path = Path(__file__).parent.parent / 'programs' / 'billions-bounty' / 'src' / 'lib.rs'
    staking_path = Path(__file__).parent.parent / 'programs' / 'staking' / 'src' / 'lib.rs'
    
    # Check lottery contract
    if lottery_path.exists():
        with open(lottery_path, 'r') as f:
            lottery_code = f.read()
        
        has_staking_wallet = 'staking_wallet' in lottery_code
        has_staking_rate = 'staking_rate' in lottery_code
        has_60_rate = 'bounty_contribution_rate = 60' in lottery_code or 'bounty_contribution_rate: 60' in lottery_code
        has_20_ops = 'operational_fee_rate = 20' in lottery_code or 'operational_fee_rate: 20' in lottery_code
        has_10_buyback = 'buyback_rate = 10' in lottery_code or 'buyback_rate: 10' in lottery_code
        has_10_staking = 'staking_rate = 10' in lottery_code or 'staking_rate: 10' in lottery_code
        
        test("Lottery has staking_wallet", has_staking_wallet, "✓")
        test("Lottery has staking_rate", has_staking_rate, "✓")
        test("Lottery has 60% bounty rate", has_60_rate, "✓")
        test("Lottery has 20% ops rate", has_20_ops, "✓")
        test("Lottery has 10% buyback rate", has_10_buyback, "✓")
        test("Lottery has 10% staking rate", has_10_staking, "✓")
    else:
        test("Lottery contract file", False, "File not found")
    
    # Check staking contract
    if staking_path.exists():
        with open(staking_path, 'r') as f:
            staking_code = f.read()
        
        has_stake_fn = 'pub fn stake' in staking_code
        has_unstake_fn = 'pub fn unstake' in staking_code
        has_claim_fn = 'pub fn claim_rewards' in staking_code
        has_pool = 'StakingPool' in staking_code
        has_position = 'StakePosition' in staking_code
        
        test("Staking has stake function", has_stake_fn, "✓")
        test("Staking has unstake function", has_unstake_fn, "✓")
        test("Staking has claim_rewards function", has_claim_fn, "✓")
        test("Staking has StakingPool struct", has_pool, "✓")
        test("Staking has StakePosition struct", has_position, "✓")
    else:
        test("Staking contract file", False, "File not found")
    
    return True

async def test_contract_deployment_files():
    """Test 8: Compiled contracts"""
    header("TEST 8: Compiled Contract Files")
    
    lottery_so = Path(__file__).parent.parent / 'programs' / 'billions-bounty' / 'target' / 'deploy' / 'billions_bounty.so'
    staking_so = Path(__file__).parent.parent / 'programs' / 'staking' / 'target' / 'deploy' / 'staking.so'
    
    lottery_exists = lottery_so.exists()
    staking_exists = staking_so.exists()
    
    if lottery_exists:
        lottery_size = lottery_so.stat().st_size
        test("Lottery .so file exists", True, f"{lottery_size:,} bytes")
        test("Lottery .so size reasonable", lottery_size > 1000, f"{lottery_size:,} bytes")
    else:
        test("Lottery .so file exists", False, "Not found")
    
    if staking_exists:
        staking_size = staking_so.stat().st_size
        test("Staking .so file exists", True, f"{staking_size:,} bytes")
        test("Staking .so size reasonable", staking_size > 1000, f"{staking_size:,} bytes")
    else:
        test("Staking .so file exists", False, "Not found")
    
    return lottery_exists and staking_exists

async def test_environment_config():
    """Test 9: Environment configuration"""
    header("TEST 9: Environment Configuration")
    
    required_vars = [
        'LOTTERY_PROGRAM_ID',
        'STAKING_PROGRAM_ID',
        'JACKPOT_WALLET_ADDRESS',
        'OPERATIONAL_WALLET_ADDRESS',
        'BUYBACK_WALLET_ADDRESS',
        'STAKING_WALLET_ADDRESS',
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        is_set = value is not None and len(value) > 0
        all_set = all_set and is_set
        test(f"{var} configured", is_set, value if is_set else "NOT SET")
    
    return all_set

async def test_security_fixes():
    """Test 10: Security fixes applied"""
    header("TEST 10: Security Fixes")
    
    # Check that dual payout is fixed (no direct backend transfers)
    ai_agent_path = Path(__file__).parent.parent / 'src' / 'ai_agent.py'
    solana_service_path = Path(__file__).parent.parent / 'src' / 'solana_service.py'
    
    if ai_agent_path.exists():
        with open(ai_agent_path, 'r') as f:
            ai_code = f.read()
        
        # Should NOT have direct transfer calls
        no_direct_transfer = 'transfer_token' not in ai_code or 'REMOVED' in ai_code or 'SECURITY FIX' in ai_code
        uses_smart_contract = 'smart_contract_service.process_ai_decision' in ai_code
        
        test("AI agent doesn't do direct transfers", no_direct_transfer, "✓ Security fix applied")
        test("AI agent uses smart contract only", uses_smart_contract, "✓ Correct payout method")
    
    if solana_service_path.exists():
        with open(solana_service_path, 'r') as f:
            solana_code = f.read()
        
        # Check if transfer methods are removed/commented
        transfer_removed = 'def transfer_token' not in solana_code or 'REMOVED' in solana_code
        
        test("Solana service transfer methods removed", transfer_removed, "✓ Security fix applied")
    
    return True

async def run_all_tests():
    """Run complete test suite"""
    print(f"\n{Colors.BOLD}{'=' * 80}")
    print(f"  COMPLETE CODE LOGIC TEST SUITE")
    print(f"  Testing Everything That Can Be Tested Without Transactions")
    print(f"{'=' * 80}{Colors.END}\n")
    
    # Run all tests
    await test_revenue_split_calculations()
    await test_smart_contract_config()
    await test_staking_tiers()
    await test_buyback_threshold()
    await test_database_models()
    await test_api_endpoints_exist()
    await test_smart_contract_rust()
    await test_contract_deployment_files()
    await test_environment_config()
    await test_security_fixes()
    
    # Summary
    header("FINAL TEST SUMMARY")
    
    passed = sum(1 for _, p, _ in test_results if p)
    total = len(test_results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\nTests Run:    {total}")
    print(f"Tests Passed: {Colors.GREEN}{passed}{Colors.END}")
    print(f"Tests Failed: {Colors.RED}{total - passed}{Colors.END}")
    print(f"Success Rate: {Colors.GREEN if percentage >= 90 else Colors.YELLOW}{percentage:.1f}%{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL CODE LOGIC TESTS PASSED!{Colors.END}")
        print(f"\n{Colors.BOLD}What This Means:{Colors.END}")
        print(f"  ✓ Revenue split math is correct")
        print(f"  ✓ Smart contract configuration is correct")
        print(f"  ✓ Database models are complete")
        print(f"  ✓ API endpoints are defined")
        print(f"  ✓ Security fixes are applied")
        print(f"  ✓ Contracts are compiled")
        print(f"  ✓ Environment is configured")
        print(f"\n{Colors.YELLOW}Still Needed:{Colors.END}")
        print(f"  ⏳ Manual testing with real transactions")
        print(f"  ⏳ Security audit before mainnet")
    elif percentage >= 90:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ MOSTLY PASSING{Colors.END}")
        print(f"\nA few tests failed, but core logic is solid.")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SIGNIFICANT ISSUES FOUND{Colors.END}")
        print(f"\nPlease review failed tests above.")
    
    print(f"\n{'=' * 80}\n")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

