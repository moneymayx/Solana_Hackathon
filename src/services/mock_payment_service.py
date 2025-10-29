"""
Mock Payment Service - For testing without real blockchain transactions
This simulates the payment flow and grants free questions without charging users
"""
import logging
import secrets
import asyncio
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

logger = logging.getLogger(__name__)

class MockPaymentService:
    """
    Mock payment service for testing
    Simulates payment flow without actual blockchain transactions
    """
    
    def __init__(self):
        self.usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC mainnet
        self.mock_recipient = "MockTreasury1111111111111111111111111111111"
        logger.info("🧪 Mock Payment Service initialized - NO REAL TRANSACTIONS")
    
    async def create_mock_transaction(
        self,
        session: AsyncSession,
        wallet_address: str,
        amount_usd: float
    ) -> Dict[str, Any]:
        """
        Create a mock transaction that looks real but doesn't execute on chain
        Returns transaction details for frontend to "sign"
        """
        try:
            logger.info(f"🧪 Creating MOCK transaction: ${amount_usd} for {wallet_address}")
            
            # Convert USD to USDC units (6 decimals)
            amount_units = int(amount_usd * 1_000_000)
            
            # Generate mock ATAs (these look real but won't be used)
            # For test wallets, use dummy addresses
            if wallet_address.startswith("Test"):
                from_ata = "TestSourceATA1111111111111111111111111111"
                to_ata = "TestDestinationATA111111111111111111111111"
            else:
                from solders.pubkey import Pubkey as SoldersPubkey
                from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID
                
                user_pubkey = SoldersPubkey.from_string(wallet_address)
                mint_pubkey = SoldersPubkey.from_string(self.usdc_mint)
                recipient_pubkey = SoldersPubkey.from_string(self.mock_recipient)
                
                # Calculate mock ATAs
                from_ata = str(SoldersPubkey.find_program_address(
                    [bytes(user_pubkey), bytes(TOKEN_PROGRAM_ID), bytes(mint_pubkey)],
                    ASSOCIATED_TOKEN_PROGRAM_ID
                )[0])
                
                to_ata = str(SoldersPubkey.find_program_address(
                    [bytes(recipient_pubkey), bytes(TOKEN_PROGRAM_ID), bytes(mint_pubkey)],
                    ASSOCIATED_TOKEN_PROGRAM_ID
                )[0])
            
            # Add warning that this is a test
            warning = f"🧪 TEST MODE: This is a simulated payment. No real funds will be transferred. You'll receive free questions for testing."
            
            return {
                "success": True,
                "transaction": {
                    "recipient": self.mock_recipient,
                    "mint": self.usdc_mint,
                    "from_ata": from_ata,
                    "to_ata": to_ata,
                    "units": amount_units,
                    "amount_usd": amount_usd
                },
                "warning": warning,
                "message": "Mock transaction details ready (TEST MODE)",
                "is_mock": True
            }
            
        except Exception as e:
            logger.error(f"Error creating mock transaction: {e}")
            return {
                "success": False,
                "error": str(e),
                "is_mock": True
            }
    
    async def verify_mock_transaction(
        self,
        session: AsyncSession,
        wallet_address: str,
        transaction_signature: str,
        amount_usd: float,
        trigger_smart_contract: bool = True
    ) -> Dict[str, Any]:
        """
        Mock verify a transaction, grant free questions, and optionally trigger devnet smart contracts
        This simulates verification but DOES call real devnet smart contracts for testing
        """
        try:
            logger.info(f"🧪 MOCK verifying transaction: {transaction_signature}")
            
            # Simulate async verification delay (like real blockchain)
            await asyncio.sleep(0.5)
            
            # Calculate number of free questions to grant based on payment
            # IMPORTANT: This uses a fixed $10 per question for simplicity
            # In production, this should be calculated based on bounty difficulty
            COST_PER_QUESTION = 10.0
            questions_to_grant = int(amount_usd / COST_PER_QUESTION)  # Floor division
            credit_remainder = amount_usd % COST_PER_QUESTION  # Remaining credit
            
            logger.info(f"🧪 MOCK PAYMENT SUCCESS: ${amount_usd} → {questions_to_grant} questions + ${credit_remainder:.2f} credit")
            
            result = {
                "success": True,
                "verified": True,
                "transaction_signature": transaction_signature,
                "wallet_address": wallet_address,
                "amount_usd": amount_usd,
                "questions_granted": questions_to_grant,
                "credit_remainder": credit_remainder,
                "is_mock": True,
                "message": f"🧪 TEST: Granted {questions_to_grant} questions" + (f" + ${credit_remainder:.2f} credit" if credit_remainder > 0 else " (no real payment made)")
            }
            
            # Optionally trigger devnet smart contract
            if trigger_smart_contract:
                logger.info(f"🔗 Triggering DEVNET smart contract for mock payment")
                
                try:
                    # Import smart contract service
                    from .smart_contract_service import smart_contract_service
                    
                    # Process lottery entry on devnet smart contract
                    # This WILL execute on devnet but uses mock payment signature
                    contract_result = await smart_contract_service.process_lottery_entry(
                        session=session,
                        user_wallet=wallet_address,
                        entry_amount=amount_usd,
                        payment_data={
                            "source": "mock_payment",
                            "type": "lottery_entry",
                            "mock_signature": transaction_signature,
                            "is_test": True
                        }
                    )
                    
                    if contract_result["success"]:
                        logger.info(f"✅ Devnet smart contract executed: {contract_result.get('transaction_signature', 'N/A')}")
                        result["smart_contract_executed"] = True
                        result["smart_contract_tx"] = contract_result.get("transaction_signature")
                        result["funds_locked"] = contract_result.get("funds_locked", False)
                        result["message"] += f" | Devnet contract: {contract_result.get('transaction_signature', 'N/A')[:20]}..."
                    else:
                        logger.warning(f"⚠️ Devnet smart contract failed: {contract_result.get('error')}")
                        result["smart_contract_executed"] = False
                        result["smart_contract_error"] = contract_result.get("error")
                        result["message"] += f" | Devnet contract failed: {contract_result.get('error')}"
                        
                except Exception as contract_error:
                    logger.error(f"❌ Error calling devnet smart contract: {contract_error}")
                    result["smart_contract_executed"] = False
                    result["smart_contract_error"] = str(contract_error)
                    result["message"] += f" | Contract error: {str(contract_error)}"
            
            return result
            
        except Exception as e:
            logger.error(f"Error verifying mock transaction: {e}")
            return {
                "success": False,
                "verified": False,
                "error": str(e),
                "is_mock": True
            }
    
    def generate_mock_signature(self) -> str:
        """Generate a mock transaction signature that looks real"""
        # Generate a base58-like string
        return secrets.token_urlsafe(64)[:88]  # Real Solana signatures are 88 chars


# Global instance
mock_payment_service = MockPaymentService()

