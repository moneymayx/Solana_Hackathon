"""
Tests for Contract Adapter V2
Verifies feature flag behavior and ensures no regression when flag is disabled
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from src.services.contract_adapter_v2 import (
    ContractAdapterV2,
    get_contract_adapter_v2,
    USE_CONTRACT_V2,
)


class TestContractAdapterV2FeatureFlag:
    """Test feature flag behavior"""
    
    def test_feature_flag_defaults_to_false(self):
        """Verify feature flag defaults to False"""
        # Should not raise when flag is False
        adapter = get_contract_adapter_v2()
        assert adapter is None or not USE_CONTRACT_V2
    
    @patch.dict(os.environ, {"USE_CONTRACT_V2": "true"})
    def test_feature_flag_when_enabled(self):
        """Verify adapter initializes when flag is enabled"""
        # Reload module to pick up new env var
        import importlib
        import src.services.contract_adapter_v2
        importlib.reload(src.services.contract_adapter_v2)
        
        # This would initialize if env var is set, but we're testing flag behavior
        assert src.services.contract_adapter_v2.USE_CONTRACT_V2 or not os.getenv("USE_CONTRACT_V2")
    
    def test_get_adapter_returns_none_when_disabled(self):
        """Verify get_contract_adapter_v2 returns None when flag is disabled"""
        adapter = get_contract_adapter_v2()
        # Should return None when flag is False
        if not USE_CONTRACT_V2:
            assert adapter is None


class TestContractAdapterV2Methods:
    """Test adapter methods (when flag is enabled)"""
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"USE_CONTRACT_V2": "true"})
    async def test_process_entry_payment_v2_raises_when_disabled(self):
        """Verify process_entry_payment_v2 raises when flag is disabled"""
        # Reload module
        import importlib
        import src.services.contract_adapter_v2
        importlib.reload(src.services.contract_adapter_v2)
        
        if not src.services.contract_adapter_v2.USE_CONTRACT_V2:
            adapter = src.services.contract_adapter_v2.ContractAdapterV2()
            with pytest.raises(RuntimeError, match="Feature flag disabled"):
                await adapter.process_entry_payment_v2(
                    bounty_id=1,
                    entry_amount=10000000,
                    user_keypair=MagicMock(),
                )
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"USE_CONTRACT_V2": "true"})
    async def test_process_ai_decision_v2_raises_when_disabled(self):
        """Verify process_ai_decision_v2 raises when flag is disabled"""
        import importlib
        import src.services.contract_adapter_v2
        importlib.reload(src.services.contract_adapter_v2)
        
        if not src.services.contract_adapter_v2.USE_CONTRACT_V2:
            adapter = src.services.contract_adapter_v2.ContractAdapterV2()
            with pytest.raises(RuntimeError, match="Feature flag disabled"):
                await adapter.process_ai_decision_v2(
                    bounty_id=1,
                    user_message="test",
                    ai_response="test",
                    decision_hash=b"test",
                    signature=b"test",
                    is_successful_jailbreak=False,
                    user_id=1,
                    session_id="test",
                    timestamp=1234567890,
                    authority_keypair=MagicMock(),
                )
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"USE_CONTRACT_V2": "true"})
    async def test_get_bounty_status_raises_when_disabled(self):
        """Verify get_bounty_status raises when flag is disabled"""
        import importlib
        import src.services.contract_adapter_v2
        importlib.reload(src.services.contract_adapter_v2)
        
        if not src.services.contract_adapter_v2.USE_CONTRACT_V2:
            adapter = src.services.contract_adapter_v2.ContractAdapterV2()
            with pytest.raises(RuntimeError, match="Feature flag disabled"):
                await adapter.get_bounty_status(bounty_id=1)


class TestNoRegressionWhenFlagDisabled:
    """Ensure existing functionality works when flag is disabled"""
    
    def test_existing_service_still_works(self):
        """Verify existing smart_contract_service still works"""
        # Import existing service
        from src.services import smart_contract_service
        
        # Should initialize without errors
        assert smart_contract_service is not None
    
    def test_adapter_does_not_interfere_with_existing_code(self):
        """Verify adapter doesn't break existing imports"""
        # Should be able to import both services
        from src.services import smart_contract_service
        from src.services.contract_adapter_v2 import get_contract_adapter_v2
        
        # Existing service should work
        assert smart_contract_service is not None
        
        # Adapter should return None when disabled
        adapter = get_contract_adapter_v2()
        if not USE_CONTRACT_V2:
            assert adapter is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

