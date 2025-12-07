"""
AI Decision Integration Service - Integrates backend AI decisions with smart contract
"""
import asyncio
import json
from typing import Dict, Any, Optional
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.transaction import Transaction
from solders.pubkey import Pubkey as PublicKey
from solders.keypair import Keypair
from anchorpy import Program, Provider
from anchorpy.provider import Wallet
from .ai_decision_service import ai_decision_service
from .smart_contract_service import SmartContractService
from .contract_adapter_v3 import get_contract_adapter_v3
import logging

logger = logging.getLogger(__name__)

class AIDecisionIntegration:
    """Service for integrating AI decisions with smart contract"""
    
    def __init__(self):
        self.smart_contract_service = SmartContractService()
        self.program_id = self.smart_contract_service.program_id
        # Get RPC endpoint - handle both V1/V2 (has rpc_endpoint) and V3 adapter (has client with rpc_endpoint)
        if hasattr(self.smart_contract_service, 'rpc_endpoint'):
            self.rpc_endpoint = self.smart_contract_service.rpc_endpoint
        elif hasattr(self.smart_contract_service, '_v3_adapter') and self.smart_contract_service._v3_adapter:
            self.rpc_endpoint = self.smart_contract_service._v3_adapter.rpc_endpoint
        else:
            # Fallback to environment variable
            from network_config import get_network_config
            network_config = get_network_config()
            self.rpc_endpoint = network_config.get_rpc_endpoint()
        
        # Get client - handle both V1/V2 (has client) and V3 adapter (has client)
        if hasattr(self.smart_contract_service, 'client'):
            self.client = self.smart_contract_service.client
        elif hasattr(self.smart_contract_service, '_v3_adapter') and self.smart_contract_service._v3_adapter:
            self.client = self.smart_contract_service._v3_adapter.client
        else:
            # Fallback: create client from rpc_endpoint
            from solana.rpc.async_api import AsyncClient
            from solana.rpc.commitment import Confirmed
            self.client = AsyncClient(self.rpc_endpoint, commitment=Confirmed)
        
    async def process_ai_decision_on_chain(
        self, 
        signed_decision: Dict[str, Any],
        winner_wallet_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process AI decision on-chain with full verification"""
        
        try:
            decision_data = signed_decision["decision_data"]
            
            # Extract decision components
            user_message = decision_data["user_message"]
            ai_response = decision_data["ai_response"]
            is_successful_jailbreak = decision_data["is_successful_jailbreak"]
            user_id = decision_data["user_id"]
            session_id = decision_data["session_id"]
            timestamp = decision_data["timestamp"]
            
            # Get decision hash and signature
            decision_hash = bytes.fromhex(signed_decision["decision_hash"])
            signature = bytes.fromhex(signed_decision["signature"])
            
            # If successful jailbreak, we need a winner wallet
            if is_successful_jailbreak and not winner_wallet_address:
                return {
                    "success": False,
                    "error": "Winner wallet address required for successful jailbreak"
                }
            
            # Create the smart contract call
            result = await self._call_smart_contract(
                user_message=user_message,
                ai_response=ai_response,
                decision_hash=decision_hash,
                signature=signature,
                is_successful_jailbreak=is_successful_jailbreak,
                user_id=user_id,
                session_id=session_id,
                timestamp=timestamp,
                winner_wallet_address=winner_wallet_address
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process AI decision on-chain: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_ai_decision_on_chain_v3(
        self,
        signed_decision: Dict[str, Any],
        winner_wallet_address: Optional[str] = None,
        conversation_history: Optional[list[Dict[str, Any]]] = None,
        model_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process an AI decision using the new V3 on-chain decision flow.

        This is a parallel, non-breaking path that:
          - Builds an AIDecisionPayload-compatible dict via AIDecisionService.
          - Signs the payload with the AI decision key.
          - For now, submits it to the V3 contract adapter's stubbed
            `submit_ai_decision_v3` helper, which can later be wired to actual
            Anchor transactions on devnet.
        """
        try:
            adapter = get_contract_adapter_v3()
            if adapter is None:
                return {
                    "success": False,
                    "error": "V3 contract adapter is not enabled (USE_CONTRACT_V3 is false)",
                }

            decision_data = signed_decision["decision_data"]

            user_message = decision_data["user_message"]
            ai_response = decision_data["ai_response"]
            is_successful_jailbreak = decision_data["is_successful_jailbreak"]
            user_id = decision_data["user_id"]
            session_id = decision_data["session_id"]
            timestamp = decision_data["timestamp"]

            # Build the contract-friendly payload and AI signature.
            v3_payload = ai_decision_service.build_v3_payload(
                user_message=user_message,
                ai_response=ai_response,
                is_successful_jailbreak=is_successful_jailbreak,
                user_id=user_id,
                session_id=session_id,
                conversation_history=conversation_history,
                model_id=model_id,
                timestamp=timestamp,
            )

            ai_signature: bytes = v3_payload.pop("ai_signature")
            _ai_public_key: bytes = v3_payload.pop("ai_public_key")

            # Winner wallet is only required for successful jailbreaks; the
            # adapter helper treats it as optional for now.
            from solders.pubkey import Pubkey as PublicKey

            winner_wallet = None
            if winner_wallet_address:
                winner_wallet = PublicKey.from_string(winner_wallet_address)

            result = await adapter.submit_ai_decision_v3(
                payload=v3_payload,
                ai_signature=ai_signature,
                winner_wallet=winner_wallet,
            )

            return result

        except Exception as e:
            logger.error(f"Failed to process AI decision on-chain via V3 flow: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def _call_smart_contract(
        self,
        user_message: str,
        ai_response: str,
        decision_hash: bytes,
        signature: bytes,
        is_successful_jailbreak: bool,
        user_id: int,
        session_id: str,
        timestamp: int,
        winner_wallet_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call the smart contract to process the AI decision"""
        
        try:
            # Get lottery PDA
            lottery_pda, lottery_bump = PublicKey.find_program_address(
                [b"lottery"],
                self.program_id
            )
            
            # Get backend authority (this would be your backend's public key)
            backend_authority = PublicKey.from_string(
                os.getenv("BACKEND_AUTHORITY_PUBLIC_KEY", "11111111111111111111111111111111")
            )
            
            # Get winner wallet if provided
            winner_wallet = None
            if winner_wallet_address:
                winner_wallet = PublicKey.from_string(winner_wallet_address)
            
            # Get USDC mint
            usdc_mint = self.smart_contract_service.usdc_mint
            
            # Get token accounts
            jackpot_token_account, _ = PublicKey.find_program_address(
                [usdc_mint.to_bytes(), lottery_pda.to_bytes()],
                PublicKey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
            )
            
            winner_token_account = None
            if winner_wallet:
                winner_token_account, _ = PublicKey.find_program_address(
                    [usdc_mint.to_bytes(), winner_wallet.to_bytes()],
                    PublicKey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
                )
            
            # Create transaction
            transaction = Transaction()
            
            # Add the process_ai_decision instruction
            # Note: This would need to be implemented with the actual Anchor program
            # For now, we'll simulate the call
            
            # In a real implementation, you would:
            # 1. Load the Anchor program
            # 2. Call the process_ai_decision method
            # 3. Send the transaction
            
            # For now, return a simulated result
            return {
                "success": True,
                "transaction_signature": "simulated_tx_signature",
                "message": "AI decision processed on-chain",
                "decision_logged": True,
                "winner_paid": is_successful_jailbreak and winner_wallet is not None
            }
            
        except Exception as e:
            logger.error(f"Smart contract call failed: {e}")
            return {
                "success": False,
                "error": f"Smart contract call failed: {str(e)}"
            }
    
    async def verify_decision_integrity(self, signed_decision: Dict[str, Any]) -> bool:
        """Verify the integrity of a signed decision"""
        try:
            return ai_decision_service.verify_decision(signed_decision)
        except Exception as e:
            logger.error(f"Decision verification failed: {e}")
            return False
    
    async def get_decision_summary(self, signed_decision: Dict[str, Any]) -> str:
        """Get a summary of the AI decision"""
        return ai_decision_service.get_decision_summary(signed_decision)
    
    async def log_decision_to_database(
        self, 
        session, 
        signed_decision: Dict[str, Any],
        on_chain_result: Dict[str, Any]
    ) -> None:
        """Log the decision to database for audit trail"""
        try:
            decision_data = signed_decision["decision_data"]
            
            # Create audit log entry
            from ..models import SecurityEvent
            audit_event = SecurityEvent(
                event_type="ai_decision_processed",
                severity="medium",
                description=f"AI decision processed for user {decision_data['user_id']}",
                session_id=decision_data["session_id"],
                additional_data=json.dumps({
                    "signed_decision": signed_decision,
                    "on_chain_result": on_chain_result,
                    "decision_hash": signed_decision["decision_hash"]
                })
            )
            
            session.add(audit_event)
            await session.commit()
            
            logger.info(f"Decision logged to database for user {decision_data['user_id']}")
            
        except Exception as e:
            logger.error(f"Failed to log decision to database: {e}")

# Global instance
ai_decision_integration = AIDecisionIntegration()
