"""
Integration tests for Attestations SDK

These tests require:
1. SAS program ID to be set in environment variables
2. A known wallet with attestations for testing
3. Network access to Solana RPC

Run with:
    python -m pytest tests/sdk/test_attestations_integration.py -v
    ENABLE_ATTESTATIONS_SDK=true pytest tests/sdk/test_attestations_integration.py -v
"""
import pytest
import os
import asyncio
from src.services.sdk.attestations_service import AttestationsService


@pytest.fixture
def attestations_service():
    """Create attestations service instance"""
    os.environ["ENABLE_ATTESTATIONS_SDK"] = "true"
    return AttestationsService()


@pytest.mark.asyncio
async def test_service_initialization(attestations_service):
    """Test that service initializes correctly"""
    assert attestations_service.is_enabled() is True
    
    # Check if program ID is set (not placeholder)
    program_id_str = str(attestations_service.program_id)
    assert program_id_str != "SASProgram111111111111111111111111111111"
    assert program_id_str != "11111111111111111111111111111111"
    print(f"✅ Using SAS Program ID: {program_id_str}")


@pytest.mark.asyncio
async def test_pda_derivation(attestations_service):
    """Test PDA derivation for attestation accounts"""
    from solana.publickey import Pubkey
    
    # Use a known test wallet
    test_wallet = Pubkey.from_string("11111111111111111111111111111111")
    
    # Derive PDA
    pda = attestations_service._derive_attestation_pda(
        wallet=test_wallet
    )
    
    assert pda is not None
    print(f"✅ Derived PDA: {pda}")


@pytest.mark.asyncio
async def test_query_nonexistent_attestation(attestations_service):
    """Test querying for a wallet without attestations"""
    # Use a wallet that likely doesn't have attestations
    test_wallet = "11111111111111111111111111111111"
    
    result = await attestations_service.verify_kyc_attestation(test_wallet)
    
    assert result["success"] is True
    assert result["kyc_verified"] is False
    print(f"✅ Correctly identified wallet without attestation")


@pytest.mark.skip(reason="Requires known wallet with attestation")
@pytest.mark.asyncio
async def test_query_existing_attestation(attestations_service):
    """
    Test querying for a wallet WITH attestations
    
    ⚠️  To enable this test:
    1. Find a wallet with a known KYC attestation
    2. Set WALLET_WITH_ATTESTATION environment variable
    3. Remove @pytest.mark.skip decorator
    """
    wallet_with_attestation = os.getenv(
        "WALLET_WITH_ATTESTATION",
        "your_wallet_with_attestation_here"
    )
    
    if wallet_with_attestation == "your_wallet_with_attestation_here":
        pytest.skip("WALLET_WITH_ATTESTATION not set")
    
    result = await attestations_service.verify_kyc_attestation(wallet_with_attestation)
    
    assert result["success"] is True
    assert result["kyc_verified"] is True
    print(f"✅ Found attestation for wallet: {wallet_with_attestation}")
    print(f"   Account: {result.get('attestation_account')}")
    print(f"   Parsed data: {result.get('parsed_data')}")


@pytest.mark.asyncio
async def test_account_data_parsing(attestations_service):
    """Test account data parsing with sample data"""
    # Sample base64 data (this is just a test structure)
    sample_data = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    
    parsed = attestations_service._parse_attestation_account_data(sample_data)
    
    assert "raw_data_length" in parsed
    print(f"✅ Parsed account data structure: {parsed}")


@pytest.mark.asyncio
async def test_invalid_wallet_address(attestations_service):
    """Test error handling for invalid wallet addresses"""
    result = await attestations_service.verify_kyc_attestation("invalid_address")
    
    assert result["success"] is False
    assert "error" in result
    print(f"✅ Correctly handled invalid address: {result['error']}")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])

