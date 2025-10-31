"""
V2 Payment Processor - Raw instruction-based payment processing
Implements process_entry_payment_v2 using solana-py with raw instructions
Based on test_v2_raw_payment.ts
"""
import os
import hashlib
import struct
from typing import Dict, Any, Optional
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.instruction import Instruction, AccountMeta
from solders.system_program import SYSTEM_PROGRAM_ID
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
import logging

# Sysvar addresses (can't be imported directly in solders)
SYSVAR_RENT_PUBKEY = Pubkey.from_string("SysvarRent111111111111111111111111111111111")

logger = logging.getLogger(__name__)


class V2PaymentProcessor:
    """
    V2 Payment Processor using raw Solana instructions.
    
    This class implements the process_entry_payment_v2 instruction
    using raw Web3.js-style instruction building, bypassing Anchor's
    client library which has account ordering issues.
    """
    
    def __init__(
        self,
        rpc_endpoint: Optional[str] = None,
        program_id: Optional[str] = None,
        usdc_mint: Optional[str] = None,
        bounty_pool_wallet: Optional[str] = None,
        operational_wallet: Optional[str] = None,
        buyback_wallet: Optional[str] = None,
        staking_wallet: Optional[str] = None,
    ):
        """
        Initialize V2 Payment Processor with configuration.
        
        All parameters can be overridden, but will default to environment variables.
        """
        # Program and network configuration
        self.program_id = Pubkey.from_string(
            program_id or os.getenv(
                "LOTTERY_PROGRAM_ID_V2",
                "HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm"
            )
        )
        
        self.rpc_endpoint = rpc_endpoint or os.getenv(
            "SOLANA_RPC_ENDPOINT",
            "https://api.devnet.solana.com"
        )
        
        # Token and wallet configuration
        self.usdc_mint = Pubkey.from_string(
            usdc_mint or os.getenv(
                "V2_USDC_MINT",
                "JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh"
            )
        )
        
        self.bounty_pool_wallet = Pubkey.from_string(
            bounty_pool_wallet or os.getenv(
                "V2_BOUNTY_POOL_WALLET",
                "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF"
            )
        )
        
        self.operational_wallet = Pubkey.from_string(
            operational_wallet or os.getenv(
                "V2_OPERATIONAL_WALLET",
                "46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D"
            )
        )
        
        self.buyback_wallet = Pubkey.from_string(
            buyback_wallet or os.getenv(
                "V2_BUYBACK_WALLET",
                "7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya"
            )
        )
        
        self.staking_wallet = Pubkey.from_string(
            staking_wallet or os.getenv(
                "V2_STAKING_WALLET",
                "Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX"
            )
        )
        
        # Initialize Solana client
        self.client = AsyncClient(self.rpc_endpoint, commitment=Confirmed)
        
        logger.info(f"✅ V2PaymentProcessor initialized")
        logger.info(f"   Program ID: {self.program_id}")
        logger.info(f"   USDC Mint: {self.usdc_mint}")
        logger.info(f"   RPC Endpoint: {self.rpc_endpoint}")
    
    def _u64_le_bytes(self, value: int) -> bytes:
        """Convert u64 to little-endian bytes."""
        return struct.pack("<Q", value)
    
    def _derive_instruction_discriminator(self, instruction_name: str) -> bytes:
        """
        Derive the 8-byte discriminator for an Anchor instruction.
        
        Anchor uses: sha256("global:instruction_name")[:8]
        """
        namespace = "global"
        seed = f"{namespace}:{instruction_name}"
        hash_bytes = hashlib.sha256(seed.encode()).digest()
        return hash_bytes[:8]
    
    async def _derive_pdas(self, bounty_id: int) -> Dict[str, Pubkey]:
        """Derive all required PDAs for the payment instruction."""
        # Global PDA
        global_pda, _ = Pubkey.find_program_address(
            [b"global"],
            self.program_id
        )
        
        # Bounty PDA
        bounty_pda, _ = Pubkey.find_program_address(
            [b"bounty", self._u64_le_bytes(bounty_id)],
            self.program_id
        )
        
        # Buyback Tracker PDA
        buyback_tracker_pda, _ = Pubkey.find_program_address(
            [b"buyback_tracker"],
            self.program_id
        )
        
        return {
            "global": global_pda,
            "bounty": bounty_pda,
            "buyback_tracker": buyback_tracker_pda,
        }
    
    def _derive_token_accounts(self, user_wallet: Pubkey) -> Dict[str, Pubkey]:
        """
        Derive associated token accounts for all wallets.
        
        ATA derivation: findProgramAddress([wallet, TOKEN_PROGRAM_ID, mint], ASSOCIATED_TOKEN_PROGRAM_ID)
        """
        accounts = {}
        wallets = {
            "user": user_wallet,
            "bounty_pool": self.bounty_pool_wallet,
            "operational": self.operational_wallet,
            "buyback": self.buyback_wallet,
            "staking": self.staking_wallet,
        }
        
        for name, wallet in wallets.items():
            # Derive ATA using standard SPL Token derivation
            accounts[name], _ = Pubkey.find_program_address(
                [
                    bytes(wallet),
                    bytes(TOKEN_PROGRAM_ID),
                    bytes(self.usdc_mint),
                ],
                ASSOCIATED_TOKEN_PROGRAM_ID
            )
        
        return accounts
    
    async def process_entry_payment(
        self,
        user_keypair: Keypair,
        bounty_id: int,
        entry_amount: int,  # Amount in smallest unit (6 decimals for USDC)
    ) -> Dict[str, Any]:
        """
        Process entry payment using V2 contract with 4-way split.
        
        Args:
            user_keypair: The user's keypair signing the transaction
            bounty_id: The bounty ID (typically 1)
            entry_amount: Payment amount in smallest unit (e.g., 15_000_000 for 15 USDC)
        
        Returns:
            Dict with transaction signature and status
        """
        try:
            logger.info(f"🔄 Processing V2 entry payment: Bounty {bounty_id}, Amount {entry_amount}")
            
            # Derive all PDAs
            pdas = await self._derive_pdas(bounty_id)
            logger.info(f"   Global PDA: {pdas['global']}")
            logger.info(f"   Bounty PDA: {pdas['bounty']}")
            logger.info(f"   Buyback Tracker PDA: {pdas['buyback_tracker']}")
            
            # Derive token accounts
            token_accounts = await self._derive_token_accounts(user_keypair.pubkey())
            
            # Build instruction discriminator
            discriminator = self._derive_instruction_discriminator("process_entry_payment_v2")
            
            # Build instruction data: discriminator + bounty_id (u64) + entry_amount (u64)
            instruction_data = (
                discriminator +
                self._u64_le_bytes(bounty_id) +
                self._u64_le_bytes(entry_amount)
            )
            
            # Build account metas (must match exact order from contract)
            account_metas = [
                # PDAs
                AccountMeta(pdas["global"], is_signer=False, is_writable=True),
                AccountMeta(pdas["bounty"], is_signer=False, is_writable=True),
                AccountMeta(pdas["buyback_tracker"], is_signer=False, is_writable=True),
                
                # User
                AccountMeta(user_keypair.pubkey(), is_signer=True, is_writable=True),
                AccountMeta(token_accounts["user"], is_signer=False, is_writable=True),
                
                # Destination token accounts
                AccountMeta(token_accounts["bounty_pool"], is_signer=False, is_writable=True),
                AccountMeta(token_accounts["operational"], is_signer=False, is_writable=True),
                AccountMeta(token_accounts["buyback"], is_signer=False, is_writable=True),
                AccountMeta(token_accounts["staking"], is_signer=False, is_writable=True),
                
                # Wallet addresses (read-only)
                AccountMeta(self.bounty_pool_wallet, is_signer=False, is_writable=False),
                AccountMeta(self.operational_wallet, is_signer=False, is_writable=False),
                AccountMeta(self.buyback_wallet, is_signer=False, is_writable=False),
                AccountMeta(self.staking_wallet, is_signer=False, is_writable=False),
                
                # Program IDs
                AccountMeta(self.usdc_mint, is_signer=False, is_writable=False),
                AccountMeta(TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
                AccountMeta(ASSOCIATED_TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
                AccountMeta(SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
                AccountMeta(SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
            ]
            
            # Create instruction
            instruction = Instruction(
                program_id=self.program_id,
                accounts=account_metas,
                data=instruction_data,
            )
            
            # Get recent blockhash
            latest_blockhash = await self.client.get_latest_blockhash()
            
            # Create transaction - solders Transaction constructor takes instructions, payer, and blockhash
            transaction = Transaction(
                instructions=[instruction],
                payer=user_keypair.pubkey(),
                recent_blockhash=latest_blockhash.value.blockhash
            )
            
            # Sign transaction - solders Transaction.sign() takes list of signers
            transaction.sign([user_keypair])
            
            # Send transaction
            signature = await self.client.send_transaction(transaction)
            
            # Confirm transaction
            await self.client.confirm_transaction(signature.value, commitment=Confirmed)
            
            logger.info(f"✅ V2 payment processed successfully")
            logger.info(f"   Signature: {signature.value}")
            
            return {
                "success": True,
                "transaction_signature": str(signature.value),
                "explorer_url": f"https://explorer.solana.com/tx/{signature.value}?cluster={'mainnet-beta' if 'mainnet' in self.rpc_endpoint else 'devnet'}",
                "bounty_id": bounty_id,
                "amount": entry_amount,
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing V2 payment: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def get_bounty_status(self, bounty_id: int) -> Dict[str, Any]:
        """Get current status of a bounty."""
        try:
            pdas = await self._derive_pdas(bounty_id)
            
            # Fetch bounty account data
            bounty_account = await self.client.get_account_info(pdas["bounty"])
            
            if not bounty_account.value:
                return {
                    "success": False,
                    "error": "Bounty not found",
                }
            
            # Decode bounty data (would need to deserialize Anchor account)
            # For now, return basic info
            return {
                "success": True,
                "bounty_id": bounty_id,
                "bounty_pda": str(pdas["bounty"]),
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting bounty status: {e}")
            return {
                "success": False,
                "error": str(e),
            }


# Global instance
_v2_payment_processor: Optional[V2PaymentProcessor] = None


def get_v2_payment_processor() -> V2PaymentProcessor:
    """Get or create global V2 payment processor instance."""
    global _v2_payment_processor
    if _v2_payment_processor is None:
        _v2_payment_processor = V2PaymentProcessor()
    return _v2_payment_processor

