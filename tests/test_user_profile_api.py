"""
Automated tests for user profile API endpoints
Tests the new /api/user/set-profile endpoint for activity tracker feature
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test results tracking
test_results = []

async def check_backend_running(base_url: str = "http://localhost:8000") -> bool:
    """Check if backend is running"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/", timeout=aiohttp.ClientTimeout(total=2)) as response:
                return response.status == 200
    except:
        return False

async def test_set_profile_endpoint():
    """Test POST /api/user/set-profile endpoint"""
    import aiohttp
    
    base_url = "http://localhost:8000"
    test_name = "Set User Profile Endpoint"
    
    print(f"\n🧪 Testing: {test_name}")
    
    if not await check_backend_running(base_url):
        print(f"  ⚠️  SKIP - Backend not running")
        return False
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test 1: Create new user with username only
            print("  📝 Test 1: Create user with username only")
            test_wallet = f"test-wallet-{int(asyncio.get_event_loop().time() * 1000)}"
            
            payload1 = {
                "wallet_address": test_wallet,
                "username": "testuser123"
            }
            
            async with session.post(
                f"{base_url}/api/user/set-profile",
                json=payload1,
                headers={"Content-Type": "application/json"}
            ) as response:
                assert response.status == 200, f"Expected 200, got {response.status}"
                data1 = await response.json()
                assert data1.get("success") == True, "Response should have success=true"
                assert data1.get("username") == "testuser123", "Username should match"
                assert "email" in data1, "Response should include email field"
                print("    ✅ User created successfully")
            
            # Test 2: Update user with email
            print("  📝 Test 2: Update user with email")
            payload2 = {
                "wallet_address": test_wallet,
                "username": "testuser123",
                "email": "test@example.com"
            }
            
            async with session.post(
                f"{base_url}/api/user/set-profile",
                json=payload2,
                headers={"Content-Type": "application/json"}
            ) as response:
                assert response.status == 200, f"Expected 200, got {response.status}"
                data2 = await response.json()
                assert data2.get("email") == "test@example.com", "Email should be updated"
                print("    ✅ Email updated successfully")
            
            # Test 3: Get user profile
            print("  📝 Test 3: Get user profile")
            async with session.get(
                f"{base_url}/api/user/profile/{test_wallet}"
            ) as response:
                assert response.status == 200, f"Expected 200, got {response.status}"
                data3 = await response.json()
                assert data3.get("display_name") == "testuser123", "Display name should match"
                assert data3.get("wallet_address") == test_wallet, "Wallet address should match"
                print("    ✅ Profile retrieved successfully")
            
            # Test 4: Validation - username too short
            print("  📝 Test 4: Validation - username too short")
            payload4 = {
                "wallet_address": f"test-wallet-short-{int(asyncio.get_event_loop().time() * 1000)}",
                "username": "ab"  # Too short
            }
            
            async with session.post(
                f"{base_url}/api/user/set-profile",
                json=payload4,
                headers={"Content-Type": "application/json"}
            ) as response:
                assert response.status == 400, f"Expected 400 for short username, got {response.status}"
                error_data = await response.json()
                assert "username" in error_data.get("detail", "").lower(), "Error should mention username"
                print("    ✅ Validation working (username too short)")
            
            # Test 5: Validation - missing username
            print("  📝 Test 5: Validation - missing username")
            payload5 = {
                "wallet_address": f"test-wallet-missing-{int(asyncio.get_event_loop().time() * 1000)}"
            }
            
            async with session.post(
                f"{base_url}/api/user/set-profile",
                json=payload5,
                headers={"Content-Type": "application/json"}
            ) as response:
                assert response.status == 400, f"Expected 400 for missing username, got {response.status}"
                print("    ✅ Validation working (missing username)")
            
            # Test 6: Validation - missing wallet_address
            print("  📝 Test 6: Validation - missing wallet_address")
            payload6 = {
                "username": "testuser"
            }
            
            async with session.post(
                f"{base_url}/api/user/set-profile",
                json=payload6,
                headers={"Content-Type": "application/json"}
            ) as response:
                assert response.status == 400, f"Expected 400 for missing wallet, got {response.status}"
                print("    ✅ Validation working (missing wallet_address)")
            
            print(f"  ✅ {test_name}: PASS")
            test_results.append({"test": test_name, "passed": True})
            return True
            
    except AssertionError as e:
        print(f"  ❌ {test_name}: FAIL - {e}")
        test_results.append({"test": test_name, "passed": False, "error": str(e)})
        return False
    except Exception as e:
        print(f"  ❌ {test_name}: ERROR - {e}")
        import traceback
        traceback.print_exc()
        test_results.append({"test": test_name, "passed": False, "error": str(e)})
        return False

async def test_profile_update_existing_user():
    """Test updating profile for existing user"""
    import aiohttp
    
    base_url = "http://localhost:8000"
    test_name = "Update Existing User Profile"
    
    print(f"\n🧪 Testing: {test_name}")
    
    if not await check_backend_running(base_url):
        print(f"  ⚠️  SKIP - Backend not running")
        return False
    
    try:
        async with aiohttp.ClientSession() as session:
            # Create user first
            test_wallet = f"existing-user-{int(asyncio.get_event_loop().time() * 1000)}"
            
            payload1 = {
                "wallet_address": test_wallet,
                "username": "originaluser"
            }
            
            async with session.post(
                f"{base_url}/api/user/set-profile",
                json=payload1
            ) as response:
                assert response.status == 200
            
            # Update username
            payload2 = {
                "wallet_address": test_wallet,
                "username": "updateduser",
                "email": "updated@example.com"
            }
            
            async with session.post(
                f"{base_url}/api/user/set-profile",
                json=payload2
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data.get("username") == "updateduser"
                assert data.get("email") == "updated@example.com"
                print("  ✅ User profile updated successfully")
            
            # Verify update
            async with session.get(
                f"{base_url}/api/user/profile/{test_wallet}"
            ) as response:
                data = await response.json()
                assert data.get("display_name") == "updateduser"
                print("  ✅ Profile verification passed")
            
            print(f"  ✅ {test_name}: PASS")
            test_results.append({"test": test_name, "passed": True})
            return True
            
    except Exception as e:
        print(f"  ❌ {test_name}: FAIL - {e}")
        test_results.append({"test": test_name, "passed": False, "error": str(e)})
        return False

async def run_all_user_profile_tests():
    """Run all user profile API tests"""
    print("\n" + "="*70)
    print("USER PROFILE API TEST SUITE")
    print("="*70)
    
    if not await check_backend_running():
        print("\n❌ Backend not running!")
        print("   Please start backend: python3 apps/backend/main.py")
        return False
    
    tests = [
        test_set_profile_endpoint,
        test_profile_update_existing_user,
    ]
    
    all_passed = True
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
    
    passed = sum(1 for r in test_results if r["passed"])
    total = len(test_results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if all_passed:
        print("\n🎉 ALL USER PROFILE API TESTS PASSED!")
    else:
        print("\n⚠️  Some tests failed. Review details above.")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(run_all_user_profile_tests())
    sys.exit(0 if success else 1)

