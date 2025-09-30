import os
import asyncio
import time
from typing import Optional, Dict, Any, List
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solders.transaction import Transaction
from solders.pubkey import Pubkey as PublicKey
from solders.keypair import Keypair
from solders.system_program import transfer, TransferParams
from solana.rpc.types import TxOpts
from spl.token.instructions import transfer_checked, TransferCheckedParams
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.async_client import AsyncToken
from spl.token.core import MintInfo
import base58

class SolanaService:
    # Token mint addresses on Solana mainnet - USDC SPL only
    TOKEN_MINTS = {
        "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    }
    
    # Security limits
    MIN_TRANSFER_AMOUNT = 0.001  # Minimum transfer amount (prevents dust attacks)
    RATE_LIMIT_WINDOW = 60  # 1 minute cooldown between transfers per user
    
    def __init__(self):
        self.rpc_endpoint = os.getenv("SOLANA_RPC_ENDPOINT", "https://api.mainnet-beta.solana.com")
        self.treasury_address = os.getenv("TREASURY_SOLANA_ADDRESS")
        self.client = AsyncClient(self.rpc_endpoint, commitment=Commitment("confirmed"))
        
        # Security tracking
        self.transfer_history = {}  # Track transfers by user
        self.rate_limits = {}  # Track rate limits by user
        
        # Load treasury private key from environment
        treasury_private_key = os.getenv("TREASURY_PRIVATE_KEY")
        if treasury_private_key:
            try:
                # Decode base58 private key
                private_key_bytes = base58.b58decode(treasury_private_key)
                self.treasury_keypair = Keypair.from_secret_key(private_key_bytes)
            except Exception as e:
                print(f"Error loading treasury keypair: {e}")
                self.treasury_keypair = None
        else:
            self.treasury_keypair = None
    
    def _validate_transfer_request(self, to_address: str, amount: float, token: str, user_id: int) -> Dict[str, Any]:
        """Validate transfer request for security
        
        NOTE: This validation only ensures basic security (address format, dust prevention, rate limiting).
        The main security is that transfers ONLY happen when the AI is genuinely convinced through
        the bounty system's natural reasoning process. No hardcoded amount limits to allow large jackpots.
        """
        current_time = time.time()
        
        # Validate address format
        try:
            PublicKey(to_address)
        except Exception:
            return {"valid": False, "error": "Invalid recipient address format"}
        
        # Validate amount (only minimum to prevent dust attacks)
        if amount < self.MIN_TRANSFER_AMOUNT:
            return {"valid": False, "error": f"Amount too small. Minimum: {self.MIN_TRANSFER_AMOUNT}"}
        
        # Validate token
        if token not in self.TOKEN_MINTS:
            return {"valid": False, "error": f"Unsupported token: {token}"}
        
        # Check rate limits (only cooldown between transfers)
        user_key = f"user_{user_id}"
        if user_key in self.rate_limits:
            last_transfer = self.rate_limits[user_key]
            if current_time - last_transfer < self.RATE_LIMIT_WINDOW:
                return {"valid": False, "error": "Rate limit exceeded. Please wait before next transfer."}
        
        return {"valid": True, "error": None}
    
    def _log_transfer(self, user_id: int, amount: float, token: str, to_address: str, signature: str):
        """Log transfer for security tracking"""
        user_key = f"user_{user_id}"
        current_time = time.time()
        
        if user_key not in self.transfer_history:
            self.transfer_history[user_key] = []
        
        self.transfer_history[user_key].append({
            "timestamp": current_time,
            "amount": amount,
            "token": token,
            "to_address": to_address,
            "signature": signature
        })
        
        self.rate_limits[user_key] = current_time
        
        # Clean old entries (older than 7 days)
        cutoff_time = current_time - (7 * 86400)
        self.transfer_history[user_key] = [
            t for t in self.transfer_history[user_key] 
            if t["timestamp"] > cutoff_time
        ]
    
    async def get_balance(self, public_key: str, token: str = "USDC") -> float:
        """Get balance for a public key (USDC SPL token only)"""
        try:
            pubkey = PublicKey(public_key)
            
            # Only support USDC SPL token
            mint_address = self.TOKEN_MINTS.get(token)
            if not mint_address:
                return 0.0
            
            # For USDC SPL token, we need to get the token account balance
            # This is a simplified version - in production you'd need to find the token account
            # and get its balance using the SPL token program
            return 0.0  # Placeholder - implement SPL token balance checking
                
        except Exception as e:
            print(f"Error getting USDC balance: {e}")
            return 0.0
    
    async def transfer_token(self, to_address: str, amount: float, token: str, user_id: int) -> Dict[str, Any]:
        """Transfer USDC SPL token from treasury to recipient with security validation"""
        if not self.treasury_keypair:
            return {
                "success": False,
                "error": "Treasury keypair not configured",
                "signature": None
            }
        
        # Validate transfer request
        validation = self._validate_transfer_request(to_address, amount, token, user_id)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"],
                "signature": None
            }
        
        try:
            # Only support USDC SPL token
            if token == "USDC":
                return await self._transfer_spl_token(to_address, amount, token, user_id)
            else:
                return {
                    "success": False,
                    "error": f"Only USDC SPL token is supported, got: {token}",
                    "signature": None
                }
                
        except Exception as e:
            print(f"Error transferring {token}: {e}")
            return {
                "success": False,
                "error": str(e),
                "signature": None
            }
    
    
    async def _transfer_spl_token(self, to_address: str, amount: float, token: str, user_id: int) -> Dict[str, Any]:
        """Transfer USDC SPL token from treasury to recipient"""
        try:
            mint_address = self.TOKEN_MINTS.get(token)
            if not mint_address:
                return {
                    "success": False,
                    "error": f"USDC token not found in configuration",
                    "signature": None
                }
            
            # For SPL tokens, we need to:
            # 1. Find the source token account
            # 2. Find or create the destination token account
            # 3. Transfer the tokens
            
            # This is a simplified implementation
            # In production, you'd need to handle token accounts properly
            
            # For now, return a placeholder response
            # In a real implementation, you'd use the SPL token program
            return {
                "success": False,
                "error": f"USDC SPL token transfers not yet implemented",
                "signature": None
            }
            
        except Exception as e:
            print(f"Error transferring {token}: {e}")
            return {
                "success": False,
                "error": str(e),
                "signature": None
            }
    
    async def transfer_usdc(self, to_address: str, amount_usdc: float) -> Dict[str, Any]:
        """Legacy method for USDC transfers - use transfer_token instead"""
        return await self.transfer_token(to_address, amount_usdc, "USDC", 0)
    
    async def verify_transaction(self, signature: str) -> bool:
        """Verify a transaction was successful"""
        try:
            response = await self.client.get_transaction(signature)
            return response.value is not None
        except Exception as e:
            print(f"Error verifying transaction: {e}")
            return False
    
    async def get_treasury_balance(self) -> float:
        """Get treasury wallet balance"""
        if not self.treasury_keypair:
            return 0.0
        return await self.get_balance(str(self.treasury_keypair.public_key))
    
    async def close(self):
        """Close the RPC client"""
        await self.client.close()

# Global instance
solana_service = SolanaService()
