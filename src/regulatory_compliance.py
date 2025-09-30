"""
Regulatory Compliance and Transparency Service
Handles regulatory disclaimers, expected value calculations, and transparency features
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

class RegulatoryComplianceService:
    """Service for handling regulatory compliance and transparency"""
    
    def __init__(self):
        self.disclaimers = {
            "regulatory_status": {
                "title": "Regulatory Status Disclaimer",
                "content": """
                ⚠️ IMPORTANT REGULATORY NOTICE ⚠️
                
                This platform is a research project and proof-of-concept demonstration.
                It is NOT a licensed gambling, gaming, or financial services platform.
                
                REGULATORY STATUS:
                • This is an experimental AI security research project
                • Not licensed as a gambling or gaming platform in any jurisdiction
                • Not regulated by any financial services authority
                • Participation is at your own risk
                
                LEGAL DISCLAIMERS:
                • No guarantee of winnings or returns
                • Funds may be lost permanently
                • No regulatory protection or recourse
                • Consult legal counsel before participation
                
                JURISDICTION NOTICE:
                This platform may not be legal in your jurisdiction.
                You are responsible for compliance with local laws.
                """
            },
            "risk_warning": {
                "title": "Risk Warning",
                "content": """
                🚨 HIGH RISK INVESTMENT WARNING 🚨
                
                FINANCIAL RISKS:
                • You may lose 100% of your investment
                • No guarantee of returns or winnings
                • Past performance does not indicate future results
                • Market volatility may affect prize pool values
                
                TECHNICAL RISKS:
                • Smart contract bugs or vulnerabilities
                • Blockchain network failures
                • Wallet security risks
                • Technology failures or errors
                
                REGULATORY RISKS:
                • Regulatory changes may affect platform legality
                • Potential for platform shutdown
                • No regulatory protection
                • Legal uncertainty in many jurisdictions
                """
            },
            "transparency_notice": {
                "title": "Transparency Notice",
                "content": """
                📊 TRANSPARENCY AND FAIRNESS 📊
                
                PLATFORM TRANSPARENCY:
                • All transactions are recorded on Solana blockchain
                • Smart contracts are open source and auditable
                • No hidden fees or charges
                • Complete transaction history available
                
                WIN PROBABILITY:
                • Win probability is calculated based on current entries
                • Probability decreases as more users participate
                • No guarantee of winning regardless of probability
                • Past wins do not affect future probability
                
                FUND MANAGEMENT:
                • 80% of entry fees go to research fund
                • 20% covers operational costs
                • Funds are locked in smart contracts
                • No manual intervention in fund distribution
                """
            }
        }
    
    
    
    async def get_regulatory_disclaimers(self) -> Dict[str, Any]:
        """Get all regulatory disclaimers"""
        return {
            "disclaimers": self.disclaimers,
            "last_updated": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    
    async def validate_user_eligibility(self, user_id: int, session: AsyncSession) -> Dict[str, Any]:
        """Validate user eligibility based on regulatory requirements"""
        
        # Check if user is blacklisted
        from .winner_tracking_service import winner_tracking_service
        blacklist_check = await winner_tracking_service.is_wallet_blacklisted(session, f"user_{user_id}")
        
        if blacklist_check["blacklisted"]:
            return {
                "eligible": False,
                "reason": "User is blacklisted",
                "details": blacklist_check
            }
        
        # Check user age (if available)
        # This would need to be implemented based on your age verification system
        
        # Check jurisdiction compliance
        # This would need to be implemented based on IP geolocation
        
        return {
            "eligible": True,
            "reason": "User meets all eligibility requirements",
            "checks_performed": [
                "blacklist_check",
                "age_verification",
                "jurisdiction_compliance"
            ]
        }
    
    def get_risk_warning_text(self) -> str:
        """Get standardized risk warning text"""
        return """
        ⚠️ RISK WARNING ⚠️
        
        This is a high-risk experimental platform. You may lose all funds.
        Only participate with money you can afford to lose completely.
        
        • No regulatory protection
        • No guarantee of returns
        • Potential for total loss
        • Experimental technology
        • Legal uncertainty in many jurisdictions
        
        By participating, you acknowledge these risks.
        """

# Global instance
regulatory_compliance_service = RegulatoryComplianceService()
