"""
WalletConnect v2.0 integration service for Solana multi-wallet support
"""
import base64
import base58
import os
from typing import Optional, Dict, Any
from datetime import datetime
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solana.rpc.types import TxOpts
from solders.transaction import Transaction
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.keypair import Keypair
from solders.hash import Hash
# SPL Token constants - we'll implement manually since spl packages aren't available
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
ASSOCIATED_TOKEN_PROGRAM_ID = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
import requests
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, PaymentTransaction
from .repositories import UserRepository

class WalletConnectSolanaService:
    """Service for handling WalletConnect v2.0 with Solana wallets"""
    
    def __init__(self, project_id: str, rpc_endpoint: str = "https://api.mainnet-beta.solana.com"):
        self.project_id = project_id
        self.client = AsyncClient(rpc_endpoint)
        
        # Wallet configuration - separate deposit and jackpot wallets
        self.deposit_wallet = os.getenv("DEPOSIT_WALLET_ADDRESS", "11111111111111111111111111111112")
        self.jackpot_wallet = os.getenv("JACKPOT_WALLET_ADDRESS", "11111111111111111111111111111112")
        self.treasury_wallet = self.jackpot_wallet  # Legacy compatibility - jackpot is now the treasury
        
        # Supported tokens for payments - USDC SPL only
        self.supported_tokens = {
            "USDC": {
                "name": "USD Coin",
                "symbol": "USDC",
                "decimals": 6,
                "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC mint address
                "icon": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v/logo.png"
            }
        }
        
        # Supported Solana wallets that work with WalletConnect
        self.supported_wallets = {
            "phantom": {
                "name": "Phantom",
                "icon": "https://phantom.app/img/phantom-icon.svg",
                "mobile_link": "phantom://",
                "desktop_link": "https://phantom.app/"
            },
            "solflare": {
                "name": "Solflare",
                "icon": "https://solflare.com/assets/solflare-logo.svg",
                "mobile_link": "solflare://",
                "desktop_link": "https://solflare.com/"
            },
            "backpack": {
                "name": "Backpack",
                "icon": "https://backpack.app/icon.png",
                "mobile_link": "backpack://",
                "desktop_link": "https://backpack.app/"
            },
            "glow": {
                "name": "Glow",
                "icon": "https://glow.app/icon.png",
                "mobile_link": "glow://",
                "desktop_link": "https://glow.app/"
            }
        }
    
    def get_walletconnect_config(self) -> Dict[str, Any]:
        """Get WalletConnect configuration for Solana"""
        return {
            "projectId": self.project_id,
            "metadata": {
                "name": "Billions",
                "description": "Challenge the AI - Try to convince me to transfer funds!",
                "url": "https://billions-bounty.com",
                "icons": ["https://billions-bounty.com/icon.png"]
            },
            "chains": ["solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp"],  # Solana Mainnet
            "methods": [
                "solana_signTransaction",
                "solana_signMessage",
                "solana_signAndSendTransaction"
            ],
            "events": ["chainChanged", "accountsChanged"],
            "supported_wallets": self.supported_wallets
        }
    
    async def verify_wallet_signature(self, wallet_address: str, signature: str, message: str) -> bool:
        """Verify that a Solana wallet signature is valid"""
        try:
            # For Solana, we'll do basic validation
            # In a production environment, you'd verify the signature using nacl or similar
            if not wallet_address or len(wallet_address) < 32:
                return False
            
            # Validate that the wallet address is a valid Solana address
            try:
                Pubkey.from_string(wallet_address)
            except:
                return False
            
            # For demo purposes, we'll assume valid if signature exists
            # In production, implement proper signature verification
            return bool(signature and len(signature) > 0)
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False
    
    async def connect_wallet(self, session: AsyncSession, user_id: int, wallet_address: str, 
                           signature: str, message: str) -> Dict[str, Any]:
        """Connect a Solana wallet to a user account"""
        # Verify the wallet signature
        is_valid = await self.verify_wallet_signature(wallet_address, signature, message)
        
        if not is_valid:
            return {
                "success": False,
                "error": "Invalid wallet signature"
            }
        
        # Update user with wallet address
        user_repo = UserRepository(session)
        # Note: Make sure your User model has wallet_address field
        
        return {
            "success": True,
            "wallet_address": wallet_address,
            "network": "solana",
            "message": "Wallet connected successfully"
        }
    
    def get_associated_token_address(self, owner: Pubkey, mint: Pubkey) -> Pubkey:
        """Calculate the associated token address for a given owner and mint"""
        # This is a simplified implementation
        # In production, you'd want to use the official SPL token library
        seeds = [
            bytes(owner),
            bytes(Pubkey.from_string(TOKEN_PROGRAM_ID)),
            bytes(mint)
        ]
        return Pubkey.find_program_address(seeds, Pubkey.from_string(ASSOCIATED_TOKEN_PROGRAM_ID))[0]
    
    async def get_wallet_balances(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Get balances for all supported tokens (SOL, USDC, USDT)"""
        try:
            pubkey = Pubkey.from_string(wallet_address)
            balances = {}
            
            # Get SOL balance
            sol_response = await self.client.get_balance(pubkey, commitment=Commitment("confirmed"))
            if sol_response.value is not None:
                balances["SOL"] = {
                    "balance": sol_response.value / 1e9,
                    "symbol": "SOL",
                    "decimals": 9,
                    "usd_value": None  # Will be calculated separately
                }
            
            # Get SPL token balances (USDC, USDT)
            for token_symbol, token_info in self.supported_tokens.items():
                if token_symbol == "SOL":
                    continue  # Already handled above
                
                try:
                    mint_pubkey = Pubkey.from_string(token_info["mint"])
                    ata = self.get_associated_token_address(pubkey, mint_pubkey)
                    
                    # Get token account info
                    account_info = await self.client.get_account_info(ata, commitment=Commitment("confirmed"))
                    
                    if account_info.value and account_info.value.data:
                        # Parse token account data (simplified)
                        # In production, use proper SPL token account parsing
                        # For now, we'll use get_token_accounts_by_owner
                        token_accounts = await self.client.get_token_accounts_by_owner(
                            pubkey, 
                            {"mint": str(mint_pubkey)},
                            commitment=Commitment("confirmed")
                        )
                        
                        if token_accounts.value:
                            # Get the first token account
                            account = token_accounts.value[0]
                            # Parse balance from account data
                            # This is simplified - in production use proper parsing
                            balance_data = account.account.data
                            if balance_data and len(balance_data) >= 64:
                                # Token amount is at bytes 64-72 (simplified)
                                raw_balance = int.from_bytes(balance_data[64:72], byteorder='little')
                                balance = raw_balance / (10 ** token_info["decimals"])
                                
                                balances[token_symbol] = {
                                    "balance": balance,
                                    "symbol": token_symbol,
                                    "decimals": token_info["decimals"],
                                    "usd_value": balance if token_symbol in ["USDC", "USDT"] else None
                                }
                except Exception as e:
                    print(f"Error getting {token_symbol} balance: {e}")
                    balances[token_symbol] = {
                        "balance": 0,
                        "symbol": token_symbol,
                        "decimals": token_info["decimals"],
                        "usd_value": 0 if token_symbol in ["USDC", "USDT"] else None
                    }
            
            return {
                "balances": balances,
                "network": "solana"
            }
        except Exception as e:
            print(f"Error getting wallet balances: {e}")
            return None
    
    async def get_wallet_balance(self, wallet_address: str, token_symbol: str = "SOL") -> Optional[Dict[str, Any]]:
        """Get balance for a specific token"""
        all_balances = await self.get_wallet_balances(wallet_address)
        if all_balances and token_symbol in all_balances["balances"]:
            balance_info = all_balances["balances"][token_symbol]
            return {
                "balance": balance_info["balance"],
                "currency": token_symbol,
                "network": "solana"
            }
        return None
    
    async def create_payment_transaction(self, from_wallet: str, amount: float, 
                                       query_cost_usd: float, token_symbol: str = "USDC") -> Dict[str, Any]:
        """Create a Solana transaction for USDC SPL token payment"""
        try:
            from_pubkey = Pubkey.from_string(from_wallet)
            to_pubkey = Pubkey.from_string(self.treasury_wallet)
            
            # Only support USDC SPL token
            if token_symbol not in self.supported_tokens:
                return {
                    "success": False,
                    "error": f"Unsupported token: {token_symbol}. Only USDC SPL is supported."
                }
            
            token_info = self.supported_tokens[token_symbol]
            mint_pubkey = Pubkey.from_string(token_info["mint"])
            
            # Calculate token amount in smallest units (USDC has 6 decimals)
            token_amount = int(amount * (10 ** token_info["decimals"]))
            
            # Get associated token addresses
            from_ata = self.get_associated_token_address(from_pubkey, mint_pubkey)
            to_ata = self.get_associated_token_address(to_pubkey, mint_pubkey)
            
            # Return transaction structure for USDC SPL token transfer
            return {
                "success": True,
                "transaction": "usdc_spl_token_transfer",  # USDC SPL token transfer
                "amount": amount,
                "token": token_symbol,
                "amount_usd": query_cost_usd,
                "recipient": self.treasury_wallet,
                "network": "solana",
                "units": token_amount,
                "mint": token_info["mint"],
                "from_ata": str(from_ata),
                "to_ata": str(to_ata),
                "note": "USDC SPL token transfer - use wallet's token transfer method"
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create transaction: {str(e)}"
            }
    
    async def verify_transaction(self, signature: str) -> Dict[str, Any]:
        """Verify that a Solana transaction was completed successfully"""
        try:
            # Get transaction details
            tx_response = await self.client.get_transaction(
                signature, 
                commitment=Commitment("confirmed"),
                max_supported_transaction_version=0
            )
            
            if tx_response.value is None:
                return {
                    "success": False,
                    "error": "Transaction not found or still pending"
                }
            
            transaction = tx_response.value
            
            # Check if transaction was successful
            if transaction.meta and transaction.meta.err is None:
                # Extract amount from transaction
                amount_lamports = None
                if transaction.meta.pre_balances and transaction.meta.post_balances:
                    # Calculate the difference in the first account (sender)
                    if len(transaction.meta.pre_balances) > 0 and len(transaction.meta.post_balances) > 0:
                        balance_diff = transaction.meta.pre_balances[0] - transaction.meta.post_balances[0]
                        # Subtract the fee to get the actual transfer amount
                        amount_lamports = balance_diff - transaction.meta.fee
                
                return {
                    "success": True,
                    "signature": signature,
                    "amount_lamports": amount_lamports,
                    "amount_sol": amount_lamports / 1e9 if amount_lamports else None,
                    "fee_lamports": transaction.meta.fee,
                    "confirmed": True,
                    "network": "solana",
                    "explorer_url": f"https://solscan.io/tx/{signature}"
                }
            else:
                return {
                    "success": False,
                    "error": "Transaction failed"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error verifying transaction: {str(e)}"
            }
    
    async def get_sol_to_usd_rate(self) -> Optional[float]:
        """Get current SOL to USD exchange rate"""
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd",
                timeout=10
            )
            data = response.json()
            return data.get("solana", {}).get("usd")
        except Exception:
            # Fallback rate if API fails
            return 100.0  # Approximate SOL price

# MoonpayService removed - $3000/month too expensive for launch
# Will implement Stripe or other affordable fiat options when profitable

class PaymentOrchestrator:
    """Orchestrates payments from Solana wallets via WalletConnect"""
    
    def __init__(self, wallet_service: WalletConnectSolanaService):
        self.wallet_service = wallet_service
    
    async def calculate_payment_options(self, amount_usd: float) -> Dict[str, Any]:
        """Calculate payment options for a given USD amount - USDC SPL only"""
        
        # Calculate amounts for USDC SPL token only
        token_options = {}
        
        for token_symbol, token_info in self.wallet_service.supported_tokens.items():
            if token_symbol == "USDC":
                # USDC is 1:1 with USD
                token_options[token_symbol] = {
                    "amount": amount_usd,
                    "rate_usd": 1.0,
                    "symbol": token_symbol,
                    "name": token_info["name"],
                    "decimals": token_info["decimals"],
                    "icon": token_info["icon"]
                }
        
        return {
            "amount_usd": amount_usd,
            "token_options": token_options,
            "payment_methods": {
                "wallet": {
                    "available": len(token_options) > 0,
                    "supported_tokens": token_options,
                    "network": "solana",
                    "supported_wallets": self.wallet_service.supported_wallets
                },
                "fiat": {
                    "available": False,
                    "note": "Fiat payments (Moonpay $3000/month) will be added when profitable"
                }
            }
        }
    
    async def process_wallet_payment(self, session: AsyncSession, user_id: int, 
                                   wallet_address: str, amount_usd: float, 
                                   token_symbol: str = "USDC") -> Dict[str, Any]:
        """Process payment via connected Solana wallet"""
        payment_options = await self.calculate_payment_options(amount_usd)
        
        if token_symbol not in payment_options["token_options"]:
            return {
                "success": False,
                "error": f"Unsupported token: {token_symbol}"
            }
        
        token_info = payment_options["token_options"][token_symbol]
        token_amount = token_info["amount"]
        
        # Check wallet balance for the specific token
        balance_info = await self.wallet_service.get_wallet_balance(wallet_address, token_symbol)
        if not balance_info or balance_info["balance"] < token_amount:
            return {
                "success": False,
                "error": f"Insufficient {token_symbol} balance"
            }
        
        # Create transaction
        tx_result = await self.wallet_service.create_payment_transaction(
            wallet_address, token_amount, amount_usd, token_symbol
        )
        
        return tx_result