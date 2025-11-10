"""
Tests for Kora SDK Integration

Tests fee abstraction and sponsored transaction functionality.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import os

# Set test environment
os.environ["ENABLE_KORA_SDK"] = "true"
os.environ["KORA_API_KEY"] = "test_key"
os.environ["KORA_BASE_URL"] = "https://api.test.kora.so"

from src.services.sdk.kora_service import KoraService


@pytest.fixture
def kora_service():
    """Create a KoraService instance for testing"""
    return KoraService()


@pytest.mark.asyncio
async def test_kora_service_initialization(kora_service):
    """Test that Kora service initializes correctly"""
    assert kora_service is not None
    assert kora_service.enabled is True


@pytest.mark.asyncio
async def test_sponsored_transaction_creation(kora_service):
    """Test creating a sponsored transaction"""
    # Mock transaction bytes
    test_transaction = b"test_transaction_bytes"
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "transaction": "sponsored_tx_hex",
            "fee_token": "USDC"
        }
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        result = await kora_service.create_sponsored_transaction(
            transaction=test_transaction,
            fee_token="USDC"
        )
        
        assert result["success"] is True
        assert result["fee_token"] == "USDC"


@pytest.mark.asyncio
async def test_fee_estimation(kora_service):
    """Test fee estimation functionality"""
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "fee_amount": "0.001",
            "estimated_usd": "0.01"
        }
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        result = await kora_service.estimate_fee_cost(
            transaction_size=512,
            fee_token="USDC"
        )
        
        assert result["success"] is True
        assert "fee_amount" in result


def test_supported_tokens(kora_service):
    """Test checking supported tokens for fee payment"""
    assert kora_service.can_pay_fees_in_token("USDC") is True
    assert kora_service.can_pay_fees_in_token("USDT") is True
    assert kora_service.can_pay_fees_in_token("SOL") is True
    assert kora_service.can_pay_fees_in_token("BTC") is False


@pytest.mark.asyncio
async def test_signing_rpc_retrieval(kora_service):
    """Test getting custom signing RPC endpoint"""
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "rpc_endpoint": "https://rpc.test.kora.so",
            "signing_method": "custom"
        }
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )
        
        result = await kora_service.get_signing_rpc(
            wallet_address="test_wallet",
            network="devnet"
        )
        
        assert result["success"] is True
        assert "rpc_endpoint" in result

