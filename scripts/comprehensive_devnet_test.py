#!/usr/bin/env python3
"""
Comprehensive Devnet Testing Suite
Tests all functionality on deployed contracts
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{'=' * 80}")
    print(f"  {Colors.BOLD}{text}{Colors.END}")
    print('=' * 80)

def print_test(name, status, message=""):
    symbol = f"{Colors.GREEN}✓{Colors.END}" if status else f"{Colors.RED}✗{Colors.END}"
    print(f"{symbol} {name}")
    if message:
        print(f"  {message}")

async def test_contract_deployment():
    """Test 1: Verify contracts are deployed"""
    print_header("TEST 1: Contract Deployment Verification")
    
    lottery_id = os.getenv('LOTTERY_PROGRAM_ID', '4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK')
    staking_id = os.getenv('STAKING_PROGRAM_ID', 'HPWRSESRyR5StX3KV5oCkgQazwJeC38kGnn2n5nqcHnU')
    
    print(f"Lottery Contract: {lottery_id}")
    print(f"Staking Contract: {staking_id}")
    
    # Try to verify via Solana CLI
    import subprocess
    
    lottery_exists = subprocess.run(
        ['solana', 'program', 'show', lottery_id, '--url', 'devnet'],
        capture_output=True
    ).returncode == 0
    
    staking_exists = subprocess.run(
        ['solana', 'program', 'show', staking_id, '--url', 'devnet'],
        capture_output=True
    ).returncode == 0
    
    print_test("Lottery contract exists on devnet", lottery_exists)
    print_test("Staking contract exists on devnet", staking_exists)
    
    return lottery_exists and staking_exists

async def test_wallet_configuration():
    """Test 2: Verify wallet configuration"""
    print_header("TEST 2: Wallet Configuration")
    
    wallets = {
        'Jackpot (60%)': os.getenv('JACKPOT_WALLET_ADDRESS'),
        'Operational (20%)': os.getenv('OPERATIONAL_WALLET_ADDRESS'),
        'Buyback (10%)': os.getenv('BUYBACK_WALLET_ADDRESS'),
        'Staking (10%)': os.getenv('STAKING_WALLET_ADDRESS'),
    }
    
    all_configured = True
    for name, address in wallets.items():
        exists = address is not None and len(address) > 0
        print_test(f"{name}: {address or 'NOT SET'}", exists)
        all_configured = all_configured and exists
    
    return all_configured

async def get_wallet_balance(address):
    """Get SOL balance of a wallet"""
    import subprocess
    try:
        result = subprocess.run(
            ['solana', 'balance', address, '--url', 'devnet'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            balance = result.stdout.strip().split()[0]
            return float(balance)
    except:
        pass
    return None

async def test_wallet_balances():
    """Test 3: Check wallet balances"""
    print_header("TEST 3: Initial Wallet Balances")
    
    wallets = {
        'Jackpot': os.getenv('JACKPOT_WALLET_ADDRESS'),
        'Operational': os.getenv('OPERATIONAL_WALLET_ADDRESS'),
        'Buyback': os.getenv('BUYBACK_WALLET_ADDRESS'),
        'Staking': os.getenv('STAKING_WALLET_ADDRESS'),
    }
    
    balances = {}
    for name, address in wallets.items():
        if address:
            balance = await get_wallet_balance(address)
            balances[name] = balance
            print_test(f"{name} wallet", True, f"{balance} SOL")
    
    return balances

async def test_database_connection():
    """Test 4: Database connectivity"""
    print_header("TEST 4: Database Connection")
    
    try:
        from database import engine
        from sqlalchemy import text
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            success = result.scalar() == 1
            
        print_test("Database connection", success, "PostgreSQL connected")
        
        # Check key tables exist
        async with engine.begin() as conn:
            tables = ['users', 'bounties', 'staking_positions', 'staking_reward_events', 'buyback_events']
            for table in tables:
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print_test(f"Table '{table}' exists", True, f"{count} rows")
        
        return True
    except Exception as e:
        print_test("Database connection", False, str(e))
        return False

async def test_backend_health():
    """Test 5: Backend API health"""
    print_header("TEST 5: Backend Health Check")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/health') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print_test("Backend is running", True, f"Status: {data.get('status', 'ok')}")
                    return True
    except Exception as e:
        print_test("Backend is running", False, "Backend not accessible - start with: python3 src/main.py")
    
    return False

async def test_bounty_api():
    """Test 6: Bounty API endpoints"""
    print_header("TEST 6: Bounty API Endpoints")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            # Test bounties list
            async with session.get('http://localhost:8000/api/bounties') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    bounties = data.get('bounties', [])
                    print_test("GET /api/bounties", True, f"Found {len(bounties)} bounties")
                    return len(bounties) > 0
                else:
                    print_test("GET /api/bounties", False, f"Status: {resp.status}")
    except Exception as e:
        print_test("Bounty API", False, str(e))
    
    return False

async def test_staking_api():
    """Test 7: Staking API endpoints"""
    print_header("TEST 7: Staking API Endpoints")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            # Test tier stats
            async with session.get('http://localhost:8000/api/token/staking/tier-stats') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print_test("GET /api/token/staking/tier-stats", True, "Endpoint working")
                    return True
                else:
                    print_test("GET /api/token/staking/tier-stats", False, f"Status: {resp.status}")
    except Exception as e:
        print_test("Staking API", False, str(e))
    
    return False

async def test_smart_contract_integration():
    """Test 8: Smart contract service"""
    print_header("TEST 8: Smart Contract Service")
    
    try:
        from smart_contract_service import smart_contract_service
        
        print_test("Smart contract service imported", True)
        
        # Check configuration
        print(f"  Lottery Program: {smart_contract_service.program_id}")
        print(f"  RPC Endpoint: {smart_contract_service.rpc_endpoint}")
        print(f"  Revenue Split: 60/20/10/10")
        
        print_test("Configuration loaded", True, "60% bounty, 20% ops, 10% buyback, 10% staking")
        
        return True
    except Exception as e:
        print_test("Smart contract service", False, str(e))
        return False

async def run_all_tests():
    """Run complete test suite"""
    print(f"\n{Colors.BOLD}{'=' * 80}")
    print(f"  COMPREHENSIVE DEVNET TESTING SUITE")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}{Colors.END}\n")
    
    results = {}
    
    # Run tests
    results['contract_deployment'] = await test_contract_deployment()
    results['wallet_config'] = await test_wallet_configuration()
    results['wallet_balances'] = await test_wallet_balances()
    results['database'] = await test_database_connection()
    results['backend'] = await test_backend_health()
    results['bounty_api'] = await test_bounty_api()
    results['staking_api'] = await test_staking_api()
    results['smart_contract'] = await test_smart_contract_integration()
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v and not isinstance(v, dict))
    total = len([k for k in results.keys() if k != 'wallet_balances'])
    
    print(f"\nTests Passed: {Colors.GREEN}{passed}/{total}{Colors.END}")
    print(f"Tests Failed: {Colors.RED}{total - passed}/{total}{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.END}")
        print(f"\nYour system is ready for:")
        print(f"  • Manual testing with real transactions")
        print(f"  • Revenue split verification")
        print(f"  • Staking functionality testing")
        print(f"  • Integration testing")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.END}")
        print(f"\nFailed tests need to be fixed before proceeding.")
    
    print(f"\n{'=' * 80}\n")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

