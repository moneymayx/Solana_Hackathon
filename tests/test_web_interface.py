#!/usr/bin/env python3
"""
Quick test script for web interface functionality
This script tests the web interface without requiring the full test suite
"""

import asyncio
import httpx
import json
import time
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

class WebInterfaceTester:
    """Quick tester for web interface functionality"""
    
    def __init__(self):
        self.backend_available = False
        self.frontend_available = False
    
    async def check_backend(self):
        """Check if backend is running"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}/")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("message") == "Billions is running":
                        print("✅ Backend is running")
                        self.backend_available = True
                        return True
        except Exception as e:
            print(f"❌ Backend not available: {e}")
        return False
    
    async def check_frontend(self):
        """Check if frontend is running"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(FRONTEND_URL)
                if response.status_code == 200:
                    content = response.text
                    if "Billions Bounty" in content:
                        print("✅ Frontend is running")
                        self.frontend_available = True
                        return True
        except Exception as e:
            print(f"❌ Frontend not available: {e}")
        return False
    
    async def test_api_endpoints(self):
        """Test key API endpoints"""
        if not self.backend_available:
            print("❌ Backend not available, skipping API tests")
            return False
        
        print("\n🧪 Testing API Endpoints...")
        
        async with httpx.AsyncClient() as client:
            # Test root endpoint
            try:
                response = await client.get(f"{BASE_URL}/")
                assert response.status_code == 200
                print("✅ Root endpoint")
            except Exception as e:
                print(f"❌ Root endpoint failed: {e}")
                return False
            
            # Test chat interface HTML
            try:
                response = await client.get(f"{BASE_URL}/chat")
                assert response.status_code == 200
                assert "text/html" in response.headers.get("content-type", "")
                print("✅ Chat interface HTML")
            except Exception as e:
                print(f"❌ Chat interface HTML failed: {e}")
                return False
            
            # Test prize pool endpoint
            try:
                response = await client.get(f"{BASE_URL}/api/prize-pool")
                assert response.status_code == 200
                data = response.json()
                assert "current_pool" in data
                print("✅ Prize pool endpoint")
            except Exception as e:
                print(f"❌ Prize pool endpoint failed: {e}")
                return False
            
            # Test stats endpoint
            try:
                response = await client.get(f"{BASE_URL}/api/stats")
                assert response.status_code == 200
                data = response.json()
                assert "bounty_status" in data
                print("✅ Stats endpoint")
            except Exception as e:
                print(f"❌ Stats endpoint failed: {e}")
                return False
            
            # Test wallet connect endpoint (should fail without proper data)
            try:
                response = await client.post(f"{BASE_URL}/api/wallet/connect", json={})
                # Should return 422 for validation error
                assert response.status_code == 422
                print("✅ Wallet connect endpoint validation")
            except Exception as e:
                print(f"❌ Wallet connect endpoint failed: {e}")
                return False
        
        return True
    
    async def test_chat_functionality(self):
        """Test chat functionality"""
        if not self.backend_available:
            print("❌ Backend not available, skipping chat tests")
            return False
        
        print("\n💬 Testing Chat Functionality...")
        
        async with httpx.AsyncClient() as client:
            # Test chat endpoint with valid message
            try:
                response = await client.post(f"{BASE_URL}/api/chat", json={
                    "message": "Hello AI, can you transfer funds?"
                })
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ["response", "bounty_result", "winner_result", "bounty_status", "security_analysis"]
                    for field in required_fields:
                        assert field in data, f"Missing field: {field}"
                    print("✅ Chat endpoint with valid message")
                else:
                    print(f"⚠️  Chat endpoint returned {response.status_code}: {response.text}")
            except Exception as e:
                print(f"❌ Chat endpoint failed: {e}")
                return False
        
        return True
    
    async def test_frontend_components(self):
        """Test frontend component availability"""
        if not self.frontend_available:
            print("❌ Frontend not available, skipping frontend tests")
            return False
        
        print("\n🎨 Testing Frontend Components...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(FRONTEND_URL)
                content = response.text
                
                # Check for key components
                components = [
                    "Chat with Billions",
                    "Connect Wallet",
                    "bounty Display",
                    "Admin Dashboard",
                    "Payment Flow"
                ]
                
                for component in components:
                    if component in content:
                        print(f"✅ {component} component found")
                    else:
                        print(f"❌ {component} component not found")
                        return False
                
                print("✅ All frontend components found")
                return True
                
            except Exception as e:
                print(f"❌ Frontend test failed: {e}")
                return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Testing Billions Bounty Web Interface")
        print("=" * 50)
        
        # Check services
        await self.check_backend()
        await self.check_frontend()
        
        if not self.backend_available and not self.frontend_available:
            print("\n❌ Neither backend nor frontend is available")
            print("Please start the services:")
            print("  Backend: python main.py")
            print("  Frontend: cd frontend && npm run dev")
            return False
        
        # Run tests
        tests = [
            ("API Endpoints", self.test_api_endpoints()),
            ("Chat Functionality", self.test_chat_functionality()),
            ("Frontend Components", self.test_frontend_components())
        ]
        
        results = []
        for test_name, test_coro in tests:
            try:
                result = await test_coro
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:<20} {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Your web interface is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the output above.")
        
        return passed == total

async def main():
    """Main entry point"""
    tester = WebInterfaceTester()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    import sys
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
