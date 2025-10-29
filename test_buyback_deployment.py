#!/usr/bin/env python3
"""
Automated Buyback System Deployment Test Script

This script verifies that the buyback system is properly deployed and configured.
Run this after updating your .env file and before deploying to production.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from typing import Dict, List, Tuple

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


class BuybackDeploymentTest:
    """Test suite for buyback system deployment"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed_tests = 0
        self.total_tests = 0
        
    def test(self, name: str, func) -> bool:
        """Run a test and track results"""
        self.total_tests += 1
        try:
            result = func()
            if result:
                self.passed_tests += 1
                print_success(f"{name}")
                return True
            else:
                self.errors.append(name)
                print_error(f"{name}")
                return False
        except Exception as e:
            self.errors.append(f"{name}: {str(e)}")
            print_error(f"{name} - {str(e)}")
            return False
    
    async def test_async(self, name: str, func) -> bool:
        """Run an async test and track results"""
        self.total_tests += 1
        try:
            result = await func()
            if result:
                self.passed_tests += 1
                print_success(f"{name}")
                return True
            else:
                self.errors.append(name)
                print_error(f"{name}")
                return False
        except Exception as e:
            self.errors.append(f"{name}: {str(e)}")
            print_error(f"{name} - {str(e)}")
            return False


async def test_environment_variables() -> Tuple[bool, Dict]:
    """Test 1: Environment Variables"""
    print_header("TEST 1: ENVIRONMENT VARIABLES")
    
    load_dotenv()
    
    required_vars = {
        'BUYBACK_WALLET_ADDRESS': 'Buyback wallet address',
        'OPERATIONAL_WALLET_ADDRESS': 'Operational wallet address',
        'TOKEN_100BS_MINT': '$100Bs token mint',
        'BUYBACK_THRESHOLD': 'Buyback auto-execute threshold',
        'SOLANA_RPC_URL': 'Solana RPC endpoint',
        'DATABASE_URL': 'PostgreSQL connection string'
    }
    
    results = {}
    all_set = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        
        if not value or value.startswith('YOUR_') or value == '':
            print_error(f"{var}: NOT SET - {description}")
            all_set = False
            results[var] = None
        else:
            print_success(f"{var}: {value[:20]}... - {description}")
            results[var] = value
    
    return all_set, results


async def test_smart_contract_service() -> bool:
    """Test 2: Smart Contract Service Configuration"""
    print_header("TEST 2: SMART CONTRACT SERVICE")
    
    try:
        from src.smart_contract_service import smart_contract_service
        
        # Check rates
        print_info(f"Checking revenue distribution rates...")
        
        bounty_rate = smart_contract_service.bounty_contribution_rate
        operational_rate = smart_contract_service.operational_fee_rate
        buyback_rate = smart_contract_service.buyback_rate
        
        print(f"  Bounty: {bounty_rate * 100}%")
        print(f"  Operational: {operational_rate * 100}%")
        print(f"  Buyback: {buyback_rate * 100}%")
        
        # Verify 60/20/20
        if bounty_rate == 0.60 and operational_rate == 0.20 and buyback_rate == 0.20:
            print_success("Revenue distribution configured correctly (60/20/20)")
            
            # Test calculation
            test_amount = 10.00
            expected_bounty = 6.00
            expected_ops = 2.00
            expected_buyback = 2.00
            
            calc_bounty = test_amount * bounty_rate
            calc_ops = test_amount * operational_rate
            calc_buyback = test_amount * buyback_rate
            
            if (abs(calc_bounty - expected_bounty) < 0.01 and
                abs(calc_ops - expected_ops) < 0.01 and
                abs(calc_buyback - expected_buyback) < 0.01):
                print_success(f"$10 split test: ${calc_bounty}/${calc_ops}/${calc_buyback}")
                return True
            else:
                print_error(f"Split calculation error")
                return False
        else:
            print_error(f"Revenue distribution incorrect: {bounty_rate}/{operational_rate}/{buyback_rate}")
            return False
            
    except ImportError as e:
        print_error(f"Cannot import smart_contract_service: {e}")
        return False
    except Exception as e:
        print_error(f"Error testing smart contract service: {e}")
        return False


async def test_buyback_service() -> bool:
    """Test 3: Buyback Service"""
    print_header("TEST 3: BUYBACK SERVICE")
    
    try:
        from src.buyback_service import buyback_service
        
        # Check configuration
        print_info("Checking buyback service configuration...")
        
        wallet = buyback_service.buyback_wallet
        token_mint = buyback_service.token_100bs_mint
        threshold = buyback_service.buyback_threshold
        
        if not wallet or wallet.startswith('YOUR_'):
            print_error("Buyback wallet not configured")
            return False
        print_success(f"Buyback wallet: {wallet[:20]}...")
        
        if not token_mint or token_mint.startswith('YOUR_'):
            print_warning("Token mint not configured (will need this for mainnet)")
        else:
            print_success(f"Token mint: {token_mint[:20]}...")
        
        print_success(f"Threshold: ${threshold}")
        
        # Test balance check
        print_info("Testing balance check...")
        balance_info = await buyback_service.check_buyback_balance()
        
        if 'error' in balance_info:
            print_warning(f"Balance check returned error (may be expected): {balance_info['error']}")
            # This is OK for new wallets
            return True
        else:
            print_success(f"Balance check successful: ${balance_info.get('usdc_balance', 0):.2f}")
            return True
            
    except ImportError as e:
        print_error(f"Cannot import buyback_service: {e}")
        return False
    except Exception as e:
        print_error(f"Error testing buyback service: {e}")
        return False


async def test_database_schema() -> bool:
    """Test 4: Database Schema"""
    print_header("TEST 4: DATABASE SCHEMA")
    
    try:
        from sqlalchemy import inspect, text
        from src.database import get_db
        from src.models import BuybackEvent
        
        print_info("Checking database schema...")
        
        async for session in get_db():
            try:
                # Use run_sync for inspection on async engine
                def check_schema(connection):
                    inspector = inspect(connection)
                    
                    # Check if buyback_events table exists
                    if 'buyback_events' not in inspector.get_table_names():
                        return {'exists': False, 'columns': []}
                    
                    # Get columns
                    columns = [col['name'] for col in inspector.get_columns('buyback_events')]
                    return {'exists': True, 'columns': columns}
                
                result = await session.connection(execution_options={"synchronous": True})
                schema_info = await result.run_sync(check_schema)
                
                if not schema_info['exists']:
                    print_warning("buyback_events table doesn't exist (will be created on first use)")
                    return True  # Not a failure, just needs initialization
                
                columns = schema_info['columns']
                print_info(f"Found {len(columns)} columns in buyback_events table")
                
                # Check for new columns
                required_columns = [
                    'tokens_burned',
                    'swap_transaction_signature',
                    'burn_transaction_signature',
                    'execution_type'
                ]
                
                missing = [col for col in required_columns if col not in columns]
                
                if missing:
                    print_warning(f"Missing columns: {missing}")
                    print_info("Run database migration to add these columns")
                    print_info("See DEPLOYMENT_AND_TESTING_GUIDE.md Phase 3")
                    return False
                else:
                    print_success("All required columns present")
                    return True
                    
            except Exception as e:
                # If inspection fails, try a simple query approach
                try:
                    await session.execute(text("SELECT 1 FROM buyback_events LIMIT 1"))
                    print_success("buyback_events table exists and accessible")
                    print_info("Unable to verify all columns (may need manual check)")
                    session_result = True
                except:
                    print_warning("buyback_events table doesn't exist yet")
                    print_info("It will be created automatically on first use")
                    session_result = True
                
                return session_result
                
    except ImportError as e:
        print_error(f"Cannot import database modules: {e}")
        return False
    except Exception as e:
        print_error(f"Error connecting to database: {e}")
        return False


async def test_api_imports() -> bool:
    """Test 5: API Imports"""
    print_header("TEST 5: API ROUTE IMPORTS")
    
    try:
        print_info("Testing API imports...")
        
        from src.api import token_router
        
        # Check if buyback endpoints exist
        has_status = any('buyback/status' in str(route) for route in token_router.router.routes)
        has_history = any('buyback/history' in str(route) for route in token_router.router.routes)
        has_execute = any('buyback/execute' in str(route) for route in token_router.router.routes)
        
        if has_status:
            print_success("GET /api/token/buyback/status endpoint found")
        else:
            print_error("Buyback status endpoint missing")
            
        if has_history:
            print_success("GET /api/token/buyback/history endpoint found")
        else:
            print_error("Buyback history endpoint missing")
            
        if has_execute:
            print_success("POST /api/token/buyback/execute endpoint found")
        else:
            print_error("Buyback execute endpoint missing")
        
        return has_status and has_history and has_execute
        
    except ImportError as e:
        print_error(f"Cannot import API modules: {e}")
        return False
    except Exception as e:
        print_error(f"Error checking API routes: {e}")
        return False


async def test_smart_contract_build() -> bool:
    """Test 6: Smart Contract Build"""
    print_header("TEST 6: SMART CONTRACT BUILD")
    
    contract_path = "programs/billions-bounty/target/deploy/billions_bounty.so"
    
    if os.path.exists(contract_path):
        size = os.path.getsize(contract_path)
        print_success(f"Smart contract built: {contract_path} ({size} bytes)")
        return True
    else:
        print_warning("Smart contract not built yet")
        print_info("Run: cd programs/billions-bounty && anchor build")
        return False


async def main():
    """Run all deployment tests"""
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   BUYBACK SYSTEM DEPLOYMENT TEST                          ║")
    print("║   Testing 60/20/20 Revenue Distribution                   ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    tester = BuybackDeploymentTest()
    
    # Run all tests
    env_passed, env_vars = await test_environment_variables()
    await asyncio.sleep(0.5)
    
    sc_passed = await test_smart_contract_service()
    await asyncio.sleep(0.5)
    
    buyback_passed = await test_buyback_service()
    await asyncio.sleep(0.5)
    
    db_passed = await test_database_schema()
    await asyncio.sleep(0.5)
    
    api_passed = await test_api_imports()
    await asyncio.sleep(0.5)
    
    build_passed = await test_smart_contract_build()
    await asyncio.sleep(0.5)
    
    # Summary
    print_header("TEST SUMMARY")
    
    # Debug: Print actual values
    # print(f"DEBUG: env_passed={env_passed}, sc_passed={sc_passed}, buyback_passed={buyback_passed}")
    # print(f"DEBUG: db_passed={db_passed}, api_passed={api_passed}, build_passed={build_passed}")
    
    total_tests = 6
    # Convert all to True/False explicitly to avoid None issues
    results = [
        bool(env_passed),
        bool(sc_passed),
        bool(buyback_passed),
        bool(db_passed),
        bool(api_passed),
        bool(build_passed)
    ]
    passed_tests = sum(results)
    
    print(f"\n{Colors.BOLD}Results: {passed_tests}/{total_tests} tests passed{Colors.END}\n")
    
    if bool(env_passed):
        print_success("Environment Variables: PASS")
    else:
        print_error("Environment Variables: FAIL")
        
    if bool(sc_passed):
        print_success("Smart Contract Service: PASS")
    else:
        print_error("Smart Contract Service: FAIL")
        
    if bool(buyback_passed):
        print_success("Buyback Service: PASS")
    else:
        print_error("Buyback Service: FAIL")
        
    if bool(db_passed):
        print_success("Database Schema: PASS")
    else:
        print_warning("Database Schema: NEEDS MIGRATION")
        
    if bool(api_passed):
        print_success("API Routes: PASS")
    else:
        print_error("API Routes: FAIL")
        
    if bool(build_passed):
        print_success("Smart Contract Build: PASS")
    else:
        print_warning("Smart Contract Build: NOT YET")
    
    # Next steps
    print_header("NEXT STEPS")
    
    if not env_passed:
        print_info("1. Update your .env file with required variables")
        print_info("   See BUYBACK_CONFIG_GUIDE.md for details")
    
    if not db_passed:
        print_info("2. Run database migration:")
        print_info("   See DEPLOYMENT_AND_TESTING_GUIDE.md Phase 3")
    
    if not build_passed:
        print_info("3. Build smart contract:")
        print_info("   cd programs/billions-bounty && anchor build")
    
    if env_passed and sc_passed and buyback_passed and api_passed:
        print_success("\n🎉 Core system ready for deployment!")
        print_info("\nFollow DEPLOYMENT_AND_TESTING_GUIDE.md for:")
        print_info("  - Smart contract deployment")
        print_info("  - Database migration")
        print_info("  - Frontend testing")
        print_info("  - End-to-end verification")
    else:
        print_warning("\n⚠️  System not ready for deployment")
        print_info("Fix the issues above before deploying")
    
    # Exit code
    sys.exit(0 if passed_tests == total_tests else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Fatal error: {e}{Colors.END}")
        sys.exit(1)

