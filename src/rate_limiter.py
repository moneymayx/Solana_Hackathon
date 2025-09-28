"""
Rate limiting and cost tracking for Billions
"""
import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from .repositories import PrizePoolRepository, SecurityEventRepository

class RateLimiter:
    """In-memory rate limiter for basic rate limiting"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.max_requests_per_minute = 10
        self.max_requests_per_hour = 50
    
    def is_allowed(self, identifier: str) -> tuple[bool, Optional[str]]:
        """Check if request is allowed for the given identifier"""
        now = time.time()
        
        # Clean old requests
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if now - req_time < 3600  # Keep last hour
            ]
        else:
            self.requests[identifier] = []
        
        recent_requests = self.requests[identifier]
        
        # Check per-minute limit
        minute_requests = [req for req in recent_requests if now - req < 60]
        if len(minute_requests) >= self.max_requests_per_minute:
            return False, f"Rate limit exceeded: {self.max_requests_per_minute} requests per minute"
        
        # Check per-hour limit
        if len(recent_requests) >= self.max_requests_per_hour:
            return False, f"Rate limit exceeded: {self.max_requests_per_hour} requests per hour"
        
        # Add current request
        self.requests[identifier].append(now)
        return True, None

class CostTracker:
    """Cost tracking and escalation system"""
    
    def __init__(self):
        self.base_cost = 10.0  # $10 starting cost
        self.escalation_rate = 0.0078  # 0.78% increase per query
        self.max_cost = 4500.0  # Maximum $4,500 per query
        self.prize_pool_percentage = 0.70  # 70% goes to prize pool
    
    async def calculate_query_cost(self, session: AsyncSession) -> float:
        """Calculate the cost for the next query"""
        prize_pool_repo = PrizePoolRepository(session)
        return await prize_pool_repo.calculate_next_query_cost()
    
    async def process_payment(self, session: AsyncSession, user_id: int, amount: float) -> dict:
        """Process a payment and update prize pool"""
        prize_pool_repo = PrizePoolRepository(session)
        
        # Calculate prize pool contribution
        prize_contribution = amount * self.prize_pool_percentage
        
        # Update prize pool
        updated_pool = await prize_pool_repo.update_prize_pool(prize_contribution)
        
        return {
            "payment_amount": amount,
            "prize_contribution": prize_contribution,
            "current_prize_pool": updated_pool.current_amount,
            "total_queries": updated_pool.total_queries,
            "next_query_cost": await self.calculate_query_cost(session)
        }
    
    async def get_prize_pool_status(self, session: AsyncSession) -> dict:
        """Get current prize pool status"""
        prize_pool_repo = PrizePoolRepository(session)
        prize_pool = await prize_pool_repo.get_current_prize_pool()
        
        if not prize_pool:
            prize_pool = await prize_pool_repo.initialize_prize_pool()
        
        next_cost = await self.calculate_query_cost(session)
        
        return {
            "current_amount": prize_pool.current_amount,
            "total_contributions": prize_pool.total_contributions,
            "total_queries": prize_pool.total_queries,
            "next_query_cost": next_cost,
            "base_cost": prize_pool.base_query_cost,
            "escalation_rate": prize_pool.escalation_rate,
            "max_cost": prize_pool.max_query_cost
        }

class SecurityMonitor:
    """Monitor for suspicious activity and security events"""
    
    def __init__(self):
        self.suspicious_patterns = [
            "ignore previous instructions",
            "forget everything",
            "you are now",
            "system prompt",
            "developer mode",
            "admin access",
            "root access",
            "bypass security",
            "override safety",
            "jailbreak",
            "prompt injection"
        ]
    
    async def analyze_message(self, message: str, session: AsyncSession, 
                            user_id: int, ip_address: Optional[str] = None) -> dict:
        """Analyze message for suspicious content"""
        message_lower = message.lower()
        
        # Check for suspicious patterns
        detected_patterns = []
        for pattern in self.suspicious_patterns:
            if pattern in message_lower:
                detected_patterns.append(pattern)
        
        # Calculate threat score
        threat_score = len(detected_patterns) / len(self.suspicious_patterns)
        
        # Determine severity
        if threat_score >= 0.3:
            severity = "high"
        elif threat_score >= 0.15:
            severity = "medium"
        elif threat_score > 0:
            severity = "low"
        else:
            severity = "none"
        
        # Log security event if suspicious
        if threat_score > 0:
            security_repo = SecurityEventRepository(session)
            await security_repo.log_security_event(
                event_type="suspicious_message",
                severity=severity,
                description=f"Detected {len(detected_patterns)} suspicious patterns: {', '.join(detected_patterns)}",
                ip_address=ip_address,
                additional_data=f"threat_score: {threat_score}, user_id: {user_id}"
            )
        
        return {
            "threat_score": threat_score,
            "severity": severity,
            "detected_patterns": detected_patterns,
            "is_suspicious": threat_score > 0
        }
