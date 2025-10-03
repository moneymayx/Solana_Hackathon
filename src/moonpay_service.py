import os
import hmac
import hashlib
import time
import requests
from typing import Dict, Any, Optional
from urllib.parse import urlencode

class MoonpayService:
    def __init__(self):
        self.api_key = os.getenv("MOONPAY_API_KEY")
        self.secret_key = os.getenv("MOONPAY_SECRET_KEY")
        self.base_url = os.getenv("MOONPAY_BASE_URL", "https://api.moonpay.com")
        self.webhook_secret = os.getenv("MOONPAY_WEBHOOK_SECRET")
        
    def _generate_signature(self, query_string: str) -> str:
        """Generate HMAC signature for Moonpay API requests"""
        if not self.secret_key:
            raise ValueError("Moonpay secret key not configured")
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def create_buy_url(self, 
                      currency_code: str,
                      base_currency_amount: float,
                      base_currency_code: str = "usd",
                      wallet_address: str = "",
                      external_customer_id: str = "",
                      external_transaction_id: str = "",
                      redirect_url: str = "",
                      failure_redirect_url: str = "",
                      quote_currency_amount: Optional[float] = None) -> Dict[str, Any]:
        """Create a Moonpay buy URL for fiat-to-crypto conversion with Apple Pay and PayPal support"""
        
        if not self.api_key:
            raise ValueError("Moonpay API key not configured")
        
        # Build query parameters
        params = {
            "apiKey": self.api_key,
            "currencyCode": currency_code,
            "baseCurrencyAmount": base_currency_amount,
            "baseCurrencyCode": base_currency_code,
            "walletAddress": wallet_address,
            "externalCustomerId": external_customer_id,
            "externalTransactionId": external_transaction_id,
            "redirectURL": redirect_url,
            "failureRedirectURL": failure_redirect_url,
            # Enable Apple Pay and PayPal payment methods
            "paymentMethod": "apple_pay,paypal",
            "enableApplePay": "true",
            "enablePayPal": "true",
            # Disable credit card manual entry
            "enableCreditCard": "false"
        }
        
        # Add optional parameters
        if quote_currency_amount:
            params["quoteCurrencyAmount"] = quote_currency_amount
        
        # Remove empty values
        params = {k: v for k, v in params.items() if v}
        
        # Generate query string
        query_string = urlencode(sorted(params.items()))
        
        # Generate signature
        signature = self._generate_signature(query_string)
        params["signature"] = signature
        
        # Build final URL
        buy_url = f"{self.base_url}/v1/buy?{urlencode(params)}"
        
        return {
            "buy_url": buy_url,
            "transaction_id": external_transaction_id,
            "currency_code": currency_code,
            "amount": base_currency_amount,
            "wallet_address": wallet_address,
            "payment_methods": ["apple_pay", "paypal"]
        }
    
    def get_quote(self, 
                 currency_code: str,
                 base_currency_amount: float,
                 base_currency_code: str = "usd") -> Dict[str, Any]:
        """Get a quote for fiat-to-crypto conversion"""
        
        if not self.api_key:
            raise ValueError("Moonpay API key not configured")
        
        params = {
            "apiKey": self.api_key,
            "currencyCode": currency_code,
            "baseCurrencyAmount": base_currency_amount,
            "baseCurrencyCode": base_currency_code,
        }
        
        try:
            response = requests.get(f"{self.base_url}/v1/currencies/{currency_code}/buy_quote", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get quote: {str(e)}")
    
    def get_supported_currencies(self) -> Dict[str, Any]:
        """Get list of supported currencies"""
        
        if not self.api_key:
            raise ValueError("Moonpay API key not configured")
        
        try:
            response = requests.get(f"{self.base_url}/v1/currencies", params={"apiKey": self.api_key})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get supported currencies: {str(e)}")
    
    def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction status"""
        
        if not self.api_key:
            raise ValueError("Moonpay API key not configured")
        
        params = {
            "apiKey": self.api_key,
        }
        
        try:
            response = requests.get(f"{self.base_url}/v1/transactions/{transaction_id}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get transaction status: {str(e)}")
    
    def verify_webhook(self, payload: str, signature: str) -> bool:
        """Verify Moonpay webhook signature"""
        
        if not self.webhook_secret:
            return False
        
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process Moonpay webhook payload"""
        
        transaction_id = payload.get("data", {}).get("id")
        status = payload.get("data", {}).get("status")
        currency_code = payload.get("data", {}).get("currencyCode")
        base_currency_amount = payload.get("data", {}).get("baseCurrencyAmount")
        quote_currency_amount = payload.get("data", {}).get("quoteCurrencyAmount")
        wallet_address = payload.get("data", {}).get("walletAddress")
        
        return {
            "transaction_id": transaction_id,
            "status": status,
            "currency_code": currency_code,
            "base_currency_amount": base_currency_amount,
            "quote_currency_amount": quote_currency_amount,
            "wallet_address": wallet_address,
            "processed_at": time.time()
        }
    
    def create_payment_for_bounty_entry(self, 
                                       wallet_address: str,
                                       user_id: int,
                                       amount_usd: float = 10.0) -> Dict[str, Any]:
        """Create a Moonpay payment for bounty entry - USDC with Apple Pay and PayPal support"""
        
        # Generate unique transaction ID
        transaction_id = f"bounty_{user_id}_{int(time.time())}"
        
        # Send USDC directly to user's wallet (they'll pay to smart contract themselves)
        # This eliminates the need for fund routing and private key management
        result = self.create_buy_url(
            currency_code="usdc_sol",  # USDC on Solana
            base_currency_amount=amount_usd,
            base_currency_code="usd",
            wallet_address=wallet_address,  # Send directly to user's wallet
            external_customer_id=str(user_id),
            external_transaction_id=transaction_id,
            redirect_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/success",
            failure_redirect_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/failure"
        )
        
        return result

# Global instance
moonpay_service = MoonpayService()
