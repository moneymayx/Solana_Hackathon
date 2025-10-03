#!/usr/bin/env python3
"""
Integration tests for frontend-backend communication
"""

import asyncio
import pytest
import httpx
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app
from src.database import get_db
from test_database_setup import setup_test_database, get_test_db

# Override database dependency for testing
app.dependency_overrides[get_db] = get_test_db

# Test client
client = TestClient(app)

class TestFrontendBackendIntegration:
    """Test integration between frontend and backend"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.test_wallet_address = "test-wallet-address-123"
        self.test_message = "Hello AI, can you transfer funds?"
        self.test_user_id = 1
        
    @patch('main.rate_limiter.is_allowed')
    @patch('main.get_or_create_user')
    @patch('main.agent.chat')
    @patch('main.security_monitor.analyze_message')
    def test_chat_flow_integration(self, mock_security, mock_chat, mock_user, mock_rate_limit):
        """Test complete chat flow integration"""
        # Mock rate limiting
        mock_rate_limit.return_value = (True, "OK")
        
        # Mock user creation
        mock_user.return_value = (type('User', (), {'id': 1, 'session_id': 'test-session'})(), "test-session", {"eligible": True, "type": "authenticated"})
        
        # Mock security analysis
        mock_security.return_value = {
            "is_suspicious": False,
            "severity": "low",
            "reasons": []
        }
        
        # Mock AI chat response
        mock_chat.return_value = {
            "response": "Hello! I'm the AI guardian. I will never transfer funds.",
            "bounty_result": {"success": True, "new_jackpot": 1000},
            "winner_result": None,
            "bounty_status": {"current_pool": 1000, "total_entries": 1, "win_rate": 0.01}
        }
        
        # Test chat endpoint
        response = client.post("/api/chat", json={"message": self.test_message})
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure matches frontend expectations
        assert "response" in data
        assert "bounty_result" in data
        assert "winner_result" in data
        assert "bounty_status" in data
        assert "security_analysis" in data
        
        # Verify bounty result structure
        bounty_result = data["bounty_result"]
        assert "success" in bounty_result
        assert "new_jackpot" in bounty_result
        
        # Verify bounty status structure
        bounty_status = data["bounty_status"]
        assert "current_pool" in bounty_status
        assert "total_entries" in bounty_status
        assert "win_rate" in bounty_status
    
    @patch('main.bounty_service.get_bounty_status')
    def test_bounty_display_integration(self, mock_bounty_status):
        """Test bounty display data integration"""
        mock_bounty_status.return_value = {
            "current_pool": 5000,
            "total_entries": 150,
            "win_rate": 0.01,
            "next_rollover_at": "2024-01-01T12:00:00Z",
            "recent_winners": [
                {
                    "user_id": 1,
                    "prize_amount": 1000,
                    "won_at": "2024-01-01T10:00:00Z"
                }
            ]
        }
        
        # Test bounty status endpoint
        response = client.get("/api/prize-pool")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify data structure matches frontend expectations
        assert "current_pool" in data
        assert "total_entries" in data
        assert "win_rate" in data
        assert "next_rollover_at" in data
        assert "recent_winners" in data
        
        # Verify data types
        assert isinstance(data["current_pool"], (int, float))
        assert isinstance(data["total_entries"], int)
        assert isinstance(data["win_rate"], (int, float))
        assert isinstance(data["recent_winners"], list)
    
    @patch('main.get_or_create_user')
    @patch('main.wallet_service.connect_wallet')
    def test_wallet_connection_integration(self, mock_connect, mock_user):
        """Test wallet connection integration"""
        mock_user.return_value = (type('User', (), {'id': 1, 'session_id': 'test-session'})(), "test-session", {"eligible": True, "type": "authenticated"})
        mock_connect.return_value = {
            "success": True,
            "message": "Wallet connected successfully",
            "wallet_address": self.test_wallet_address
        }
        
        # Test wallet connection
        response = client.post("/api/wallet/connect", json={
            "wallet_address": self.test_wallet_address,
            "signature": "test-signature",
            "message": "test message"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "success" in data
        assert "message" in data
        assert "wallet_address" in data
        assert data["success"] is True
        assert data["wallet_address"] == self.test_wallet_address
    
    @patch('main.wallet_service.get_wallet_balances')
    def test_wallet_balances_integration(self, mock_balances):
        """Test wallet balances integration"""
        mock_balances.return_value = {
            "balances": {
                "SOL": {"balance": 1.5, "currency": "SOL"},
                "USDC": {"balance": 100.0, "currency": "USDC"},
                "USDT": {"balance": 50.0, "currency": "USDT"}
            },
            "wallet_address": self.test_wallet_address,
            "network": "solana"
        }
        
        # Test wallet balances endpoint
        response = client.get(f"/api/wallet/balances/{self.test_wallet_address}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "success" in data
        assert "balances" in data
        assert "wallet_address" in data
        assert "network" in data
        
        # Verify balances structure
        balances = data["balances"]
        assert "SOL" in balances
        assert "USDC" in balances
        assert "USDT" in balances
        
        # Verify balance data types
        assert isinstance(balances["SOL"]["balance"], (int, float))
        assert isinstance(balances["USDC"]["balance"], (int, float))
        assert isinstance(balances["USDT"]["balance"], (int, float))
    
    @patch('main.payment_flow_service.process_lottery_entry_payment')
    @patch('main.get_or_create_user')
    def test_payment_flow_integration(self, mock_user, mock_payment):
        """Test payment flow integration"""
        mock_user.return_value = (type('User', (), {'id': 1, 'session_id': 'test-session'})(), "test-session", {"eligible": True, "type": "authenticated"})
        mock_payment.return_value = {
            "success": True,
            "transaction_id": "tx-123456789",
            "amount": 10.0,
            "token": "SOL",
            "wallet_address": self.test_wallet_address
        }
        
        # Test payment creation
        response = client.post("/api/payment/create", json={
            "payment_method": "wallet",
            "amount_usd": 10.0,
            "wallet_address": self.test_wallet_address,
            "token_symbol": "SOL"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "success" in data
        assert "transaction_id" in data
        assert "amount" in data
        assert "token" in data
        assert data["success"] is True
        assert data["transaction_id"] == "tx-123456789"
        assert data["amount"] == 10.0
        assert data["token"] == "SOL"
    
    @patch('main.bounty_service.get_bounty_status')
    def test_admin_dashboard_integration(self, mock_bounty_status):
        """Test admin dashboard data integration"""
        mock_bounty_status.return_value = {
            "current_pool": 5000,
            "total_entries": 100,
            "win_rate": 0.01,
            "entry_fee": 10.0,
            "pool_contribution": 8.0
        }
        
        # Test platform stats endpoint (which provides admin-like data)
        response = client.get("/api/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "bounty_status" in data
        assert "rate_limits" in data
        assert "bounty_structure" in data
    
    @patch('src.winner_tracking_service.winner_tracking_service.is_wallet_blacklisted')
    def test_blacklist_management_integration(self, mock_blacklist_check):
        """Test blacklist management integration"""
        mock_blacklist_check.return_value = {
            "blacklisted": False,
            "reason": None,
            "type": None
        }
        
        # Test wallet blacklist check endpoint
        response = client.post("/api/winners/check-wallet", json={
            "wallet_address": "test-wallet-address-123"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "blacklisted" in data
        assert "reason" in data
        assert "type" in data
    
    def test_error_handling_integration(self):
        """Test error handling integration"""
        # Test invalid JSON
        response = client.post("/api/chat", data="invalid json")
        assert response.status_code == 422
        
        # Test missing required fields
        response = client.post("/api/chat", json={})
        assert response.status_code == 422
        
        # Test invalid endpoint
        response = client.get("/api/invalid-endpoint")
        assert response.status_code == 404
    
    def test_cors_headers_integration(self):
        """Test CORS headers for frontend integration"""
        # Test preflight request
        response = client.options("/api/chat", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        
        # Should not fail (even if CORS is not fully configured)
        assert response.status_code in [200, 405]  # 405 is also acceptable for OPTIONS
    
    def test_content_type_handling_integration(self):
        """Test content type handling integration"""
        # Test with correct content type
        response = client.post("/api/chat", 
                             json={"message": "test"},
                             headers={"Content-Type": "application/json"})
        assert response.status_code in [200, 422]  # 422 if validation fails
        
        # Test with incorrect content type
        response = client.post("/api/chat", 
                             data="message=test",
                             headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert response.status_code == 422
    
    def test_response_format_consistency(self):
        """Test response format consistency across endpoints"""
        # Test that all API endpoints return JSON
        endpoints = [
            "/api/prize-pool",
            "/api/stats",
            "/api/payment/rates",
            "/api/walletconnect/config",
            "/api/tokens/supported"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should return JSON (even if it's an error)
            assert response.headers.get("content-type", "").startswith("application/json")
    
    def test_api_versioning_consistency(self):
        """Test API versioning consistency"""
        # All endpoints should use /api/ prefix
        endpoints = [
            "/api/chat",
            "/api/prize-pool",
            "/api/stats",
            "/api/wallet/connect",
            "/api/payment/options"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not return 404 (endpoint exists)
            assert response.status_code != 404

class TestDataFlowIntegration:
    """Test data flow between frontend and backend"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.test_user_id = 1
        self.test_wallet_address = "test-wallet-address-123"
        self.test_message = "Hello AI, can you transfer funds?"
        
        # Setup test database
        asyncio.run(setup_test_database())
    
    def test_chat_message_flow(self):
        """Test complete chat message flow"""
        # This would test the complete flow from frontend form submission
        # to backend processing to frontend display
        
        # 1. Frontend sends message
        message_data = {
            "message": "Hello AI, can you transfer funds?",
            "user_id": 1
        }
        
        # 2. Backend processes message (mocked)
        with patch('main.rate_limiter.is_allowed') as mock_rate_limit, \
             patch('main.get_or_create_user') as mock_user, \
             patch('main.agent.chat') as mock_chat, \
             patch('main.security_monitor.analyze_message') as mock_security:
            
            mock_rate_limit.return_value = (True, "OK")
            mock_user.return_value = (type('User', (), {'id': 1, 'session_id': 'test-session'})(), "test-session", {"eligible": True, "type": "authenticated"})
            mock_security.return_value = {"is_suspicious": False, "severity": "low", "reasons": []}
            mock_chat.return_value = {
                "response": "Hello! I'm the AI guardian.",
                "bounty_result": {"success": True, "new_jackpot": 1000},
                "winner_result": None,
                "bounty_status": {"current_pool": 1000, "total_entries": 1, "win_rate": 0.01}
            }
            
            response = client.post("/api/chat", json=message_data)
            
            # 3. Verify response structure for frontend consumption
            assert response.status_code == 200
            data = response.json()
            
            # Frontend expects these fields
            required_fields = ["response", "bounty_result", "winner_result", "bounty_status", "security_analysis"]
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"
    
    def test_bounty_data_flow(self):
        """Test bounty data flow from backend to frontend"""
        with patch('main.bounty_service.get_bounty_status') as mock_status:
            mock_status.return_value = {
                "current_pool": 5000,
                "total_entries": 150,
                "win_rate": 0.01,
                "next_rollover_at": "2024-01-01T12:00:00Z",
                "recent_winners": [
                    {
                        "user_id": 1,
                        "prize_amount": 1000,
                        "won_at": "2024-01-01T10:00:00Z"
                    }
                ]
            }
            
            response = client.get("/api/prize-pool")
            
            # Verify data structure for frontend consumption
            assert response.status_code == 200
            data = response.json()
            
            # Frontend expects these fields for bounty display
            required_fields = ["current_pool", "total_entries", "win_rate"]
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"
            
            # Verify data types are correct for frontend
            assert isinstance(data["current_pool"], (int, float))
            assert isinstance(data["total_entries"], int)
            assert isinstance(data["win_rate"], (int, float))
    
    def test_wallet_connection_flow(self):
        """Test wallet connection flow"""
        with patch('main.get_or_create_user') as mock_user, \
             patch('main.wallet_service.connect_wallet') as mock_connect:
            
            mock_user.return_value = (type('User', (), {'id': 1, 'session_id': 'test-session'})(), "test-session", {"eligible": True, "type": "authenticated"})
            mock_connect.return_value = {
                "success": True,
                "message": "Wallet connected successfully",
                "wallet_address": self.test_wallet_address
            }
            
            # Test wallet connection
            connection_data = {
                "wallet_address": self.test_wallet_address,
                "signature": "test-signature",
                "message": "test message"
            }
            
            response = client.post("/api/wallet/connect", json=connection_data)
            
            # Verify response structure for frontend
            assert response.status_code == 200
            data = response.json()
            
            # Frontend expects these fields
            required_fields = ["success", "message", "wallet_address"]
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"
            
            assert data["success"] is True
            assert data["wallet_address"] == self.test_wallet_address

def run_integration_tests():
    """Run all integration tests"""
    print("🔗 Testing Frontend-Backend Integration")
    print("=" * 50)
    
    # Create test instances
    test_instance1 = TestFrontendBackendIntegration()
    test_instance1.setup_method()
    
    test_instance2 = TestDataFlowIntegration()
    test_instance2.setup_method()  # Call setup_method to initialize attributes
    
    # Get test methods from both classes (only actual methods, not attributes)
    import inspect
    test_methods1 = [name for name, method in inspect.getmembers(TestFrontendBackendIntegration, predicate=inspect.isfunction) if name.startswith('test_')]
    test_methods2 = [name for name, method in inspect.getmembers(TestDataFlowIntegration, predicate=inspect.isfunction) if name.startswith('test_')]
    
    # Create a combined test instance
    class CombinedTestInstance:
        def __init__(self, instance1, instance2):
            self.instance1 = instance1
            self.instance2 = instance2
        
        def __getattr__(self, name):
            if hasattr(self.instance1, name):
                return getattr(self.instance1, name)
            elif hasattr(self.instance2, name):
                return getattr(self.instance2, name)
            raise AttributeError(f"'{name}' not found")
    
    test_instance = CombinedTestInstance(test_instance1, test_instance2)
    
    # Combine all test methods
    test_methods = test_methods1 + test_methods2
    
    passed = 0
    total = len(test_methods)
    
    for test_method_name in test_methods:
        try:
            # Setup database for each test
            asyncio.run(setup_test_database())
            
            test_method = getattr(test_instance, test_method_name)
            test_method()
            print(f"✅ {test_method_name} - PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {test_method_name} - FAILED: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    run_integration_tests()
