"""
KYC Service - Handles KYC data processing and compliance tracking
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, desc
from .models import User, PaymentTransaction, EmailVerification

class KYCService:
    """Service for managing KYC data and compliance"""
    
    def __init__(self):
        self.kyc_providers = ["moonpay", "manual", "stripe"]
        self.kyc_statuses = ["pending", "verified", "rejected", "expired", "under_review"]
    
    async def process_moonpay_kyc_data(self, session: AsyncSession, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process KYC data from MoonPay webhook"""
        try:
            # Extract KYC data from MoonPay webhook
            transaction_id = webhook_data.get("data", {}).get("id")
            wallet_address = webhook_data.get("data", {}).get("walletAddress")
            status = webhook_data.get("data", {}).get("status")
            
            # Find user by wallet address
            user = await self._get_user_by_wallet(session, wallet_address)
            if not user:
                return {
                    "success": False,
                    "error": f"User not found for wallet: {wallet_address}"
                }
            
            # Extract KYC information from MoonPay data
            kyc_data = self._extract_moonpay_kyc_data(webhook_data)
            
            # Update user KYC information
            await self._update_user_kyc(session, user.id, kyc_data, "moonpay", transaction_id)
            
            # Update payment transaction with KYC status
            await self._update_payment_transaction_kyc(session, transaction_id, kyc_data)
            
            # Log KYC event
            await self._log_kyc_event(session, user.id, "moonpay_kyc_processed", kyc_data)
            
            return {
                "success": True,
                "message": "KYC data processed successfully",
                "user_id": user.id,
                "kyc_status": kyc_data.get("kyc_status", "pending")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process KYC data: {str(e)}"
            }
    
    def _extract_moonpay_kyc_data(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract KYC data from MoonPay webhook payload"""
        data = webhook_data.get("data", {})
        
        # Extract customer information
        customer = data.get("customer", {})
        
        kyc_data = {
            "full_name": customer.get("firstName", "") + " " + customer.get("lastName", ""),
            "date_of_birth": self._parse_date(customer.get("dateOfBirth")),
            "phone_number": customer.get("phone", {}).get("number", ""),
            "address": self._format_address(customer.get("address", {})),
            "email": customer.get("email", ""),
            "kyc_status": self._map_moonpay_status(data.get("status")),
            "kyc_provider": "moonpay",
            "kyc_reference_id": data.get("id"),
            "kyc_data": json.dumps({
                "moonpay_customer_id": customer.get("id"),
                "verification_level": data.get("verificationLevel"),
                "compliance_tier": data.get("complianceTier"),
                "risk_level": data.get("riskLevel"),
                "kyc_verification_date": data.get("verificationDate"),
                "document_verification": data.get("documentVerification", {}),
                "address_verification": data.get("addressVerification", {}),
                "phone_verification": data.get("phoneVerification", {})
            })
        }
        
        return kyc_data
    
    def _map_moonpay_status(self, moonpay_status: str) -> str:
        """Map MoonPay status to our KYC status"""
        status_mapping = {
            "completed": "verified",
            "pending": "pending",
            "failed": "rejected",
            "expired": "expired",
            "cancelled": "rejected"
        }
        return status_mapping.get(moonpay_status, "pending")
    
    def _parse_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_string:
            return None
        
        try:
            # Try different date formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
                try:
                    return datetime.strptime(date_string, fmt)
                except ValueError:
                    continue
            return None
        except:
            return None
    
    def _format_address(self, address_data: Dict[str, Any]) -> str:
        """Format address data into string"""
        if not address_data:
            return ""
        
        parts = [
            address_data.get("addressLine1", ""),
            address_data.get("addressLine2", ""),
            address_data.get("city", ""),
            address_data.get("state", ""),
            address_data.get("postalCode", ""),
            address_data.get("country", "")
        ]
        
        return ", ".join(filter(None, parts))
    
    async def _get_user_by_wallet(self, session: AsyncSession, wallet_address: str) -> Optional[User]:
        """Get user by wallet address"""
        result = await session.execute(
            select(User).where(User.wallet_address == wallet_address)
        )
        return result.scalar_one_or_none()
    
    async def _update_user_kyc(self, session: AsyncSession, user_id: int, kyc_data: Dict[str, Any], 
                              provider: str, reference_id: str) -> None:
        """Update user KYC information"""
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                full_name=kyc_data.get("full_name"),
                date_of_birth=kyc_data.get("date_of_birth"),
                phone_number=kyc_data.get("phone_number"),
                address=kyc_data.get("address"),
                kyc_status=kyc_data.get("kyc_status", "pending"),
                kyc_provider=provider,
                kyc_reference_id=reference_id
            )
        )
        await session.commit()
    
    async def _update_payment_transaction_kyc(self, session: AsyncSession, transaction_id: str, 
                                            kyc_data: Dict[str, Any]) -> None:
        """Update payment transaction with KYC information"""
        await session.execute(
            update(PaymentTransaction)
            .where(PaymentTransaction.moonpay_tx_id == transaction_id)
            .values(
                extra_data=json.dumps({
                    "kyc_status": kyc_data.get("kyc_status"),
                    "kyc_provider": kyc_data.get("kyc_provider"),
                    "kyc_verification_date": datetime.utcnow().isoformat()
                })
            )
        )
        await session.commit()
    
    async def _log_kyc_event(self, session: AsyncSession, user_id: int, event_type: str, 
                           event_data: Dict[str, Any]) -> None:
        """Log KYC-related events"""
        # This would integrate with your existing security event logging
        # For now, we'll just print the event
        print(f"KYC Event: {event_type} for user {user_id}: {event_data}")
    
    async def get_kyc_status(self, session: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Get user's KYC status and information"""
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {
                "success": False,
                "error": "User not found"
            }
        
        return {
            "success": True,
            "kyc_status": user.kyc_status,
            "kyc_provider": user.kyc_provider,
            "kyc_reference_id": user.kyc_reference_id,
            "full_name": user.full_name,
            "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
            "phone_number": user.phone_number,
            "address": user.address,
            "is_verified": user.is_verified
        }
    
    async def get_kyc_statistics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get KYC statistics for admin dashboard"""
        # Get total users
        total_users_result = await session.execute(select(User))
        total_users = len(total_users_result.scalars().all())
        
        # Get KYC status counts
        kyc_stats = {}
        for status in self.kyc_statuses:
            result = await session.execute(
                select(User).where(User.kyc_status == status)
            )
            kyc_stats[status] = len(result.scalars().all())
        
        # Get provider counts
        provider_stats = {}
        for provider in self.kyc_providers:
            result = await session.execute(
                select(User).where(User.kyc_provider == provider)
            )
            provider_stats[provider] = len(result.scalars().all())
        
        return {
            "total_users": total_users,
            "kyc_status_breakdown": kyc_stats,
            "provider_breakdown": provider_stats,
            "verification_rate": (kyc_stats.get("verified", 0) / total_users * 100) if total_users > 0 else 0
        }
    
    async def get_pending_kyc_reviews(self, session: AsyncSession, limit: int = 50) -> List[Dict[str, Any]]:
        """Get users pending KYC review"""
        result = await session.execute(
            select(User)
            .where(User.kyc_status.in_(["pending", "under_review"]))
            .order_by(desc(User.created_at))
            .limit(limit)
        )
        
        users = result.scalars().all()
        
        return [
            {
                "user_id": user.id,
                "email": user.email,
                "wallet_address": user.wallet_address,
                "full_name": user.full_name,
                "kyc_status": user.kyc_status,
                "kyc_provider": user.kyc_provider,
                "created_at": user.created_at.isoformat(),
                "last_active": user.last_active.isoformat()
            }
            for user in users
        ]
    
    async def update_kyc_status(self, session: AsyncSession, user_id: int, 
                              new_status: str, admin_notes: Optional[str] = None) -> Dict[str, Any]:
        """Update user's KYC status (admin function)"""
        if new_status not in self.kyc_statuses:
            return {
                "success": False,
                "error": f"Invalid KYC status: {new_status}"
            }
        
        # Update user KYC status
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(kyc_status=new_status)
        )
        
        # Log the status change
        await self._log_kyc_event(session, user_id, "kyc_status_updated", {
            "new_status": new_status,
            "admin_notes": admin_notes,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        await session.commit()
        
        return {
            "success": True,
            "message": f"KYC status updated to {new_status}",
            "user_id": user_id,
            "new_status": new_status
        }

# Global instance
kyc_service = KYCService()
