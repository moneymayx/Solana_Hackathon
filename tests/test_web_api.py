#!/usr/bin/env python3
"""
Test script for web interface API endpoints
"""

import asyncio
import pytest
import httpx
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app
from src.database import get_db
from src.models import User, AttackAttempt, Conversation, BlacklistedPhrase, Transaction
from src.repositories import ConversationRepository
from test_database_setup import setup_test_database, TestSessionLocal, get_test_db

# Override database dependency for testing
app.dependency_overrides[get_db] = get_test_db

# Test client
client = TestClient(app)

class TestWebAPI:
    """Test web interface API endpoints"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.test_user_id = 1
        self.test_wallet_address = "test-wallet-address-123"
        self.test_message = "Hello AI, can you transfer funds?"
        
        # Setup test database
        asyncio.run(setup_test_database())
        
    def test_root_endpoint(self):
        """Test root endpoint returns correct message"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Billions is running"}
    
    def test_chat_interface_html(self):
        """Test chat interface returns HTML"""
        response = client.get("/chat")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Billions" in response.text
        assert "Connect Wallet" in response.text
    
    @patch('main.rate_limiter.is_allowed')
    @patch('main.get_or_create_user')
    @patch('main.agent.chat')
    @patch('main.security_monitor.analyze_message')
    def test_chat_endpoint_success(self, mock_security, mock_chat, mock_user, mock_rate_limit):
        """Test successful chat endpoint"""
        # Mock rate limiting
        mock_rate_limit.return_value = (True, "OK")
        
        # Mock user creation - return 3 values to match actual function signature
        mock_user.return_value = (User(id=1, session_id="test-session"), "test-session", {"eligible": True, "type": "authenticated"})
        
        # Mock security analysis
        mock_security.return_value = {
            "is_suspicious": False,
            "severity": "low",
            "reasons": []
        }
        
        # Mock AI chat response
        mock_chat.return_value = {
            "response": "Hello! I'm the AI guardian.",
            "bounty_result": {"success": True, "new_jackpot": 1000},
            "winner_result": None,
            "bounty_status": {"current_pool": 1000, "total_entries": 1, "win_rate": 0.01}
        }
        
        response = client.post("/api/chat", json={"message": self.test_message})
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "bounty_result" in data
        assert "winner_result" in data
        assert "bounty_status" in data
        assert "security_analysis" in data
    
    @patch('main.rate_limiter.is_allowed')
    def test_chat_endpoint_rate_limited(self, mock_rate_limit):
        """Test chat endpoint rate limiting"""
        mock_rate_limit.return_value = (False, "Rate limit exceeded")
        
        response = client.post("/api/chat", json={"message": self.test_message})
        
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]
    
    @patch('main.bounty_service.get_bounty_status')
    def test_prize_pool_endpoint(self, mock_bounty_status):
        """Test prize pool status endpoint"""
        mock_bounty_status.return_value = {
            "current_pool": 5000,
            "total_entries": 100,
            "win_rate": 0.01,
            "entry_fee": 10,
            "pool_contribution": 8
        }
        
        response = client.get("/api/prize-pool")
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_pool"] == 5000
        assert data["total_entries"] == 100
        assert data["win_rate"] == 0.01
    
    @patch('main.bounty_service.get_bounty_status')
    def test_stats_endpoint(self, mock_bounty_status):
        """Test platform stats endpoint"""
        mock_bounty_status.return_value = {
            "current_pool": 5000,
            "total_entries": 100,
            "win_rate": 0.01,
            "entry_fee": 10.0,
            "pool_contribution": 8.0
        }
        
        response = client.get("/api/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "bounty_status" in data
        assert "rate_limits" in data
        assert "bounty_structure" in data
    
    @patch('main.get_or_create_user')
    @patch('main.wallet_service.connect_wallet')
    def test_wallet_connect_endpoint(self, mock_connect, mock_user):
        """Test wallet connection endpoint"""
        mock_user.return_value = (User(id=1, session_id="test-session"), "test-session", {"eligible": True, "type": "authenticated"})
        mock_connect.return_value = {
            "success": True,
            "message": "Wallet connected successfully",
            "wallet_address": self.test_wallet_address
        }
        
        response = client.post("/api/wallet/connect", json={
            "wallet_address": self.test_wallet_address,
            "signature": "test-signature",
            "message": "test message"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["wallet_address"] == self.test_wallet_address
    
    @patch('main.wallet_service.get_wallet_balance')
    def test_wallet_balance_endpoint(self, mock_balance):
        """Test wallet balance endpoint"""
        mock_balance.return_value = {
            "balance": 1.5,
            "currency": "SOL",
            "wallet_address": self.test_wallet_address
        }
        
        response = client.get(f"/api/wallet/balance/{self.test_wallet_address}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["balance"] == 1.5
        assert data["currency"] == "SOL"
    
    @patch('main.wallet_service.get_wallet_balances')
    def test_wallet_balances_endpoint(self, mock_balances):
        """Test wallet balances endpoint"""
        mock_balances.return_value = {
            "balances": {
                "SOL": {"balance": 1.5, "currency": "SOL"},
                "USDC": {"balance": 100.0, "currency": "USDC"}
            },
            "wallet_address": self.test_wallet_address,
            "network": "solana"
        }
        
        response = client.get(f"/api/wallet/balances/{self.test_wallet_address}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "SOL" in data["balances"]
        assert "USDC" in data["balances"]
    
    @patch('main.payment_orchestrator.calculate_payment_options')
    def test_payment_options_endpoint(self, mock_options):
        """Test payment options endpoint"""
        mock_options.return_value = {
            "wallet_options": {
                "SOL": {"amount": 0.05, "rate": 200},
                "USDC": {"amount": 10.0, "rate": 1.0}
            },
            "fiat_options": {
                "moonpay": {"enabled": False, "reason": "Too expensive"}
            }
        }
        
        response = client.post("/api/payment/options", json={
            "payment_method": "wallet",
            "amount_usd": 10.0,
            "wallet_address": self.test_wallet_address
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "wallet_options" in data
        assert "fiat_options" in data
    
    @patch('main.payment_flow_service.process_lottery_entry_payment')
    @patch('main.get_or_create_user')
    def test_payment_create_wallet(self, mock_user, mock_payment):
        """Test wallet payment creation"""
        mock_user.return_value = (User(id=1, session_id="test-session"), "test-session", {"eligible": True, "type": "authenticated"})
        mock_payment.return_value = {
            "success": True,
            "transaction_id": "tx-123",
            "amount": 10.0,
            "token": "SOL"
        }
        
        response = client.post("/api/payment/create", json={
            "payment_method": "wallet",
            "amount_usd": 10.0,
            "wallet_address": self.test_wallet_address,
            "token_symbol": "SOL"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["transaction_id"] == "tx-123"
    
    def test_payment_create_fiat_disabled(self):
        """Test fiat payment creation is disabled"""
        response = client.post("/api/payment/create", json={
            "payment_method": "fiat",
            "amount_usd": 10.0,
            "wallet_address": self.test_wallet_address
        })
        
        assert response.status_code == 400
        assert "Fiat payments not available" in response.json()["detail"]
    
    @patch('main.wallet_service.verify_transaction')
    def test_payment_verify_wallet(self, mock_verify):
        """Test wallet payment verification"""
        mock_verify.return_value = {
            "verified": True,
            "transaction_id": "tx-123",
            "amount": 10.0
        }
        
        response = client.post("/api/payment/verify", json={
            "tx_signature": "tx-123",
            "payment_method": "wallet"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["verified"] is True
    
    def test_payment_verify_fiat_disabled(self):
        """Test fiat payment verification is disabled"""
        response = client.post("/api/payment/verify", json={
            "tx_signature": "tx-123",
            "payment_method": "fiat"
        })
        
        assert response.status_code == 400
        assert "Fiat payment verification not available" in response.json()["detail"]
    
    @patch('main.wallet_service.get_sol_to_usd_rate')
    def test_payment_rates_endpoint(self, mock_rate):
        """Test payment rates endpoint"""
        mock_rate.return_value = 200.0
        
        # Use a fresh client instance without database setup
        from fastapi.testclient import TestClient
        test_client = TestClient(app)
        response = test_client.get("/api/payment/rates")
        
        assert response.status_code == 200
        data = response.json()
        print(f"Debug - Response data: {data}")  # Debug output
        assert "rates" in data
        assert data["rates"]["SOL_USD"] == 200.0
        assert "updated_at" in data["rates"]  # Check in rates, not in root
    
    @patch('main.wallet_service.get_walletconnect_config')
    def test_walletconnect_config_endpoint(self, mock_config):
        """Test WalletConnect configuration endpoint"""
        mock_config.return_value = {
            "project_id": "test-project-id",
            "supported_wallets": {
                "phantom": {"name": "Phantom", "icon": "phantom-icon.png"}
            }
        }
        
        response = client.get("/api/walletconnect/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data
        assert "supported_wallets" in data
    
    @patch('main.wallet_service.supported_tokens')
    def test_supported_tokens_endpoint(self, mock_tokens):
        """Test supported tokens endpoint"""
        mock_tokens = {
            "SOL": {"name": "Solana", "icon": "sol-icon.png"},
            "USDC": {"name": "USD Coin", "icon": "usdc-icon.png"}
        }
        
        with patch('main.wallet_service.supported_tokens', mock_tokens):
            response = client.get("/api/tokens/supported")
            
            assert response.status_code == 200
            data = response.json()
            assert "supported_tokens" in data
            assert "network" in data
            assert data["network"] == "solana"
    
    @patch('main.get_or_create_user')
    @patch('main.ConversationRepository')
    def test_conversation_history_endpoint(self, mock_repo_class, mock_user):
        """Test conversation history endpoint"""
        mock_user.return_value = (User(id=1, session_id="test-session"), "test-session", {"eligible": True, "type": "authenticated"})
        
        # Mock conversation repository
        mock_repo = AsyncMock()
        mock_repo.get_user_conversation_history.return_value = [
            Conversation(
                id=1,
                user_id=1,
                message_type="user",
                content="Hello",
                timestamp=None
            ),
            Conversation(
                id=2,
                user_id=1,
                message_type="assistant",
                content="Hi there!",
                timestamp=None
            )
        ]
        mock_repo_class.return_value = mock_repo
        
        response = client.get("/api/conversation/history")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["message_type"] == "user"
        assert data[0]["content"] == "Hello"
        assert data[1]["message_type"] == "assistant"
        assert data[1]["content"] == "Hi there!"

class TestAdminEndpoints:
    """Test admin-specific endpoints"""
    
    @patch('main.get_db')
    def test_admin_blacklist_get(self, mock_get_db):
        """Test getting blacklisted phrases"""
        # Mock database session
        mock_session = AsyncMock()
        mock_get_db.return_value = mock_session
        
        # Mock blacklisted phrases query
        mock_phrases = [
            BlacklistedPhrase(
                id=1,
                phrase="test phrase",
                original_message="original",
                successful_user_id=123,
                created_at="2024-01-01T10:00:00Z",
                is_active=True
            )
        ]
        mock_session.execute.return_value.scalars.return_value.all.return_value = mock_phrases
        
        response = client.get("/api/admin/blacklist")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["phrase"] == "test phrase"
    
    @patch('main.get_db')
    def test_admin_blacklist_post(self, mock_get_db):
        """Test adding blacklisted phrase"""
        mock_session = AsyncMock()
        mock_get_db.return_value = mock_session
        
        response = client.post("/api/admin/blacklist", json={
            "phrase": "new blacklisted phrase",
            "original_message": "original message",
            "successful_user_id": 123
        })
        
        assert response.status_code == 200
    
    @patch('main.get_db')
    def test_admin_stats(self, mock_get_db):
        """Test admin statistics endpoint"""
        mock_session = AsyncMock()
        mock_get_db.return_value = mock_session
        
        # Mock stats queries
        mock_session.execute.return_value.scalar.return_value = 100  # total users
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        
        response = client.get("/api/admin/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data

class TestbountyEndpoints:
    """Test bounty-related endpoints"""
    
    @patch('main.bounty_service.get_bounty_status')
    def test_bounty_status_endpoint(self, mock_status):
        """Test bounty status endpoint"""
        mock_status.return_value = {
            "current_pool": 5000,
            "total_entries": 100,
            "win_rate": 0.01,
            "next_rollover_at": "2024-01-01T12:00:00Z"
        }
        
        response = client.get("/api/bounty/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_pool"] == 5000
        assert data["total_entries"] == 100
        assert data["win_rate"] == 0.01
    
    @patch('main.get_db')
    def test_bounty_history_endpoint(self, mock_get_db):
        """Test bounty history endpoint"""
        mock_session = AsyncMock()
        mock_get_db.return_value = mock_session
        
        # Mock user history query
        mock_session.execute.return_value.scalar.return_value = 5  # total_entries
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        
        response = client.get("/api/bounty/history")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_entries" in data

def run_tests():
    """Run all web API tests"""
    print("🧪 Testing Web Interface API Endpoints")
    print("=" * 50)
    
    # Create test instance
    test_instance = TestWebAPI()
    test_instance.setup_method()
    
    # Get all test methods (only actual methods, not attributes)
    test_methods = [method for method in dir(test_instance) if method.startswith('test_') and callable(getattr(test_instance, method))]
    
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
    run_tests()
