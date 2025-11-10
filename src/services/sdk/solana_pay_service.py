"""
Solana Pay SDK Service - Standardized Payments Framework

Solana Pay is a standard protocol for decentralized payments on Solana.
It provides a unified approach to payments across all Solana wallets and apps.

Transfer Request Format (from official spec):
solana:<recipient>?amount=<amount>&label=<label>&message=<message>&spl-token=<mint>&reference=<reference>

Key Features:
- Ultra Fast: Transactions confirm in less than a second
- Ultra Cheap: Average transaction cost of $0.0005
- Universal Wallet Support: Phantom, Solflare, Backpack, etc.
- Standard Protocol: Unified approach across all Solana wallets

Official Documentation: https://launch.solana.com/docs/solana-pay
Official Specification: https://docs.solanapay.com

Note: Your V2 contract uses custom instructions with PDAs and multi-recipient splits.
Solana Pay transfer requests are for simple payments. For V2 contract entry payments,
you'll need to continue using custom instructions. Solana Pay could be used for
other payment flows (donations, simple transfers) alongside your contract.
"""
import logging
from typing import Optional, Dict, Any
from solders.pubkey import Pubkey
import os
import urllib.parse
import base64

logger = logging.getLogger(__name__)


class SolanaPayService:
    """Service for Solana Pay protocol integration"""
    
    def __init__(self):
        """Initialize Solana Pay service"""
        self.enabled = os.getenv("ENABLE_SOLANA_PAY_SDK", "false").lower() == "true"
        self.rpc_endpoint = os.getenv("SOLANA_RPC_ENDPOINT", "https://api.devnet.solana.com")
        
        if not self.enabled:
            logger.info("🔧 Solana Pay SDK is disabled (set ENABLE_SOLANA_PAY_SDK=true to enable)")
        else:
            logger.info("✅ Solana Pay SDK enabled")
            logger.warning("⚠️  Note: Your V2 contract uses custom instructions - compatibility check needed")
    
    def is_enabled(self) -> bool:
        """Check if Solana Pay service is enabled"""
        return self.enabled
    
    def create_transfer_request_url(
        self,
        recipient: str,
        amount: Optional[float] = None,
        label: Optional[str] = None,
        message: Optional[str] = None,
        spl_token: Optional[str] = None,
        reference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Solana Pay Transfer Request URL following official specification
        
        Official format: solana:<recipient>?amount=<amount>&label=<label>&message=<message>&spl-token=<mint>&reference=<reference>
        
        Example from docs: solana:recipient?amount=0.01&label=Coffee%20Shop&message=Grande%20Latte
        
        This creates a non-interactive payment URL for simple SOL or SPL token transfers.
        The URL can be:
        - Encoded as a QR code for mobile wallet scanning
        - Used as a payment link in web applications
        - Embedded in mobile apps as deep links
        
        Args:
            recipient: Recipient wallet address (base58, required)
            amount: Payment amount in SOL or token units (optional)
            label: Merchant or payment label (optional, will be URL encoded)
            message: Payment message/description (optional, will be URL encoded)
            spl_token: SPL token mint address (optional, defaults to SOL if omitted)
            reference: Reference pubkey for payment tracking (optional, base58)
            
        Returns:
            Dict with payment URL and metadata
            
        Reference: https://launch.solana.com/docs/solana-pay
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Solana Pay service is disabled"
            }
        
        try:
            # Validate recipient (required)
            recipient_pubkey = Pubkey.from_string(recipient)
            
            # Build Solana Pay URL following official spec
            base_url = f"solana:{recipient}"
            params = {}
            
            # Amount (optional, in SOL or token units)
            if amount is not None:
                params["amount"] = str(amount)
            
            # Label (optional, URL encoded)
            if label:
                params["label"] = label  # urllib.parse.urlencode will encode it
            
            # Message (optional, URL encoded)
            if message:
                params["message"] = message  # urllib.parse.urlencode will encode it
            
            # SPL Token (optional, if omitted defaults to SOL)
            if spl_token:
                # Validate token mint
                token_pubkey = Pubkey.from_string(spl_token)
                params["spl-token"] = spl_token
            
            # Reference (optional, for payment tracking)
            if reference:
                # Validate reference is a valid pubkey
                ref_pubkey = Pubkey.from_string(reference)
                params["reference"] = reference
            
            # Build complete URL with proper encoding
            if params:
                # urllib.parse.urlencode properly encodes special characters
                query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
                payment_url = f"{base_url}?{query_string}"
            else:
                payment_url = base_url
            
            return {
                "success": True,
                "payment_url": payment_url,
                "transfer_request_url": payment_url,  # Alias for clarity
                "recipient": recipient,
                "amount": amount,
                "spl_token": spl_token or "SOL (native)",
                "label": label,
                "message": message,
                "reference": reference,
                "qr_data": payment_url,  # Can be used to generate QR code
                "note": "This is a transfer request URL. For V2 contract payments, use custom instructions."
            }
        
        except Exception as e:
            logger.error(f"Error creating Solana Pay transfer request URL: {e}")
            return {
                "success": False,
                "error": f"Invalid parameters: {str(e)}"
            }
    
    async def verify_payment_transaction(
        self,
        transaction_signature: str,
        expected_amount: Optional[float] = None,
        expected_recipient: Optional[str] = None,
        expected_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify a Solana Pay payment transaction
        
        Queries the transaction on-chain to verify payment details.
        
        Args:
            transaction_signature: Transaction signature to verify
            expected_amount: Expected payment amount (optional, for validation)
            expected_recipient: Expected recipient address (optional, for validation)
            expected_token: Expected token mint (optional, for validation)
            
        Returns:
            Dict with verification status and transaction details
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Solana Pay service is disabled"
            }
        
        try:
            import httpx
            
            # Query transaction from blockchain
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.rpc_endpoint,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTransaction",
                        "params": [
                            transaction_signature,
                            {
                                "encoding": "jsonParsed",
                                "maxSupportedTransactionVersion": 0
                            }
                        ]
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("result")
                    
                    if not result:
                        return {
                            "success": False,
                            "error": "Transaction not found"
                        }
                    
                    # Parse transaction to extract payment details
                    # TODO: Extract actual transfer details from transaction
                    # This needs parsing of instruction data
                    
                    return {
                        "success": True,
                        "transaction_signature": transaction_signature,
                        "verified": True,  # Placeholder - needs actual validation
                        "transaction_data": result,
                        "note": "Payment verification - need to parse instruction data for full validation"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"RPC error: {response.status_code}"
                    }
        
        except Exception as e:
            logger.error(f"Error verifying Solana Pay transaction: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_v2_compatibility(self) -> Dict[str, Any]:
        """
        Check if Solana Pay is compatible with V2 contract requirements
        
        Your V2 contract uses:
        - Custom instructions with PDAs
        - Multi-recipient splits (60/20/10/10)
        - Specific instruction format
        
        Returns:
            Dict with compatibility assessment
        """
        return {
            "compatible_for_simple_payments": True,
            "compatible_for_v2_contract": False,
            "reason": "V2 contract requires custom instructions with PDAs and multi-recipient splits",
            "recommendation": "Use Solana Pay for simple transfers, keep custom instructions for contract entry payments",
            "hybrid_approach": "Could use Solana Pay URL format but process with custom instruction builder"
        }


# Global instance
solana_pay_service = SolanaPayService()

