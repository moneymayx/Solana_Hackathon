"""
GDPR Compliance Service for Billions Bounty AI Security Research Platform

Implements essential GDPR requirements:
- Right to erasure (Article 17)
- Right to data portability (Article 20)
- Consent management (Article 6)
- Data processing records (Article 30)
- Privacy by design (Article 25)
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import AsyncSessionLocal
from ..models import User, SecurityEvent, PaymentTransaction, Referral
from .encryption_service import EncryptionService

logger = logging.getLogger(__name__)

class ConsentType(Enum):
    """Types of consent for data processing"""
    ESSENTIAL = "essential"  # Required for service operation
    ANALYTICS = "analytics"  # Optional analytics data
    MARKETING = "marketing"  # Optional marketing communications
    RESEARCH = "research"    # Optional research data sharing

class DataCategory(Enum):
    """Categories of personal data"""
    IDENTITY = "identity"        # Name, email, user ID
    BEHAVIORAL = "behavioral"    # Chat history, AI interactions
    FINANCIAL = "financial"      # Payment data, wallet addresses
    TECHNICAL = "technical"      # IP addresses, device info
    RESEARCH = "research"        # AI research data, decisions

@dataclass
class ConsentRecord:
    """Record of user consent for data processing"""
    user_id: int
    consent_type: ConsentType
    granted: bool
    timestamp: datetime
    ip_address: str
    user_agent: str
    consent_text: str

@dataclass
class DataProcessingRecord:
    """Record of data processing activities"""
    purpose: str
    data_categories: List[DataCategory]
    legal_basis: str
    retention_period: int  # days
    data_subjects: str
    data_recipients: str
    transfers_outside_eu: bool
    safeguards: str

class GDPRComplianceService:
    """GDPR compliance service for the AI Security Research Platform"""
    
    def __init__(self):
        self.encryption_service = EncryptionService()
        self.data_retention_period = 7 * 365  # 7 years for research data
        self.breach_notification_days = 72  # 72 hours for breach notification
        
        # Data processing records
        self.processing_records = [
            DataProcessingRecord(
                purpose="AI Security Research Platform Operation",
                data_categories=[DataCategory.IDENTITY, DataCategory.BEHAVIORAL, DataCategory.TECHNICAL],
                legal_basis="Legitimate interest (AI security research)",
                retention_period=7 * 365,
                data_subjects="AI security researchers, users",
                data_recipients="Internal systems, Solana blockchain",
                transfers_outside_eu=True,
                safeguards="Standard contractual clauses, encryption"
            ),
            DataProcessingRecord(
                purpose="Payment Processing",
                data_categories=[DataCategory.FINANCIAL, DataCategory.IDENTITY],
                legal_basis="Contract performance",
                retention_period=7 * 365,
                data_subjects="Users making payments",
                data_recipients="Payment processors, Solana blockchain",
                transfers_outside_eu=True,
                safeguards="PCI DSS compliance, encryption"
            ),
            DataProcessingRecord(
                purpose="Research Data Analysis",
                data_categories=[DataCategory.RESEARCH, DataCategory.BEHAVIORAL],
                legal_basis="Consent",
                retention_period=7 * 365,
                data_subjects="Research participants",
                data_recipients="Research team, anonymized datasets",
                transfers_outside_eu=False,
                safeguards="Anonymization, pseudonymization"
            )
        ]
    
    async def handle_data_deletion_request(self, user_id: int, request_ip: str, user_agent: str) -> Dict[str, Any]:
        """
        GDPR Article 17 - Right to erasure (Right to be forgotten)
        
        Deletes all personal data for a user while preserving:
        - Anonymized research data
        - Legal compliance records
        - System integrity data
        """
        try:
            async with AsyncSessionLocal() as db:
                # Get user data before deletion
                user_data = await self._get_user_data_summary(db, user_id)
                
                # Log the deletion request
                await self._log_data_deletion_request(db, user_id, request_ip, user_agent)
                
                # Delete personal data
                deletion_results = await self._delete_user_personal_data(db, user_id)
                
                # Anonymize research data
                anonymization_results = await self._anonymize_research_data(db, user_id)
                
                # Generate deletion report
                deletion_report = {
                    "user_id": user_id,
                    "deletion_timestamp": datetime.utcnow().isoformat(),
                    "deleted_data": deletion_results,
                    "anonymized_data": anonymization_results,
                    "preserved_data": {
                        "anonymized_research": "Preserved for research purposes",
                        "legal_records": "Preserved for compliance",
                        "system_logs": "Preserved for security"
                    },
                    "gdpr_article": "Article 17 - Right to erasure",
                    "legal_basis": "User request for data deletion"
                }
                
                logger.info(f"GDPR data deletion completed for user {user_id}")
                return deletion_report
                
        except Exception as e:
            logger.error(f"GDPR data deletion failed for user {user_id}: {e}")
            raise
    
    async def export_user_data(self, user_id: int, request_ip: str, user_agent: str) -> Dict[str, Any]:
        """
        GDPR Article 20 - Right to data portability
        
        Exports all user data in a machine-readable format
        """
        try:
            async with AsyncSessionLocal() as db:
                # Get all user data
                user_data = await self._get_complete_user_data(db, user_id)
                
                # Log the export request
                await self._log_data_export_request(db, user_id, request_ip, user_agent)
                
                # Generate export package
                export_package = {
                    "user_id": user_id,
                    "export_timestamp": datetime.utcnow().isoformat(),
                    "data_categories": {
                        "identity": user_data.get("identity", {}),
                        "behavioral": user_data.get("behavioral", {}),
                        "financial": user_data.get("financial", {}),
                        "technical": user_data.get("technical", {}),
                        "research": user_data.get("research", {})
                    },
                    "gdpr_article": "Article 20 - Right to data portability",
                    "format": "JSON",
                    "encoding": "UTF-8"
                }
                
                logger.info(f"GDPR data export completed for user {user_id}")
                return export_package
                
        except Exception as e:
            logger.error(f"GDPR data export failed for user {user_id}: {e}")
            raise
    
    async def manage_consent(self, user_id: int, consent_type: ConsentType, granted: bool, 
                           request_ip: str, user_agent: str, consent_text: str) -> Dict[str, Any]:
        """
        GDPR Article 6 - Lawfulness of processing
        
        Manages user consent for different types of data processing
        """
        try:
            async with AsyncSessionLocal() as db:
                # Create consent record
                consent_record = ConsentRecord(
                    user_id=user_id,
                    consent_type=consent_type,
                    granted=granted,
                    timestamp=datetime.utcnow(),
                    ip_address=request_ip,
                    user_agent=user_agent,
                    consent_text=consent_text
                )
                
                # Store consent record
                await self._store_consent_record(db, consent_record)
                
                # Update user consent status
                await self._update_user_consent_status(db, user_id, consent_type, granted)
                
                # Log consent change
                await self._log_consent_change(db, user_id, consent_type, granted, request_ip)
                
                result = {
                    "user_id": user_id,
                    "consent_type": consent_type.value,
                    "granted": granted,
                    "timestamp": consent_record.timestamp.isoformat(),
                    "gdpr_article": "Article 6 - Lawfulness of processing",
                    "legal_basis": "Consent" if granted else "Withdrawn consent"
                }
                
                logger.info(f"GDPR consent updated for user {user_id}: {consent_type.value} = {granted}")
                return result
                
        except Exception as e:
            logger.error(f"GDPR consent management failed for user {user_id}: {e}")
            raise
    
    async def get_data_processing_records(self) -> List[Dict[str, Any]]:
        """
        GDPR Article 30 - Records of processing activities
        
        Returns records of all data processing activities
        """
        try:
            records = []
            for record in self.processing_records:
                records.append({
                    "purpose": record.purpose,
                    "data_categories": [cat.value for cat in record.data_categories],
                    "legal_basis": record.legal_basis,
                    "retention_period_days": record.retention_period,
                    "data_subjects": record.data_subjects,
                    "data_recipients": record.data_recipients,
                    "transfers_outside_eu": record.transfers_outside_eu,
                    "safeguards": record.safeguards,
                    "gdpr_article": "Article 30 - Records of processing activities"
                })
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to get data processing records: {e}")
            raise
    
    async def check_data_retention_compliance(self) -> Dict[str, Any]:
        """
        Check compliance with data retention periods
        """
        try:
            async with AsyncSessionLocal() as db:
                # Check for data older than retention period
                cutoff_date = datetime.utcnow() - timedelta(days=self.data_retention_period)
                
                # Get counts of old data
                result = await db.execute(
                    text("SELECT COUNT(*) FROM users WHERE created_at < :cutoff"),
                    {"cutoff": cutoff_date}
                )
                old_users = result.scalar()
                
                try:
                    result = await db.execute(
                        text("SELECT COUNT(*) FROM ai_decisions WHERE created_at < :cutoff"),
                        {"cutoff": cutoff_date}
                    )
                    old_decisions = result.scalar()
                except:
                    old_decisions = 0
                
                result = await db.execute(
                    text("SELECT COUNT(*) FROM payment_transactions WHERE created_at < :cutoff"),
                    {"cutoff": cutoff_date}
                )
                old_payments = result.scalar()
                
                compliance_report = {
                    "retention_period_days": self.data_retention_period,
                    "cutoff_date": cutoff_date.isoformat(),
                    "old_data_counts": {
                        "users": old_users,
                        "ai_decisions": old_decisions,
                        "payments": old_payments
                    },
                    "compliance_status": "COMPLIANT" if old_users == 0 else "NON_COMPLIANT",
                    "recommendations": [
                        "Review data retention policies",
                        "Implement automated data purging",
                        "Update privacy notices"
                    ] if old_users > 0 else []
                }
                
                return compliance_report
                
        except Exception as e:
            logger.error(f"Failed to check data retention compliance: {e}")
            raise
    
    async def _get_user_data_summary(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Get summary of user data before deletion"""
        try:
            # Get user basic info
            result = await db.execute(
                text("SELECT id, email, created_at FROM users WHERE id = :user_id"),
                {"user_id": user_id}
            )
            user = result.fetchone()
            
            if not user:
                return {}
            
            # Get data counts
            try:
                result = await db.execute(
                    text("SELECT COUNT(*) FROM ai_decisions WHERE user_id = :user_id"),
                    {"user_id": user_id}
                )
                decisions_count = result.scalar()
            except:
                decisions_count = 0
            
            result = await db.execute(
                text("SELECT COUNT(*) FROM payment_transactions WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            payments_count = result.scalar()
            
            return {
                "user_id": user.id,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "data_counts": {
                    "ai_decisions": decisions_count,
                    "payments": payments_count
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get user data summary: {e}")
            return {}
    
    async def _get_complete_user_data(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Get complete user data for export"""
        try:
            # Get user basic info
            result = await db.execute(
                text("SELECT * FROM users WHERE id = :user_id"),
                {"user_id": user_id}
            )
            user = result.fetchone()
            
            if not user:
                return {}
            
            # Get AI decisions (if table exists)
            try:
                result = await db.execute(
                    text("SELECT * FROM ai_decisions WHERE user_id = :user_id ORDER BY created_at"),
                    {"user_id": user_id}
                )
                decisions = result.fetchall()
            except:
                decisions = []
            
            # Get payments
            result = await db.execute(
                text("SELECT * FROM payment_transactions WHERE user_id = :user_id ORDER BY created_at"),
                {"user_id": user_id}
            )
            payments = result.fetchall()
            
            # Get security events
            result = await db.execute(
                text("SELECT * FROM security_events WHERE user_id = :user_id ORDER BY created_at"),
                {"user_id": user_id}
            )
            security_events = result.fetchall()
            
            return {
                "identity": {
                    "user_id": user.id,
                    "email": user.email,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None
                },
                "behavioral": {
                    "ai_decisions": [dict(decision) for decision in decisions],
                    "total_decisions": len(decisions)
                },
                "financial": {
                    "payments": [dict(payment) for payment in payments],
                    "total_payments": len(payments)
                },
                "technical": {
                    "security_events": [dict(event) for event in security_events],
                    "total_events": len(security_events)
                },
                "research": {
                    "research_data": "Anonymized research data preserved",
                    "data_retention": f"{self.data_retention_period} days"
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get complete user data: {e}")
            return {}
    
    async def _delete_user_personal_data(self, db: AsyncSession, user_id: int) -> Dict[str, int]:
        """Delete user's personal data"""
        try:
            deletion_counts = {}
            
            # Delete AI decisions (personal data) - if table exists
            try:
                result = await db.execute(
                    text("DELETE FROM ai_decisions WHERE user_id = :user_id"),
                    {"user_id": user_id}
                )
                deletion_counts["ai_decisions"] = result.rowcount
            except:
                deletion_counts["ai_decisions"] = 0
            
            # Delete payments (personal data)
            result = await db.execute(
                text("DELETE FROM payment_transactions WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            deletion_counts["payments"] = result.rowcount
            
            # Delete security events (personal data)
            result = await db.execute(
                text("DELETE FROM security_events WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            deletion_counts["security_events"] = result.rowcount
            
            # Anonymize user record (keep for system integrity)
            await db.execute(
                text("""
                    UPDATE users 
                    SET email = :anonymized_email, 
                        last_login = NULL,
                        updated_at = :now
                    WHERE id = :user_id
                """),
                {
                    "user_id": user_id,
                    "anonymized_email": f"deleted_user_{user_id}@anonymized.local",
                    "now": datetime.utcnow()
                }
            )
            
            await db.commit()
            return deletion_counts
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete user personal data: {e}")
            raise
    
    async def _anonymize_research_data(self, db: AsyncSession, user_id: int) -> Dict[str, int]:
        """Anonymize research data while preserving research value"""
        try:
            anonymization_counts = {}
            
            # Anonymize AI decisions for research - if table exists
            try:
                result = await db.execute(
                    text("""
                        UPDATE ai_decisions 
                        SET user_message = :anonymized_message,
                            ai_response = :anonymized_response,
                            user_id = :anonymized_user_id,
                            updated_at = :now
                        WHERE user_id = :user_id
                    """),
                    {
                        "user_id": user_id,
                        "anonymized_message": "[ANONYMIZED]",
                        "anonymized_response": "[ANONYMIZED]",
                        "anonymized_user_id": -1,  # Special anonymized user ID
                        "now": datetime.utcnow()
                    }
                )
                anonymization_counts["ai_decisions"] = result.rowcount
            except:
                anonymization_counts["ai_decisions"] = 0
            
            await db.commit()
            return anonymization_counts
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to anonymize research data: {e}")
            raise
    
    async def _log_data_deletion_request(self, db: AsyncSession, user_id: int, request_ip: str, user_agent: str):
        """Log data deletion request for audit trail"""
        try:
            await db.execute(
                text("""
                    INSERT INTO security_events 
                    (event_type, description, ip_address, user_agent, timestamp, severity)
                    VALUES (:event_type, :description, :ip_address, :user_agent, :now, :severity)
                """),
                {
                    "event_type": "GDPR_DATA_DELETION_REQUEST",
                    "description": f"User {user_id} requested data deletion under GDPR Article 17",
                    "ip_address": request_ip,
                    "user_agent": user_agent,
                    "now": datetime.utcnow(),
                    "severity": "INFO"
                }
            )
            await db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log data deletion request: {e}")
    
    async def _log_data_export_request(self, db: AsyncSession, user_id: int, request_ip: str, user_agent: str):
        """Log data export request for audit trail"""
        try:
            await db.execute(
                text("""
                    INSERT INTO security_events 
                    (event_type, description, ip_address, user_agent, timestamp, severity)
                    VALUES (:event_type, :description, :ip_address, :user_agent, :now, :severity)
                """),
                {
                    "event_type": "GDPR_DATA_EXPORT_REQUEST",
                    "description": f"User {user_id} requested data export under GDPR Article 20",
                    "ip_address": request_ip,
                    "user_agent": user_agent,
                    "now": datetime.utcnow(),
                    "severity": "INFO"
                }
            )
            await db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log data export request: {e}")
    
    async def _store_consent_record(self, db: AsyncSession, consent_record: ConsentRecord):
        """Store consent record in database"""
        try:
            await db.execute(
                text("""
                    INSERT INTO consent_records 
                    (user_id, consent_type, granted, timestamp, ip_address, user_agent, consent_text, created_at)
                    VALUES (:user_id, :consent_type, :granted, :timestamp, :ip_address, :user_agent, :consent_text, :now)
                """),
                {
                    "user_id": consent_record.user_id,
                    "consent_type": consent_record.consent_type.value,
                    "granted": consent_record.granted,
                    "timestamp": consent_record.timestamp,
                    "ip_address": consent_record.ip_address,
                    "user_agent": consent_record.user_agent,
                    "consent_text": consent_record.consent_text,
                    "now": datetime.utcnow()
                }
            )
            await db.commit()
            
        except Exception as e:
            logger.error(f"Failed to store consent record: {e}")
    
    async def _update_user_consent_status(self, db: AsyncSession, user_id: int, consent_type: ConsentType, granted: bool):
        """Update user's consent status"""
        try:
            # This would update a user consent table
            # For now, we'll log it as a security event
            await db.execute(
                text("""
                    INSERT INTO security_events 
                    (event_type, description, timestamp, severity)
                    VALUES (:event_type, :description, :now, :severity)
                """),
                {
                    "event_type": "GDPR_CONSENT_UPDATE",
                    "description": f"User {user_id} consent updated: {consent_type.value} = {granted}",
                    "now": datetime.utcnow(),
                    "severity": "INFO"
                }
            )
            await db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update user consent status: {e}")
    
    async def _log_consent_change(self, db: AsyncSession, user_id: int, consent_type: ConsentType, granted: bool, request_ip: str):
        """Log consent change for audit trail"""
        try:
            await db.execute(
                text("""
                    INSERT INTO security_events 
                    (event_type, description, ip_address, timestamp, severity)
                    VALUES (:event_type, :description, :ip_address, :now, :severity)
                """),
                {
                    "event_type": "GDPR_CONSENT_CHANGE",
                    "description": f"User {user_id} consent changed: {consent_type.value} = {granted}",
                    "ip_address": request_ip,
                    "now": datetime.utcnow(),
                    "severity": "INFO"
                }
            )
            await db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log consent change: {e}")
