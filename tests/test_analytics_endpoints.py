"""
Automated Tests for Analytics/Dashboard Endpoints
Tests fund verification and contract activity endpoints with V2 support
"""

import sys
import os
import asyncio
import httpx
from typing import Dict, Any, List

# Configuration
BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TIMEOUT = 30.0

# Test results tracking
test_results = []

def log_test(name: str, passed: bool, details: str = ""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"   {details}")
    test_results.append({"name": name, "passed": passed, "details": details})

async def check_backend_running():
    """Check if backend is accessible"""
    print("\n" + "="*70)
    print("Checking Backend Status...")
    print("="*70)
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print("✅ Backend is running")
                return True
            else:
                print(f"⚠️  Backend returned status {response.status_code}")
                return True  # Still running, just different status
    except httpx.ConnectError:
        print("❌ Backend is NOT running!")
        print(f"   Please start backend or set BACKEND_URL env var")
        print(f"   Current BASE_URL: {BASE_URL}")
        return False
    except Exception as e:
        print(f"⚠️  Backend check error: {e}")
        return False

async def test_fund_verification_endpoint():
    """Test GET /api/dashboard/fund-verification"""
    print("\n" + "="*70)
    print("TEST: Fund Verification Endpoint")
    print("="*70)
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/api/dashboard/fund-verification")
            
            # Check HTTP status
            if response.status_code != 200:
                log_test("Fund Verification - HTTP Status", False, f"Got {response.status_code}")
                return False
            log_test("Fund Verification - HTTP Status", True, "200 OK")
            
            data = response.json()
            
            # Check response structure
            if "success" not in data:
                log_test("Fund Verification - Response Structure", False, "Missing 'success' field")
                return False
            
            if not data.get("success"):
                error_msg = data.get("error", "Unknown error")
                log_test("Fund Verification - API Success", False, f"API returned error: {error_msg}")
                return False
            
            log_test("Fund Verification - API Success", True, "API returned success=true")
            
            if "data" not in data:
                log_test("Fund Verification - Response Data", False, "Missing 'data' field")
                return False
            
            fund_data = data["data"]
            
            # Check required fields
            required_fields = [
                "lottery_funds",
                "jackpot_wallet",
                "fund_activity",
                "verification_links",
                "last_updated"
            ]
            
            for field in required_fields:
                if field not in fund_data:
                    log_test(f"Fund Verification - Field '{field}'", False, "Missing")
                    return False
                log_test(f"Fund Verification - Field '{field}'", True, "Present")
            
            # Check lottery_funds structure
            lottery_funds = fund_data.get("lottery_funds", {})
            lottery_required = ["lottery_pda", "program_id", "current_jackpot_usdc", "jackpot_balance_usdc"]
            for field in lottery_required:
                if field not in lottery_funds:
                    log_test(f"Fund Verification - Lottery '{field}'", False, "Missing")
                    return False
                log_test(f"Fund Verification - Lottery '{field}'", True, 
                        f"Value: {lottery_funds[field]}" if lottery_funds[field] else "Empty")
            
            # Check if V2 wallets are present (when V2 is enabled)
            if "v2_wallets" in fund_data and fund_data["v2_wallets"]:
                v2_wallets = fund_data["v2_wallets"]
                log_test("Fund Verification - V2 Wallets", True, f"Found {len(v2_wallets)} V2 wallets")
                
                # Check V2 wallet structure
                expected_v2_wallets = ["bounty_pool", "operational", "buyback", "staking"]
                for wallet_key in expected_v2_wallets:
                    if wallet_key in v2_wallets and v2_wallets[wallet_key]:
                        wallet = v2_wallets[wallet_key]
                        if "address" in wallet and "label" in wallet:
                            log_test(f"Fund Verification - V2 {wallet_key}", True, 
                                    f"Address: {wallet['address'][:20]}...")
                        else:
                            log_test(f"Fund Verification - V2 {wallet_key} structure", False, 
                                    "Missing address or label")
            
            # Check verification_links
            verification_links = fund_data.get("verification_links", {})
            link_fields = ["solana_explorer", "program_id", "jackpot_token_account"]
            
            for field in link_fields:
                if field in verification_links and verification_links[field]:
                    link = verification_links[field]
                    # Check if link is valid URL
                    if isinstance(link, str) and ("explorer.solana.com" in link or link.startswith("http")):
                        log_test(f"Fund Verification - Link '{field}'", True, "Valid URL")
                    else:
                        log_test(f"Fund Verification - Link '{field}'", False, f"Invalid URL: {link[:50]}")
            
            # Check V2-specific links if present
            v2_link_fields = ["bounty_pool_wallet", "operational_wallet", "buyback_wallet", "bounty_pda"]
            for field in v2_link_fields:
                if field in verification_links and verification_links[field]:
                    log_test(f"Fund Verification - V2 Link '{field}'", True, "Present")
            
            print(f"\n📊 Fund Verification Summary:")
            print(f"   Lottery PDA: {lottery_funds.get('lottery_pda', 'N/A')[:30]}...")
            print(f"   Program ID: {lottery_funds.get('program_id', 'N/A')[:30]}...")
            print(f"   Jackpot: ${lottery_funds.get('current_jackpot_usdc', 0):,.2f}")
            print(f"   Balance: ${lottery_funds.get('jackpot_balance_usdc', 0):,.2f}")
            if fund_data.get("v2_wallets"):
                print(f"   V2 Wallets: {len(fund_data['v2_wallets'])} configured")
            
            return True
            
    except Exception as e:
        log_test("Fund Verification - Exception", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_contract_activity_endpoint():
    """Test GET /api/contract/activity"""
    print("\n" + "="*70)
    print("TEST: Contract Activity Endpoint")
    print("="*70)
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Test with default limit
            response = await client.get(f"{BASE_URL}/api/contract/activity")
            
            # Check HTTP status
            if response.status_code != 200:
                log_test("Contract Activity - HTTP Status", False, f"Got {response.status_code}")
                # If 500, try to get error message
                if response.status_code == 500:
                    try:
                        error_data = response.json()
                        log_test("Contract Activity - Error Details", False, 
                                error_data.get("error", "Unknown error"))
                    except:
                        pass
                return False
            log_test("Contract Activity - HTTP Status", True, "200 OK")
            
            data = response.json()
            
            # Check response structure
            if "success" not in data:
                log_test("Contract Activity - Response Structure", False, "Missing 'success' field")
                return False
            
            log_test("Contract Activity - Response Structure", True, "Has 'success' field")
            
            if not data.get("success"):
                error_msg = data.get("error", "Unknown error")
                log_test("Contract Activity - API Success", False, f"API returned error: {error_msg}")
                # This is OK if no transactions exist yet
                if "not configured" in error_msg.lower() or "Program ID" in error_msg:
                    log_test("Contract Activity - Program ID", False, "Program ID not configured")
                return False
            
            log_test("Contract Activity - API Success", True, "API returned success=true")
            
            if "transactions" not in data:
                log_test("Contract Activity - Transactions Field", False, "Missing 'transactions' field")
                return False
            
            log_test("Contract Activity - Transactions Field", True, "Present")
            
            transactions = data.get("transactions", [])
            log_test("Contract Activity - Transactions List", True, f"Found {len(transactions)} transactions")
            
            # Test with custom limit
            response_limit = await client.get(f"{BASE_URL}/api/contract/activity?limit=10")
            if response_limit.status_code == 200:
                data_limit = response_limit.json()
                if "transactions" in data_limit:
                    limit_count = len(data_limit["transactions"])
                    log_test("Contract Activity - Limit Parameter", True, f"Returned {limit_count} transactions")
            
            # If transactions exist, check their structure
            if transactions:
                sample_tx = transactions[0]
                tx_fields = ["id", "type", "transaction_signature", "wallet_address", 
                           "amount", "status", "created_at"]
                
                for field in tx_fields:
                    if field in sample_tx:
                        log_test(f"Contract Activity - TX Field '{field}'", True, 
                                f"Value: {str(sample_tx[field])[:30]}...")
                    else:
                        log_test(f"Contract Activity - TX Field '{field}'", False, "Missing")
                
                print(f"\n📊 Contract Activity Summary:")
                print(f"   Total Transactions: {len(transactions)}")
                if transactions:
                    print(f"   Latest TX: {transactions[0].get('transaction_signature', 'N/A')[:30]}...")
                    print(f"   Latest Type: {transactions[0].get('type', 'N/A')}")
                    print(f"   Latest Status: {transactions[0].get('status', 'N/A')}")
            else:
                print(f"\n📊 Contract Activity Summary:")
                print(f"   No transactions found (this is OK if no activity yet)")
            
            return True
            
    except Exception as e:
        log_test("Contract Activity - Exception", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_verification_links_format():
    """Test that verification links are properly formatted"""
    print("\n" + "="*70)
    print("TEST: Verification Links Format")
    print("="*70)
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/api/dashboard/fund-verification")
            
            if response.status_code != 200:
                log_test("Links Format - HTTP Status", False, f"Got {response.status_code}")
                return False
            
            data = response.json()
            if not data.get("success"):
                log_test("Links Format - API Success", False, "API returned error")
                return False
            
            verification_links = data.get("data", {}).get("verification_links", {})
            
            # Check that links are valid URLs
            link_fields_to_check = [
                "solana_explorer",
                "program_id",
                "jackpot_token_account",
                "jackpot_wallet",
                "staking_wallet"
            ]
            
            all_valid = True
            for field in link_fields_to_check:
                link = verification_links.get(field)
                if link:
                    if isinstance(link, str) and ("explorer.solana.com" in link or link.startswith("http")):
                        # Check if it has proper cluster parameter
                        if "?cluster=devnet" in link or "?cluster=mainnet" in link or "?" not in link:
                            log_test(f"Links Format - {field}", True, "Valid URL")
                        else:
                            log_test(f"Links Format - {field}", False, "Missing cluster parameter")
                            all_valid = False
                    else:
                        log_test(f"Links Format - {field}", False, f"Invalid URL format: {link[:50]}")
                        all_valid = False
            
            # Check V2 links if present
            v2_link_fields = ["bounty_pool_wallet", "operational_wallet", "buyback_wallet", "bounty_pda"]
            for field in v2_link_fields:
                link = verification_links.get(field)
                if link:
                    if isinstance(link, str) and "explorer.solana.com" in link:
                        log_test(f"Links Format - V2 {field}", True, "Valid URL")
                    else:
                        log_test(f"Links Format - V2 {field}", False, "Invalid URL")
                        all_valid = False
            
            return all_valid
            
    except Exception as e:
        log_test("Links Format - Exception", False, f"Error: {str(e)}")
        return False

async def test_v2_wallet_addresses():
    """Test that V2 wallet addresses are correct when V2 is enabled"""
    print("\n" + "="*70)
    print("TEST: V2 Wallet Addresses")
    print("="*70)
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/api/dashboard/fund-verification")
            
            if response.status_code != 200:
                log_test("V2 Wallets - HTTP Status", False, f"Got {response.status_code}")
                return False
            
            data = response.json()
            if not data.get("success"):
                log_test("V2 Wallets - API Success", False, "API returned error")
                return False
            
            fund_data = data.get("data", {})
            v2_wallets = fund_data.get("v2_wallets")
            
            if not v2_wallets:
                log_test("V2 Wallets - Present", False, "V2 wallets not returned (may be V1 mode)")
                return True  # Not a failure if V2 not enabled
            
            log_test("V2 Wallets - Present", True, "V2 wallets found")
            
            # Check expected V2 wallets
            expected_wallets = ["bounty_pool", "operational", "buyback", "staking"]
            all_present = True
            
            for wallet_key in expected_wallets:
                if wallet_key in v2_wallets and v2_wallets[wallet_key]:
                    wallet = v2_wallets[wallet_key]
                    if "address" in wallet and wallet["address"]:
                        address = wallet["address"]
                        # Solana addresses are base58, typically 32-44 chars
                        if len(address) >= 32 and len(address) <= 44:
                            log_test(f"V2 Wallets - {wallet_key} address", True, 
                                    f"Valid format: {address[:10]}...{address[-5:]}")
                        else:
                            log_test(f"V2 Wallets - {wallet_key} address", False, 
                                    f"Invalid length: {len(address)} chars")
                            all_present = False
                        
                        if "label" in wallet and wallet["label"]:
                            log_test(f"V2 Wallets - {wallet_key} label", True, wallet["label"])
                        else:
                            log_test(f"V2 Wallets - {wallet_key} label", False, "Missing label")
                    else:
                        log_test(f"V2 Wallets - {wallet_key}", False, "Missing address")
                        all_present = False
                else:
                    log_test(f"V2 Wallets - {wallet_key}", False, "Not present")
                    all_present = False
            
            return all_present
            
    except Exception as e:
        log_test("V2 Wallets - Exception", False, f"Error: {str(e)}")
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def run_all_analytics_tests():
    """Run all analytics/dashboard tests"""
    print("\n" + "="*70)
    print("ANALYTICS/DASHBOARD ENDPOINT TEST SUITE")
    print("="*70)
    
    # Check backend
    if not await check_backend_running():
        print("\n❌ Cannot run tests - backend not running")
        print(f"\nTo start backend:")
        print(f"  cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty")
        print(f"  source venv/bin/activate")
        print(f"  python3 apps/backend/main.py")
        print(f"\nOr set BACKEND_URL env var:")
        print(f"  export BACKEND_URL=https://your-backend-url.com")
        return False
    
    # Run tests
    all_passed = True
    
    tests = [
        test_fund_verification_endpoint,
        test_contract_activity_endpoint,
        test_verification_links_format,
        test_v2_wallet_addresses,
    ]
    
    for test_func in tests:
        try:
            result = await test_func()
            all_passed = all_passed and result
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for r in test_results if r["passed"])
    total_count = len(test_results)
    
    print(f"\n✅ Passed: {passed_count}/{total_count}")
    print(f"❌ Failed: {total_count - passed_count}/{total_count}")
    
    if all_passed:
        print("\n🎉 ALL ANALYTICS TESTS PASSED!")
        print("\n✅ Analytics Endpoint Test Results:")
        print("   ✓ Fund verification endpoint working")
        print("   ✓ Contract activity endpoint working")
        print("   ✓ Verification links properly formatted")
        print("   ✓ V2 wallet addresses correct (if V2 enabled)")
        print("\n🚀 Analytics system is working correctly!")
    else:
        print("\n⚠️  Some tests failed. Review details above.")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(run_all_analytics_tests())
    sys.exit(0 if success else 1)

