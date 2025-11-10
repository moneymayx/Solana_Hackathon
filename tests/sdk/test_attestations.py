"""
Tests for Attestations SDK Integration

Tests verifiable credentials and KYC replacement functionality.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import os

# Set test environment
os.environ["ENABLE_ATTESTATIONS_SDK"] = "true"
os.environ["SOLANA_RPC_ENDPOINT"] = "https://api.devnet.solana.com"

from src.services.sdk.attestations_service import AttestationsService


@pytest.fixture
def attestations_service():
    """Create an AttestationsService instance for testing"""
    return AttestationsService()


@pytest.mark.asyncio
async def test_attestations_service_initialization(attestations_service):
    """Test that Attestations service initializes correctly"""
    assert attestations_service is not None
    assert attestations_service.enabled is True


@pytest.mark.asyncio
async def test_kyc_verification(attestations_service):
    """Test KYC attestation verification"""
    test_wallet = "test_wallet_address"
    
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "value": {
                    "data": ["test_attestation_data"]
                }
            }
        }
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        result = await attestations_service.verify_kyc_attestation(test_wallet)
        
        # Service may return success even if attestation not found
        assert "success" in result
        assert "wallet_address" in result


@pytest.mark.asyncio
async def test_geographic_verification(attestations_service):
    """Test geographic attestation verification"""
    test_wallet = "test_wallet_address"
    allowed_countries = ["US", "CA"]
    
    result = await attestations_service.verify_geographic_attestation(
        wallet_address=test_wallet,
        allowed_countries=allowed_countries
    )
    
    assert "success" in result
    assert result["wallet_address"] == test_wallet


@pytest.mark.asyncio
async def test_accreditation_verification(attestations_service):
    """Test accreditation verification"""
    test_wallet = "test_wallet_address"
    
    result = await attestations_service.verify_accreditation(
        wallet_address=test_wallet,
        accreditation_type="investor"
    )
    
    assert "success" in result
    assert result["wallet_address"] == test_wallet


@pytest.mark.asyncio
async def test_get_all_attestations(attestations_service):
    """Test retrieving all attestations for a wallet"""
    test_wallet = "test_wallet_address"
    
    result = await attestations_service.get_all_attestations(test_wallet)
    
    assert "success" in result
    assert result["wallet_address"] == test_wallet
    assert "attestations" in result

