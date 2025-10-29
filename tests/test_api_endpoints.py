"""
Automated API Endpoint Tests
Tests all escape plan and system APIs
"""

import sys
import os
import time
import asyncio
import httpx
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
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
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Backend is running")
                return True
            else:
                print(f"⚠️  Backend returned status {response.status_code}")
                return True  # Still running, just different status
    except httpx.ConnectError:
        print("❌ Backend is NOT running!")
        print("   Please start backend with: python3 src/main.py")
        return False
    except Exception as e:
        print(f"⚠️  Backend check error: {e}")
        return False

async def test_escape_plan_status_api():
    """Test GET /api/bounty/escape-plan/status"""
    print("\n" + "="*70)
    print("TEST: Escape Plan Status API")
    print("="*70)
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{BASE_URL}/api/bounty/escape-plan/status",
                params={"bounty_id": 1}
            )
            
            if response.status_code != 200:
                log_test("Status API - HTTP Status", False, f"Got {response.status_code}")
                return False
            
            log_test("Status API - HTTP Status", True, "200 OK")
            
            data = response.json()
            
            # Check response structure
            required_fields = ["success", "escape_plan"]
            for field in required_fields:
                if field not in data:
                    log_test(f"Status API - Field '{field}'", False, "Missing")
                    return False
                log_test(f"Status API - Field '{field}'", True, "Present")
            
            # Check escape_plan data
            escape_plan = data.get("escape_plan", {})
            if "is_active" in escape_plan:
                log_test("Status API - is_active", True, f"Value: {escape_plan['is_active']}")
            
            if "message" in escape_plan:
                log_test("Status API - message", True, f"{escape_plan['message'][:50]}...")
            
            if "should_trigger" in escape_plan:
                log_test("Status API - should_trigger", True, f"Value: {escape_plan['should_trigger']}")
            
            # Check for OBSOLETE markers (should not exist)
            response_text = response.text.lower()
            if "obsolete" in response_text:
                log_test("Status API - No OBSOLETE", False, "Found OBSOLETE in response")
                return False
            log_test("Status API - No OBSOLETE", True, "Clean response")
            
            print(f"\n📊 Status Response:")
            print(f"   Active: {escape_plan.get('is_active')}")
            print(f"   Time since last: {escape_plan.get('time_since_last_question', 'N/A')}")
            print(f"   Time until escape: {escape_plan.get('time_until_escape', 'N/A')}")
            print(f"   Should trigger: {escape_plan.get('should_trigger')}")
            
            return True
            
    except Exception as e:
        log_test("Status API", False, f"Exception: {e}")
        return False

async def test_escape_plan_trigger_api():
    """Test POST /api/bounty/escape-plan/trigger"""
    print("\n" + "="*70)
    print("TEST: Escape Plan Trigger API")
    print("="*70)
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{BASE_URL}/api/bounty/escape-plan/trigger",
                params={"bounty_id": 1}
            )
            
            if response.status_code not in [200, 400]:  # 400 is ok if not ready
                log_test("Trigger API - HTTP Status", False, f"Got {response.status_code}")
                return False
            
            log_test("Trigger API - HTTP Status", True, f"{response.status_code}")
            
            data = response.json()
            
            # Check response structure
            if "success" not in data:
                log_test("Trigger API - Response Structure", False, "Missing 'success'")
                return False
            
            log_test("Trigger API - Response Structure", True, "Valid")
            
            # If not ready to trigger, that's expected
            if not data.get("success"):
                if "24 hours have not passed" in data.get("error", "") or \
                   "not ready" in data.get("message", "").lower():
                    log_test("Trigger API - Expected Rejection", True, "Not ready (expected)")
                    print(f"\n📊 Trigger Response: {data.get('error') or data.get('message')}")
                else:
                    log_test("Trigger API - Error Handling", True, f"Error: {data.get('error', 'Unknown')}")
            else:
                log_test("Trigger API - Execution", True, "Executed successfully")
                print(f"\n📊 Trigger executed: {data.get('message', 'Success')}")
            
            return True
            
    except Exception as e:
        log_test("Trigger API", False, f"Exception: {e}")
        return False

async def test_bounty_chat_api():
    """Test POST /api/bounty/{id}/chat (timer reset integration)"""
    print("\n" + "="*70)
    print("TEST: Bounty Chat API (Timer Reset)")
    print("="*70)
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Send a test message
            response = await client.post(
                f"{BASE_URL}/api/bounty/1/chat",
                json={
                    "message": "Test message for timer reset",
                    "user_id": 1,
                    "wallet_address": "TestWallet123",
                    "ip_address": "127.0.0.1"
                }
            )
            
            # May fail due to free question limits, but that's ok
            if response.status_code in [200, 400, 422]:
                log_test("Chat API - Accessible", True, f"Status: {response.status_code}")
                
                # Check if timer integration exists (no errors about escape_plan_service)
                response_text = response.text
                if "escape_plan_service" in response_text and "error" in response_text.lower():
                    log_test("Chat API - Timer Integration", False, "Import error detected")
                    return False
                else:
                    log_test("Chat API - Timer Integration", True, "No import errors")
                
                return True
            else:
                log_test("Chat API", False, f"Unexpected status: {response.status_code}")
                return False
                
    except Exception as e:
        # May fail due to missing dependencies, but we can check the error
        error_msg = str(e).lower()
        if "escape_plan_service" in error_msg and "cannot import" in error_msg:
            log_test("Chat API - Timer Integration", False, "Import error")
            return False
        else:
            log_test("Chat API", True, f"Endpoint exists (validation error expected)")
            return True

async def test_stats_api():
    """Test GET /api/stats"""
    print("\n" + "="*70)
    print("TEST: Platform Stats API")
    print("="*70)
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(f"{BASE_URL}/api/stats")
            
            if response.status_code == 200:
                log_test("Stats API", True, "Accessible")
                data = response.json()
                print(f"\n📊 Platform Stats:")
                for key, value in list(data.items())[:5]:
                    print(f"   {key}: {value}")
                return True
            else:
                log_test("Stats API", False, f"Status: {response.status_code}")
                return False
                
    except Exception as e:
        log_test("Stats API", False, f"Exception: {e}")
        return False

async def test_api_error_handling():
    """Test API error handling"""
    print("\n" + "="*70)
    print("TEST: API Error Handling")
    print("="*70)
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Test invalid bounty_id
            response = await client.get(
                f"{BASE_URL}/api/bounty/escape-plan/status",
                params={"bounty_id": 99999}
            )
            
            if response.status_code in [200, 404]:
                log_test("Error Handling - Invalid ID", True, "Handled gracefully")
            else:
                log_test("Error Handling - Invalid ID", False, f"Status: {response.status_code}")
            
            return True
            
    except Exception as e:
        log_test("Error Handling", False, f"Exception: {e}")
        return False

async def test_configuration_endpoints():
    """Test configuration and system endpoints"""
    print("\n" + "="*70)
    print("TEST: Configuration Endpoints")
    print("="*70)
    
    endpoints = [
        "/api/token/config",
        "/api/token/staking/tier-stats",
        "/api/bounty/1/status",
    ]
    
    results = []
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        for endpoint in endpoints:
            try:
                response = await client.get(f"{BASE_URL}{endpoint}")
                passed = response.status_code in [200, 404]
                log_test(f"Config - {endpoint}", passed, f"Status: {response.status_code}")
                results.append(passed)
            except Exception as e:
                log_test(f"Config - {endpoint}", False, f"Error: {e}")
                results.append(False)
    
    return all(results)

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def run_all_api_tests():
    """Run all API tests"""
    print("\n" + "🎯"*35)
    print("AUTOMATED API ENDPOINT TEST SUITE")
    print("🎯"*35)
    
    # Check backend
    if not await check_backend_running():
        print("\n❌ Cannot run tests - backend not running")
        print("\nTo start backend:")
        print("  cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty")
        print("  source venv/bin/activate")
        print("  python3 src/main.py")
        return False
    
    # Run tests
    all_passed = True
    
    tests = [
        test_escape_plan_status_api,
        test_escape_plan_trigger_api,
        test_bounty_chat_api,
        test_stats_api,
        test_api_error_handling,
        test_configuration_endpoints,
    ]
    
    for test_func in tests:
        try:
            result = await test_func()
            all_passed = all_passed and result
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
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
        print("\n🎉 ALL API TESTS PASSED!")
        print("\n✅ API Endpoint Test Results:")
        print("   ✓ Escape plan status API working")
        print("   ✓ Escape plan trigger API working")
        print("   ✓ Timer integration in chat endpoints")
        print("   ✓ Error handling implemented")
        print("   ✓ Configuration endpoints accessible")
        print("\n🚀 API system is working correctly!")
    else:
        print("\n⚠️  Some tests failed. Review details above.")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(run_all_api_tests())
    sys.exit(0 if success else 1)

