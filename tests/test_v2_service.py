#!/usr/bin/env python3
"""
Unit Tests for V2 Contract Service

Tests the backend's v2 contract service layer.
Run with: pytest tests/test_v2_service.py -v
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.v2.contract_service import ContractServiceV2


# Test configuration
PROGRAM_ID = "GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm"
GLOBAL_PDA = "F4YATUC3tEA3Gb3Tt3v7sZBT9iKRhHXJsZ6s7nBWKDgh"
BOUNTY_1_PDA = "AJC6D2mvMcktdzpJJQmbYXkTZn9xGpd2C3qm4VAZK83Z"
RPC_URL = os.getenv("SOLANA_RPC_ENDPOINT", "https://api.devnet.solana.com")


@pytest.fixture
def service():
    """Create a v2 contract service instance."""
    return ContractServiceV2(rpc_endpoint=RPC_URL, program_id=PROGRAM_ID)


@pytest.mark.asyncio
async def test_service_initialization(service):
    """Test that service initializes correctly."""
    assert service is not None
    assert service.program_id is not None
    assert service.rpc_endpoint == RPC_URL
    assert service.client is not None


@pytest.mark.asyncio
async def test_get_bounty_status_existing(service):
    """Test fetching status of an existing bounty."""
    result = await service.get_bounty_status(1)
    
    # Should succeed since bounty 1 is initialized
    assert result["success"] is True
    assert result["bounty_id"] == 1


@pytest.mark.asyncio
async def test_get_bounty_status_nonexistent(service):
    """Test fetching status of a non-existent bounty."""
    result = await service.get_bounty_status(999)
    
    # Should fail since bounty 999 doesn't exist
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_multiple_concurrent_requests(service):
    """Test that service handles concurrent requests."""
    tasks = [
        service.get_bounty_status(1),
        service.get_bounty_status(1),
        service.get_bounty_status(1),
    ]
    
    results = await asyncio.gather(*tasks)
    
    # All should succeed
    assert all(r["success"] for r in results)
    assert all(r["bounty_id"] == 1 for r in results)


def test_sync_wrapper():
    """Test synchronous wrapper for async service methods."""
    service = ContractServiceV2(rpc_endpoint=RPC_URL, program_id=PROGRAM_ID)
    
    # Run async method in sync context
    result = asyncio.run(service.get_bounty_status(1))
    
    assert result["success"] is True


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])



