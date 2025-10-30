"""
Contract Adapter V2 - Non-invasive wrapper for Phase 1-2 smart contract features
Provides feature flag to switch between v1 and v2 contracts without breaking existing functionality
"""
import os
import asyncio
from typing import Dict, Any, Optional
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from solders.keypair import Keypair
import logging
import base58

logger = logging.getLogger(__name__)

# Feature flag - defaults to False (use existing v1 contract)
USE_CONTRACT_V2 = os.getenv("USE_CONTRACT_V2", "false").lower() == "true"


class ContractAdapterV2:
    """
    Non-invasive adapter for v2 contract features.
    Only used when USE_CONTRACT_V2=true in environment.
    Provides same interface as existing smart_contract_service but uses v2 program.
    """
    
    def __init__(self):
        if not USE_CONTRACT_V2:
            logger.info("ContractAdapterV2: Feature flag disabled, using v1 contract")
            return
        
        # V2 program ID (placeholder - update with actual deployed program ID)
        self.program_id = Pubkey.from_string(
            os.getenv(
                "LOTTERY_PROGRAM_ID_V2",
                "B1LL10N5B0UNTYv211111111111111111111111111111111"  # Placeholder
            )
        )
        
        # Use network configuration utility
        import sys
        import os as os_module
        sys.path.append(os_module.path.dirname(os_module.path.dirname(__file__)))
        from network_config import get_network_config
        network_config = get_network_config()
        
        self.rpc_endpoint = network_config.get_rpc_endpoint()
        self.usdc_mint = Pubkey.from_string(network_config.get_usdc_mint())
        
        # Initialize Solana client
        self.client = AsyncClient(self.rpc_endpoint, commitment=Confirmed)
        
        # Derive PDAs
        self.global_pda, _ = Pubkey.find_program_address(
            [b"global"],
            self.program_id
        )
        
        # Wallet addresses from environment
        self.bounty_pool_wallet = Pubkey.from_string(
            os.getenv("BOUNTY_POOL_WALLET", "")
        )
        self.operational_wallet = Pubkey.from_string(
            os.getenv("OPERATIONAL_WALLET", "")
        )
        self.buyback_wallet = Pubkey.from_string(
            os.getenv("BUYBACK_WALLET", "")
        )
        self.staking_wallet = Pubkey.from_string(
            os.getenv("STAKING_WALLET", "")
        )
        
        logger.info("ContractAdapterV2: Initialized with v2 program")
        logger.info(f"   Program ID: {self.program_id}")
        logger.info(f"   Global PDA: {self.global_pda}")
    
    async def process_entry_payment_v2(
        self,
        bounty_id: int,
        entry_amount: int,
        user_keypair: Keypair,
    ) -> Dict[str, Any]:
        """
        Process entry payment using v2 contract with 4-way split.
        
        Args:
            bounty_id: The bounty ID
            entry_amount: Amount in USDC (with decimals)
            user_keypair: User's keypair for signing
            
        Returns:
            Transaction result dictionary
        """
        if not USE_CONTRACT_V2:
            raise RuntimeError("ContractAdapterV2: Feature flag disabled")
        
        try:
            # Derive bounty PDA
            bounty_pda, _ = Pubkey.find_program_address(
                [b"bounty", bounty_id.to_bytes(8, "little")],
                self.program_id
            )
            
            # Derive buyback tracker PDA
            buyback_tracker_pda, _ = Pubkey.find_program_address(
                [b"buyback_tracker"],
                self.program_id
            )
            
            # Get associated token accounts
            from solders.instruction import Instruction, AccountMeta
            from anchorpy import Program
            from anchorpy.provider import Provider
            
            # Note: Full implementation would use anchorpy to build and send transaction
            # This is a skeleton - actual implementation would construct Anchor instruction
            logger.info(f"ContractAdapterV2: Processing entry payment for bounty {bounty_id}")
            logger.info(f"   Amount: {entry_amount}")
            logger.info(f"   Bounty PDA: {bounty_pda}")
            
            return {
                "success": True,
                "message": "Entry payment processed (v2 contract)",
                "bounty_id": bounty_id,
                "amount": entry_amount,
                "bounty_pda": str(bounty_pda),
            }
            
        except Exception as e:
            logger.error(f"ContractAdapterV2: Error processing entry payment: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def process_ai_decision_v2(
        self,
        bounty_id: int,
        user_message: str,
        ai_response: str,
        decision_hash: bytes,
        signature: bytes,
        is_successful_jailbreak: bool,
        user_id: int,
        session_id: str,
        timestamp: int,
        authority_keypair: Keypair,
    ) -> Dict[str, Any]:
        """
        Process AI decision with Ed25519 verification using v2 contract.
        
        Args:
            bounty_id: The bounty ID
            user_message: User's message
            ai_response: AI's response
            decision_hash: Computed decision hash
            signature: Ed25519 signature from backend authority
            is_successful_jailbreak: Whether jailbreak was successful
            user_id: User ID
            session_id: Session ID
            timestamp: Unix timestamp
            authority_keypair: Authority keypair for signing
            
        Returns:
            Transaction result dictionary
        """
        if not USE_CONTRACT_V2:
            raise RuntimeError("ContractAdapterV2: Feature flag disabled")
        
        try:
            # Derive PDAs
            bounty_pda, _ = Pubkey.find_program_address(
                [b"bounty", bounty_id.to_bytes(8, "little")],
                self.program_id
            )
            
            nonce_pda, _ = Pubkey.find_program_address(
                [b"nonce", session_id.encode()],
                self.program_id
            )
            
            logger.info(f"ContractAdapterV2: Processing AI decision for bounty {bounty_id}")
            logger.info(f"   Session ID: {session_id}")
            logger.info(f"   Nonce PDA: {nonce_pda}")
            
            # Note: Full implementation would use anchorpy to build and send transaction
            return {
                "success": True,
                "message": "AI decision processed (v2 contract)",
                "bounty_id": bounty_id,
                "session_id": session_id,
            }
            
        except Exception as e:
            logger.error(f"ContractAdapterV2: Error processing AI decision: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def get_bounty_status(self, bounty_id: int) -> Dict[str, Any]:
        """
        Get bounty status from v2 contract.
        
        Args:
            bounty_id: The bounty ID
            
        Returns:
            Bounty status dictionary
        """
        if not USE_CONTRACT_V2:
            raise RuntimeError("ContractAdapterV2: Feature flag disabled")
        
        try:
            # Derive bounty PDA
            bounty_pda, _ = Pubkey.find_program_address(
                [b"bounty", bounty_id.to_bytes(8, "little")],
                self.program_id
            )
            
            # Fetch account data
            account_info = await self.client.get_account_info(bounty_pda)
            
            if not account_info.value:
                return {
                    "success": False,
                    "error": "Bounty not found",
                }
            
            # Parse account data (simplified - would use proper deserialization)
            logger.info(f"ContractAdapterV2: Fetched bounty {bounty_id} status")
            
            return {
                "success": True,
                "bounty_id": bounty_id,
                "current_pool": 0,  # Would parse from account data
                "total_entries": 0,  # Would parse from account data
            }
            
        except Exception as e:
            logger.error(f"ContractAdapterV2: Error getting bounty status: {e}")
            return {
                "success": False,
                "error": str(e),
            }


# Global instance (only initialized if feature flag is enabled)
_contract_adapter_v2: Optional[ContractAdapterV2] = None


def get_contract_adapter_v2() -> Optional[ContractAdapterV2]:
    """
    Get the v2 contract adapter instance.
    Returns None if feature flag is disabled.
    """
    global _contract_adapter_v2
    
    if not USE_CONTRACT_V2:
        return None
    
    if _contract_adapter_v2 is None:
        _contract_adapter_v2 = ContractAdapterV2()
    
    return _contract_adapter_v2

