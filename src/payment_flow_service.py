"""
Payment Flow Service - Direct MoonPay to Smart Contract Integration
Handles the complete payment flow from MoonPay to smart contract without fund routing
"""
import os
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from .models import PaymentTransaction, User
from .moonpay_service import moonpay_service
from .smart_contract_service import smart_contract_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentFlowService:
    """Service for managing direct MoonPay to smart contract payment flow"""
    
    def __init__(self):
        self.moonpay = moonpay_service
        self.smart_contract = smart_contract_service
        
    async def create_payment_request(
        self, 
        session: AsyncSession, 
        user_id: int, 
        wallet_address: str, 
        amount_usd: float = 10.0
    ) -> Dict[str, Any]:
        """Create a payment request that sends USDC directly to user's wallet"""
        try:
            logger.info(f"💳 Creating payment request: User {user_id}, Wallet {wallet_address}, Amount ${amount_usd}")
            
            # Create MoonPay payment URL
            payment_data = self.moonpay.create_payment_for_bounty_entry(
                wallet_address=wallet_address,
                user_id=user_id,
                amount_usd=amount_usd
            )
            
            # Record payment transaction in database
            transaction_record = await self._record_payment_transaction(
                session, user_id, wallet_address, amount_usd, payment_data
            )
            
            if not transaction_record:
                return {"success": False, "error": "Failed to record payment transaction"}
            
            logger.info(f"✅ Payment request created: {payment_data['transaction_id']}")
            
            return {
                "success": True,
                "payment_url": payment_data["buy_url"],
                "transaction_id": payment_data["transaction_id"],
                "amount_usd": amount_usd,
                "wallet_address": wallet_address,
                "payment_methods": payment_data["payment_methods"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating payment request: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_payment_completion(
        self, 
        session: AsyncSession, 
        payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a completed MoonPay payment and enable lottery entry"""
        try:
            transaction_id = payment_data.get("transaction_id")
            wallet_address = payment_data.get("wallet_address")
            amount_usd = payment_data.get("base_currency_amount", 0.0)
            amount_usdc = payment_data.get("quote_currency_amount", 0.0)
            
            logger.info(f"💰 Processing payment completion: {transaction_id} - ${amount_usd} USD -> {amount_usdc} USDC")
            
            # Update payment transaction status
            await self._update_payment_status(
                session, transaction_id, "completed", payment_data
            )
            
            # Enable lottery entry for user (they now have USDC to pay with)
            user = await self._get_user_by_wallet(session, wallet_address)
            if user:
                await self._enable_lottery_entry(session, user.id, amount_usdc)
            
            logger.info(f"✅ Payment completed successfully: {transaction_id}")
            
            return {
                "success": True,
                "message": "Payment completed successfully. You can now play the lottery!",
                "transaction_id": transaction_id,
                "amount_usdc": amount_usdc,
                "lottery_enabled": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing payment completion: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_lottery_entry_payment(
        self, 
        session: AsyncSession, 
        user_id: int, 
        wallet_address: str, 
        entry_amount: float
    ) -> Dict[str, Any]:
        """Process a lottery entry payment using smart contract"""
        try:
            logger.info(f"🎫 Processing lottery entry payment: User {user_id}, Amount ${entry_amount}")
            
            # Use smart contract to process the entry payment
            # This will transfer USDC from user's wallet to smart contract
            contract_result = await self.smart_contract.process_lottery_entry(
                session=session,
                user_wallet=wallet_address,
                entry_amount=entry_amount,
                payment_data={"source": "user_wallet", "type": "lottery_entry"}
            )
            
            if contract_result["success"]:
                logger.info(f"✅ Lottery entry processed successfully: {contract_result['transaction_signature']}")
                return {
                    "success": True,
                    "message": "Lottery entry processed successfully!",
                    "transaction_signature": contract_result["transaction_signature"],
                    "funds_locked": contract_result["funds_locked"],
                    "research_contribution": contract_result["research_contribution"],
                    "operational_fee": contract_result["operational_fee"]
                }
            else:
                logger.error(f"❌ Lottery entry failed: {contract_result['error']}")
                return {
                    "success": False,
                    "error": contract_result["error"]
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing lottery entry payment: {e}")
            return {"success": False, "error": str(e)}
    
    async def _record_payment_transaction(
        self, 
        session: AsyncSession, 
        user_id: int, 
        wallet_address: str, 
        amount_usd: float, 
        payment_data: Dict[str, Any]
    ) -> Optional[PaymentTransaction]:
        """Record payment transaction in database"""
        try:
            transaction = PaymentTransaction(
                user_id=user_id,
                payment_method="moonpay",
                payment_type="usdc_purchase",
                amount_usd=amount_usd,
                amount_crypto=0.0,  # Will be updated when payment completes
                crypto_currency="USDC",
                tx_signature="",  # Will be updated when payment completes
                moonpay_tx_id=payment_data["transaction_id"],
                status="pending",
                from_wallet="moonpay",
                to_wallet=wallet_address,
                created_at=datetime.utcnow()
            )
            
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
            
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Error recording payment transaction: {e}")
            await session.rollback()
            return None
    
    async def _update_payment_status(
        self, 
        session: AsyncSession, 
        transaction_id: str, 
        status: str, 
        payment_data: Dict[str, Any]
    ) -> None:
        """Update payment transaction status"""
        try:
            await session.execute(
                update(PaymentTransaction)
                .where(PaymentTransaction.moonpay_tx_id == transaction_id)
                .values(
                    status=status,
                    amount_crypto=payment_data.get("quote_currency_amount", 0.0),
                    tx_signature=payment_data.get("transaction_id", ""),
                    confirmed_at=datetime.utcnow() if status == "completed" else None,
                    extra_data=str(payment_data)
                )
            )
            await session.commit()
            
        except Exception as e:
            logger.error(f"❌ Error updating payment status: {e}")
            await session.rollback()
    
    async def _get_user_by_wallet(
        self, 
        session: AsyncSession, 
        wallet_address: str
    ) -> Optional[User]:
        """Get user by wallet address"""
        try:
            result = await session.execute(
                select(User).where(User.wallet_address == wallet_address)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"❌ Error getting user by wallet: {e}")
            return None
    
    async def _enable_lottery_entry(
        self, 
        session: AsyncSession, 
        user_id: int, 
        usdc_balance: float
    ) -> None:
        """Enable lottery entry for user (they now have USDC)"""
        try:
            # Update user's USDC balance or add a flag
            await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(
                    total_cost=usdc_balance,  # Track USDC balance
                    last_active=datetime.utcnow()
                )
            )
            await session.commit()
            
        except Exception as e:
            logger.error(f"❌ Error enabling lottery entry: {e}")
            await session.rollback()

# Global instance
payment_flow_service = PaymentFlowService()
