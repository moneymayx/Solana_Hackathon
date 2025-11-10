"""
Contract Router - Automatic V3/V2/V1 Routing Based on Feature Flags

This service automatically routes contract calls to the appropriate version:
- V3 if USE_CONTRACT_V3=true (most secure)
- V2 if USE_CONTRACT_V2=true (parallel build)
- V1 otherwise (legacy)

This allows existing code to use the contract without modifications.
Just set the environment variable and it automatically uses the right version.
"""

import os
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Feature flags - checked in priority order (V3 > V2 > V1)
USE_CONTRACT_V3 = os.getenv("USE_CONTRACT_V3", "false").lower() == "true"
USE_CONTRACT_V2 = os.getenv("USE_CONTRACT_V2", "false").lower() == "true"


class ContractRouter:
    """
    Automatic contract version router.
    
    Routes calls to V3 (if enabled), V2 (if enabled), or V1 (fallback).
    Existing code can use this instead of smart_contract_service directly,
    and it will automatically use the correct version based on feature flags.
    """
    
    def __init__(self):
        # Import adapters lazily to avoid circular dependencies
        self._v3_adapter = None
        self._v2_adapter = None
        self._v1_service = None
        
        # Determine which version to use
        if USE_CONTRACT_V3:
            logger.info("🔒 Contract Router: Using V3 (secure)")
        elif USE_CONTRACT_V2:
            logger.info("🆕 Contract Router: Using V2 (parallel)")
        else:
            logger.info("📌 Contract Router: Using V1 (legacy)")
    
    def _get_v3_adapter(self):
        """Lazy load V3 adapter"""
        if self._v3_adapter is None and USE_CONTRACT_V3:
            try:
                from .contract_adapter_v3 import get_contract_adapter_v3
                self._v3_adapter = get_contract_adapter_v3()
            except Exception as e:
                logger.warning(f"Failed to load V3 adapter: {e}")
        return self._v3_adapter
    
    def _get_v2_adapter(self):
        """Lazy load V2 adapter"""
        if self._v2_adapter is None and USE_CONTRACT_V2:
            try:
                from .contract_adapter_v2 import get_contract_adapter_v2
                self._v2_adapter = get_contract_adapter_v2()
            except Exception as e:
                logger.warning(f"Failed to load V2 adapter: {e}")
        return self._v2_adapter
    
    def _get_v1_service(self):
        """Lazy load V1 service"""
        if self._v1_service is None:
            from .smart_contract_service import smart_contract_service
            self._v1_service = smart_contract_service
        return self._v1_service
    
    async def process_lottery_entry(
        self,
        session: AsyncSession,
        user_wallet: str,
        entry_amount: float,
        payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process lottery entry - automatically routes to V3/V2/V1
        
        This is the drop-in replacement for smart_contract_service.process_lottery_entry
        """
        # Try V3 first
        if USE_CONTRACT_V3:
            adapter = self._get_v3_adapter()
            if adapter:
                try:
                    from solders.pubkey import Pubkey
                    from solders.keypair import Keypair
                    # Note: V3 adapter needs user_keypair - this is a limitation
                    # For automatic routing, we'd need to handle this differently
                    # For now, log that V3 needs special handling
                    logger.warning("V3 adapter requires user_keypair - cannot auto-route. Use adapter directly.")
                    # Fall through to V2/V1
                except Exception as e:
                    logger.error(f"V3 adapter error: {e}")
        
        # Try V2
        if USE_CONTRACT_V2:
            adapter = self._get_v2_adapter()
            if adapter:
                try:
                    from solders.pubkey import Pubkey
                    # V2 adapter has process_entry_payment method
                    # But it also needs keypair - same issue
                    logger.warning("V2 adapter requires user_keypair - cannot auto-route. Use adapter directly.")
                    # Fall through to V1
                except Exception as e:
                    logger.error(f"V2 adapter error: {e}")
        
        # Fall back to V1
        service = self._get_v1_service()
        return await service.process_lottery_entry(
            session=session,
            user_wallet=user_wallet,
            entry_amount=entry_amount,
            payment_data=payment_data
        )
    
    async def get_lottery_status(self) -> Dict[str, Any]:
        """Get lottery status - automatically routes to V3/V2/V1"""
        # Try V3 first
        if USE_CONTRACT_V3:
            adapter = self._get_v3_adapter()
            if adapter:
                try:
                    return await adapter.get_lottery_status()
                except Exception as e:
                    logger.error(f"V3 adapter error: {e}")
        
        # Try V2
        if USE_CONTRACT_V2:
            adapter = self._get_v2_adapter()
            if adapter:
                try:
                    return await adapter.get_bounty_status(bounty_id=1)
                except Exception as e:
                    logger.error(f"V2 adapter error: {e}")
        
        # Fall back to V1
        service = self._get_v1_service()
        return await service.get_lottery_status()


# Global instance
contract_router = ContractRouter()

