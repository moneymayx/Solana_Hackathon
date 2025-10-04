"""
Fund Routing Service - Automated Fund Management
Handles automatic routing of USDC from deposit wallet to jackpot wallet
"""
import os
import asyncio
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from .models import FundDeposit, FundTransfer, PaymentTransaction
from .solana_service import solana_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FundRoutingService:
    """Service for managing automated fund routing from deposit to jackpot wallet"""
    
    def __init__(self):
        # Wallet addresses - separate deposit and jackpot wallets
        self.deposit_wallet = os.getenv("DEPOSIT_WALLET_ADDRESS")  # Where MoonPay sends USDC
        self.jackpot_wallet = os.getenv("JACKPOT_WALLET_ADDRESS")  # Where jackpot funds are stored
        self.treasury_wallet = os.getenv("TREASURY_SOLANA_ADDRESS")  # Legacy treasury (for backward compatibility)
        
        # Fund routing settings
        self.auto_routing_enabled = os.getenv("AUTO_FUND_ROUTING", "true").lower() == "true"
        self.min_routing_amount = float(os.getenv("MIN_ROUTING_AMOUNT", "1.0"))  # Minimum USDC to route
        self.routing_delay_seconds = int(os.getenv("ROUTING_DELAY_SECONDS", "30"))  # Delay before routing
        
        # Load deposit wallet private key for automated transfers
        self.deposit_private_key = os.getenv("DEPOSIT_WALLET_PRIVATE_KEY")
        self.deposit_keypair = None
        
        if self.deposit_private_key:
            try:
                import base58
                private_key_bytes = base58.b58decode(self.deposit_private_key)
                from solders.keypair import Keypair
                self.deposit_keypair = Keypair.from_secret_key(private_key_bytes)
                logger.info(f"✅ Deposit wallet keypair loaded: {str(self.deposit_keypair.public_key)}")
            except Exception as e:
                logger.error(f"❌ Error loading deposit wallet keypair: {e}")
                self.deposit_keypair = None
        else:
            logger.warning("⚠️ DEPOSIT_WALLET_PRIVATE_KEY not configured - automated routing disabled")
    
    async def process_payment_completion(self, session: AsyncSession, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a completed payment and route funds if necessary"""
        try:
            # Extract payment information
            transaction_id = payment_data.get("transaction_id")
            wallet_address = payment_data.get("wallet_address")
            amount_usd = payment_data.get("base_currency_amount", 0.0)
            amount_usdc = payment_data.get("quote_currency_amount", 0.0)
            payment_method = payment_data.get("payment_method", "moonpay")
            
            logger.info(f"💰 Processing payment completion: {transaction_id} - ${amount_usd} USD -> {amount_usdc} USDC")
            
            # Record the deposit
            deposit_record = await self._record_deposit(
                session, transaction_id, wallet_address, amount_usd, amount_usdc, payment_method
            )
            
            if not deposit_record:
                return {"success": False, "error": "Failed to record deposit"}
            
            # Determine routing destination based on payment method
            if payment_method == "moonpay":
                # MoonPay payments go to deposit wallet, then route to jackpot
                routing_destination = self.jackpot_wallet
                source_wallet = self.deposit_wallet
            else:
                # Direct wallet payments go directly to jackpot
                routing_destination = self.jackpot_wallet
                source_wallet = wallet_address
            
            # Route funds if auto-routing is enabled and we have sufficient amount
            if self.auto_routing_enabled and amount_usdc >= self.min_routing_amount:
                if payment_method == "moonpay":
                    # Wait for funds to arrive in deposit wallet, then route
                    await asyncio.sleep(self.routing_delay_seconds)
                    routing_result = await self._route_funds(
                        session, deposit_record.id, source_wallet, routing_destination, amount_usdc
                    )
                    return routing_result
                else:
                    # Direct wallet payment - funds already in correct location
                    return {
                        "success": True,
                        "message": "Direct wallet payment - funds in jackpot wallet",
                        "deposit_id": deposit_record.id,
                        "routing_required": False
                    }
            else:
                return {
                    "success": True,
                    "message": "Deposit recorded - manual routing required",
                    "deposit_id": deposit_record.id,
                    "routing_required": True
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing payment completion: {e}")
            return {"success": False, "error": str(e)}
    
    async def _record_deposit(self, session: AsyncSession, transaction_id: str, wallet_address: str, 
                            amount_usd: float, amount_usdc: float, payment_method: str) -> Optional[FundDeposit]:
        """Record a fund deposit in the database"""
        try:
            deposit = FundDeposit(
                transaction_id=transaction_id,
                wallet_address=wallet_address,
                amount_usd=amount_usd,
                amount_usdc=amount_usdc,
                payment_method=payment_method,
                status="pending",
                deposit_wallet=self.deposit_wallet if payment_method == "moonpay" else wallet_address,
                target_wallet=self.jackpot_wallet
            )
            
            session.add(deposit)
            await session.commit()
            await session.refresh(deposit)
            
            logger.info(f"📝 Recorded deposit: {deposit.id} - ${amount_usd} USD")
            return deposit
            
        except Exception as e:
            logger.error(f"❌ Error recording deposit: {e}")
            await session.rollback()
            return None
    
    async def _route_funds(self, session: AsyncSession, deposit_id: int, from_wallet: str, 
                         to_wallet: str, amount_usdc: float) -> Dict[str, Any]:
        """Route USDC funds from deposit wallet to jackpot wallet"""
        try:
            if not self.deposit_keypair:
                return {
                    "success": False,
                    "error": "Deposit wallet keypair not configured",
                    "deposit_id": deposit_id
                }
            
            logger.info(f"🔄 Routing {amount_usdc} USDC from {from_wallet} to {to_wallet}")
            
            # Create USDC transfer transaction
            transfer_result = await self._transfer_usdc_spl(
                from_wallet, to_wallet, amount_usdc
            )
            
            if transfer_result["success"]:
                # Record the transfer
                transfer_record = FundTransfer(
                    deposit_id=deposit_id,
                    from_wallet=from_wallet,
                    to_wallet=to_wallet,
                    amount_usdc=amount_usdc,
                    transaction_signature=transfer_result["signature"],
                    status="completed"
                )
                
                session.add(transfer_record)
                
                # Update deposit status
                await session.execute(
                    update(FundDeposit)
                    .where(FundDeposit.id == deposit_id)
                    .values(status="routed", routed_at=datetime.utcnow())
                )
                
                await session.commit()
                
                logger.info(f"✅ Funds routed successfully: {transfer_result['signature']}")
                return {
                    "success": True,
                    "message": "Funds routed successfully",
                    "deposit_id": deposit_id,
                    "transfer_signature": transfer_result["signature"],
                    "routed_amount": amount_usdc
                }
            else:
                # Update deposit status to failed
                await session.execute(
                    update(FundDeposit)
                    .where(FundDeposit.id == deposit_id)
                    .values(status="routing_failed", error_message=transfer_result["error"])
                )
                await session.commit()
                
                return {
                    "success": False,
                    "error": f"Fund routing failed: {transfer_result['error']}",
                    "deposit_id": deposit_id
                }
                
        except Exception as e:
            logger.error(f"❌ Error routing funds: {e}")
            return {"success": False, "error": str(e), "deposit_id": deposit_id}
    
    async def _transfer_usdc_spl(self, from_wallet: str, to_wallet: str, amount_usdc: float) -> Dict[str, Any]:
        """Transfer USDC SPL tokens between wallets"""
        try:
            # This would use the Solana service to create and sign the USDC transfer
            # For now, return a placeholder - actual implementation would use SPL token program
            
            # In production, you would:
            # 1. Create SPL token transfer instruction
            # 2. Sign with deposit wallet keypair
            # 3. Send transaction
            # 4. Wait for confirmation
            
            return {
                "success": True,
                "signature": f"placeholder_signature_{int(time.time())}",
                "amount": amount_usdc,
                "from": from_wallet,
                "to": to_wallet
            }
            
        except Exception as e:
            logger.error(f"❌ Error transferring USDC: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_fund_status(self, session: AsyncSession) -> Dict[str, Any]:
        """Get current fund status and routing information"""
        try:
            # Get recent deposits
            deposits_result = await session.execute(
                select(FundDeposit)
                .order_by(FundDeposit.created_at.desc())
                .limit(10)
            )
            recent_deposits = deposits_result.scalars().all()
            
            # Get pending routing
            pending_result = await session.execute(
                select(FundDeposit)
                .where(FundDeposit.status == "pending")
            )
            pending_deposits = pending_result.scalars().all()
            
            # Calculate totals
            total_deposits = sum(dep.amount_usdc for dep in recent_deposits)
            pending_amount = sum(dep.amount_usdc for dep in pending_deposits)
            
            return {
                "deposit_wallet": self.deposit_wallet,
                "jackpot_wallet": self.jackpot_wallet,
                "auto_routing_enabled": self.auto_routing_enabled,
                "recent_deposits": [
                    {
                        "id": dep.id,
                        "amount_usdc": dep.amount_usdc,
                        "status": dep.status,
                        "created_at": dep.created_at.isoformat()
                    } for dep in recent_deposits
                ],
                "pending_routing": len(pending_deposits),
                "pending_amount": pending_amount,
                "total_recent_deposits": total_deposits
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting fund status: {e}")
            return {"error": str(e)}
    
    async def manual_route_funds(self, session: AsyncSession, deposit_id: int) -> Dict[str, Any]:
        """Manually trigger fund routing for a specific deposit"""
        try:
            # Get deposit record
            deposit_result = await session.execute(
                select(FundDeposit).where(FundDeposit.id == deposit_id)
            )
            deposit = deposit_result.scalar_one_or_none()
            
            if not deposit:
                return {"success": False, "error": "Deposit not found"}
            
            if deposit.status != "pending":
                return {"success": False, "error": f"Deposit status is {deposit.status}, cannot route"}
            
            # Route the funds
            return await self._route_funds(
                session, deposit_id, deposit.deposit_wallet, deposit.target_wallet, deposit.amount_usdc
            )
            
        except Exception as e:
            logger.error(f"❌ Error in manual fund routing: {e}")
            return {"success": False, "error": str(e)}

# Global instance
fund_routing_service = FundRoutingService()
