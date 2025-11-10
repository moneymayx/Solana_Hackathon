"""
Integration tests for Kora SDK

These tests require:
1. Kora server running (kora rpc)
2. KORA_RPC_URL set to Kora server endpoint
3. Network access

Run with:
    python -m pytest tests/sdk/test_kora_integration.py -v
    ENABLE_KORA_SDK=true KORA_RPC_URL=http://localhost:8080 pytest tests/sdk/test_kora_integration.py -v
"""
import pytest
import os
import asyncio
from src.services.sdk.kora_service import KoraService


@pytest.fixture
def kora_service():
    """Create Kora service instance"""
    os.environ["ENABLE_KORA_SDK"] = "true"
    if not os.getenv("KORA_RPC_URL"):
        os.environ["KORA_RPC_URL"] = "http://localhost:8080"
    return KoraService()


@pytest.mark.asyncio
async def test_service_initialization(kora_service):
    """Test that service initializes correctly"""
    assert kora_service.is_enabled() is True
    assert kora_service.rpc_url is not None
    print(f"✅ Kora service initialized with URL: {kora_service.rpc_url}")


@pytest.mark.asyncio
async def test_get_config(kora_service):
    """Test getting Kora server configuration"""
    result = await kora_service.get_config()
    
    if not result.get("success"):
        pytest.skip(f"Kora server not available: {result.get('error')}")
    
    assert result["success"] is True
    assert "result" in result
    print(f"✅ Got Kora config: {result.get('result')}")


@pytest.mark.asyncio
async def test_get_supported_tokens(kora_service):
    """Test getting supported fee tokens"""
    result = await kora_service.get_supported_tokens()
    
    if not result.get("success"):
        pytest.skip(f"Kora server not available: {result.get('error')}")
    
    assert result["success"] is True
    print(f"✅ Supported tokens: {result.get('result')}")


@pytest.mark.skip(reason="Requires actual transaction to test")
@pytest.mark.asyncio
async def test_estimate_transaction_fee(kora_service):
    """
    Test estimating transaction fee
    
    ⚠️  To enable this test:
    1. Build a sample transaction (base64)
    2. Set SAMPLE_TRANSACTION_BASE64 environment variable
    3. Remove @pytest.mark.skip decorator
    """
    sample_transaction = os.getenv("SAMPLE_TRANSACTION_BASE64")
    
    if not sample_transaction:
        pytest.skip("SAMPLE_TRANSACTION_BASE64 not set")
    
    result = await kora_service.estimate_transaction_fee(
        transaction_base64=sample_transaction,
        fee_token="USDC"
    )
    
    assert result["success"] is True
    print(f"✅ Fee estimate: {result.get('result')}")


@pytest.mark.skip(reason="Requires actual transaction to test")
@pytest.mark.asyncio
async def test_sign_transaction(kora_service):
    """
    Test signing a transaction with Kora
    
    ⚠️  To enable this test:
    1. Build a sample transaction (base64)
    2. Set SAMPLE_TRANSACTION_BASE64 environment variable
    3. Remove @pytest.mark.skip decorator
    """
    sample_transaction = os.getenv("SAMPLE_TRANSACTION_BASE64")
    
    if not sample_transaction:
        pytest.skip("SAMPLE_TRANSACTION_BASE64 not set")
    
    result = await kora_service.sign_transaction(
        transaction_base64=sample_transaction
    )
    
    assert result["success"] is True
    print(f"✅ Transaction signed: {result.get('result')}")


@pytest.mark.asyncio
async def test_connection_error_handling(kora_service):
    """Test error handling when Kora server is not available"""
    # Temporarily set invalid URL
    original_url = kora_service.rpc_url
    kora_service.rpc_url = "http://localhost:9999"
    
    try:
        result = await kora_service.get_config()
        # Should handle error gracefully
        if not result.get("success"):
            assert "error" in result
            print(f"✅ Correctly handled connection error: {result['error']}")
    finally:
        kora_service.rpc_url = original_url


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])

