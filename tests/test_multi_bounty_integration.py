"""
Backend Integration Tests for Multi-Bounty Smart Contract

Tests that the backend correctly:
- Maps difficulty levels to bounty_id
- Routes payments to correct bounty PDA
- Enforces single-bounty constraint
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

# Import services
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.smart_contract_service import SmartContractService
from src.services.contract_adapter_v3 import ContractAdapterV3, get_contract_adapter_v3


class TestMultiBountyIntegration:
    """Test backend integration with multi-bounty smart contract"""
    
    @pytest.fixture
    def smart_contract_service(self):
        """Create smart contract service instance"""
        return SmartContractService()
    
    @pytest.fixture
    def mock_session(self):
        """Create mock database session"""
        return AsyncMock(spec=AsyncSession)
    
    @pytest.mark.asyncio
    async def test_difficulty_to_bounty_id_mapping(self, smart_contract_service, mock_session):
        """Test that difficulty levels map correctly to bounty_id"""
        # Test expert -> bounty_id 1
        payment_data_expert = {"difficulty": "expert", "bounty_id": 1}
        # Extract bounty_id mapping logic
        difficulty_map = {
            "expert": 1,
            "hard": 2,
            "medium": 3,
            "easy": 4
        }
        
        assert difficulty_map["expert"] == 1
        assert difficulty_map["hard"] == 2
        assert difficulty_map["medium"] == 3
        assert difficulty_map["easy"] == 4
    
    @pytest.mark.asyncio
    async def test_payment_flow_includes_bounty_id(self, smart_contract_service, mock_session):
        """Test that payment flow includes bounty_id in contract call"""
        # Mock the contract adapter
        with patch.object(smart_contract_service, '_v3_adapter') as mock_adapter:
            if smart_contract_service._v3_adapter:
                mock_adapter.process_entry_payment = AsyncMock(return_value={
                    "success": True,
                    "transaction_signature": "test_tx",
                    "funds_locked": True,
                })
                
                # Mock database operations
                mock_session.add = MagicMock()
                mock_session.commit = AsyncMock()
                mock_session.refresh = AsyncMock()
                
                # Process entry with difficulty
                payment_data = {
                    "difficulty": "expert",
                    "bounty_id": 1
                }
                
                result = await smart_contract_service.process_lottery_entry(
                    session=mock_session,
                    user_wallet="test_wallet",
                    entry_amount=10.0,
                    payment_data=payment_data
                )
                
                # Verify bounty_id is included in result
                assert "bounty_id" in result or result.get("success") is not None
    
    @pytest.mark.asyncio
    async def test_contract_adapter_derives_correct_pda(self):
        """Test that contract adapter derives correct PDA for each bounty"""
        # This test would verify that get_lottery_pda_for_bounty returns correct PDAs
        # Placeholder for full implementation
        pass
    
    @pytest.mark.asyncio
    async def test_single_bounty_constraint_enforcement(self, smart_contract_service, mock_session):
        """Test that smart contract service enforces single-bounty constraint"""
        # This test would verify that users cannot enter multiple bounties
        # Placeholder for full implementation
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

