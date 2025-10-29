"""
Advanced Rate Limiter - User-specific rate limiting with sliding window and abuse detection
"""
import time
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import logging
from collections import defaultdict, deque
import redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from ..models import SecurityEvent

logger = logging.getLogger(__name__)

class RateLimitType(Enum):
    """Types of rate limiting"""
    API_CALLS = "api_calls"
    CHAT_MESSAGES = "chat_messages"
    PAYMENT_ATTEMPTS = "payment_attempts"
    LOGIN_ATTEMPTS = "login_attempts"
    WALLET_CONNECTIONS = "wallet_connections"
    AI_DECISION_REQUESTS = "ai_decision_requests"

@dataclass
class RateLimitRule:
    """Rate limit rule configuration"""
    limit_type: RateLimitType
    max_requests: int
    time_window: int  # seconds
    burst_limit: int  # max requests in burst
    user_specific: bool = True
    ip_specific: bool = True
    session_specific: bool = True

@dataclass
class RateLimitStatus:
    """Current rate limit status"""
    is_limited: bool
    remaining_requests: int
    reset_time: float
    limit_type: RateLimitType
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    session_id: Optional[str] = None
    reason: str = ""

@dataclass
class AbusePattern:
    """Detected abuse pattern"""
    pattern_type: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    detected_at: float
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class SlidingWindowRateLimiter:
    """Sliding window rate limiter implementation"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    def is_allowed(self) -> Tuple[bool, int]:
        """Check if request is allowed and return remaining count"""
        now = time.time()
        
        # Remove old requests outside time window
        while self.requests and self.requests[0] <= now - self.time_window:
            self.requests.popleft()
        
        # Check if under limit
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True, self.max_requests - len(self.requests)
        else:
            return False, 0
    
    def get_reset_time(self) -> float:
        """Get time when rate limit resets"""
        if not self.requests:
            return time.time()
        return self.requests[0] + self.time_window

class AdvancedRateLimiter:
    """Advanced rate limiter with multiple strategies and abuse detection"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.memory_limits = defaultdict(lambda: defaultdict(lambda: SlidingWindowRateLimiter(100, 3600)))
        
        # Rate limit rules
        self.rules = {
            RateLimitType.API_CALLS: RateLimitRule(
                limit_type=RateLimitType.API_CALLS,
                max_requests=1000,  # 1000 requests per hour
                time_window=3600,
                burst_limit=50,  # 50 requests in 1 minute
                user_specific=True,
                ip_specific=True,
                session_specific=True
            ),
            RateLimitType.CHAT_MESSAGES: RateLimitRule(
                limit_type=RateLimitType.CHAT_MESSAGES,
                max_requests=100,  # 100 messages per hour
                time_window=3600,
                burst_limit=10,  # 10 messages in 1 minute
                user_specific=True,
                ip_specific=True,
                session_specific=True
            ),
            RateLimitType.PAYMENT_ATTEMPTS: RateLimitRule(
                limit_type=RateLimitType.PAYMENT_ATTEMPTS,
                max_requests=10,  # 10 payment attempts per hour
                time_window=3600,
                burst_limit=3,  # 3 attempts in 5 minutes
                user_specific=True,
                ip_specific=True,
                session_specific=True
            ),
            RateLimitType.LOGIN_ATTEMPTS: RateLimitRule(
                limit_type=RateLimitType.LOGIN_ATTEMPTS,
                max_requests=5,  # 5 login attempts per hour
                time_window=3600,
                burst_limit=3,  # 3 attempts in 10 minutes
                user_specific=False,  # IP-based only
                ip_specific=True,
                session_specific=False
            ),
            RateLimitType.WALLET_CONNECTIONS: RateLimitRule(
                limit_type=RateLimitType.WALLET_CONNECTIONS,
                max_requests=20,  # 20 wallet connections per hour
                time_window=3600,
                burst_limit=5,  # 5 connections in 5 minutes
                user_specific=True,
                ip_specific=True,
                session_specific=True
            ),
            RateLimitType.AI_DECISION_REQUESTS: RateLimitRule(
                limit_type=RateLimitType.AI_DECISION_REQUESTS,
                max_requests=50,  # 50 AI decision requests per hour
                time_window=3600,
                burst_limit=10,  # 10 requests in 5 minutes
                user_specific=True,
                ip_specific=True,
                session_specific=True
            )
        }
        
        # Abuse detection patterns
        self.abuse_patterns = {
            "rapid_fire": {"threshold": 10, "window": 60, "severity": "high"},
            "burst_requests": {"threshold": 50, "window": 300, "severity": "medium"},
            "sustained_high": {"threshold": 200, "window": 3600, "severity": "high"},
            "pattern_repetition": {"threshold": 5, "window": 1800, "severity": "medium"},
            "unusual_timing": {"threshold": 3, "window": 3600, "severity": "low"}
        }
    
    async def check_rate_limit(
        self,
        limit_type: RateLimitType,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
        request_metadata: Optional[Dict[str, Any]] = None
    ) -> RateLimitStatus:
        """Check if request is within rate limits"""
        
        rule = self.rules[limit_type]
        
        # Check user-specific limits
        if rule.user_specific and user_id:
            user_allowed, user_remaining = await self._check_user_limit(
                limit_type, user_id, rule
            )
            if not user_allowed:
                return RateLimitStatus(
                    is_limited=True,
                    remaining_requests=0,
                    reset_time=time.time() + rule.time_window,
                    limit_type=limit_type,
                    user_id=user_id,
                    reason=f"User rate limit exceeded: {limit_type.value}"
                )
        
        # Check IP-specific limits
        if rule.ip_specific and ip_address:
            ip_allowed, ip_remaining = await self._check_ip_limit(
                limit_type, ip_address, rule
            )
            if not ip_allowed:
                return RateLimitStatus(
                    is_limited=True,
                    remaining_requests=0,
                    reset_time=time.time() + rule.time_window,
                    limit_type=limit_type,
                    ip_address=ip_address,
                    reason=f"IP rate limit exceeded: {limit_type.value}"
                )
        
        # Check session-specific limits
        if rule.session_specific and session_id:
            session_allowed, session_remaining = await self._check_session_limit(
                limit_type, session_id, rule
            )
            if not session_allowed:
                return RateLimitStatus(
                    is_limited=True,
                    remaining_requests=0,
                    reset_time=time.time() + rule.time_window,
                    limit_type=limit_type,
                    session_id=session_id,
                    reason=f"Session rate limit exceeded: {limit_type.value}"
                )
        
        # Check burst limits
        burst_allowed = await self._check_burst_limit(
            limit_type, user_id, ip_address, session_id, rule
        )
        if not burst_allowed:
            return RateLimitStatus(
                is_limited=True,
                remaining_requests=0,
                reset_time=time.time() + 60,  # 1 minute burst window
                limit_type=limit_type,
                user_id=user_id,
                ip_address=ip_address,
                session_id=session_id,
                reason=f"Burst rate limit exceeded: {limit_type.value}"
            )
        
        # Record request for abuse detection
        await self._record_request(
            limit_type, user_id, ip_address, session_id, request_metadata
        )
        
        # Check for abuse patterns
        abuse_detected = await self._detect_abuse_patterns(
            limit_type, user_id, ip_address, session_id
        )
        
        if abuse_detected:
            return RateLimitStatus(
                is_limited=True,
                remaining_requests=0,
                reset_time=time.time() + 3600,  # 1 hour block
                limit_type=limit_type,
                user_id=user_id,
                ip_address=ip_address,
                session_id=session_id,
                reason=f"Abuse pattern detected: {abuse_detected.pattern_type}"
            )
        
        # Calculate remaining requests
        remaining = min(
            user_remaining if user_id else rule.max_requests,
            ip_remaining if ip_address else rule.max_requests,
            session_remaining if session_id else rule.max_requests
        )
        
        return RateLimitStatus(
            is_limited=False,
            remaining_requests=remaining,
            reset_time=time.time() + rule.time_window,
            limit_type=limit_type,
            user_id=user_id,
            ip_address=ip_address,
            session_id=session_id,
            reason="Request allowed"
        )
    
    async def _check_user_limit(
        self, limit_type: RateLimitType, user_id: int, rule: RateLimitRule
    ) -> Tuple[bool, int]:
        """Check user-specific rate limit"""
        key = f"rate_limit:user:{limit_type.value}:{user_id}"
        return await self._check_limit(key, rule.max_requests, rule.time_window)
    
    async def _check_ip_limit(
        self, limit_type: RateLimitType, ip_address: str, rule: RateLimitRule
    ) -> Tuple[bool, int]:
        """Check IP-specific rate limit"""
        key = f"rate_limit:ip:{limit_type.value}:{ip_address}"
        return await self._check_limit(key, rule.max_requests, rule.time_window)
    
    async def _check_session_limit(
        self, limit_type: RateLimitType, session_id: str, rule: RateLimitRule
    ) -> Tuple[bool, int]:
        """Check session-specific rate limit"""
        key = f"rate_limit:session:{limit_type.value}:{session_id}"
        return await self._check_limit(key, rule.max_requests, rule.time_window)
    
    async def _check_burst_limit(
        self, limit_type: RateLimitType, user_id: Optional[int], 
        ip_address: Optional[str], session_id: Optional[str], rule: RateLimitRule
    ) -> bool:
        """Check burst rate limit"""
        # Use the most restrictive identifier
        identifier = user_id or ip_address or session_id
        if not identifier:
            return True
        
        key = f"burst_limit:{limit_type.value}:{identifier}"
        allowed, _ = await self._check_limit(key, rule.burst_limit, 60)  # 1 minute window
        return allowed
    
    async def _check_limit(self, key: str, max_requests: int, time_window: int) -> Tuple[bool, int]:
        """Check rate limit using Redis or memory"""
        if self.redis_client:
            return await self._check_redis_limit(key, max_requests, time_window)
        else:
            return await self._check_memory_limit(key, max_requests, time_window)
    
    async def _check_redis_limit(self, key: str, max_requests: int, time_window: int) -> Tuple[bool, int]:
        """Check rate limit using Redis"""
        try:
            pipe = self.redis_client.pipeline()
            now = time.time()
            
            # Add current request
            pipe.zadd(key, {str(now): now})
            
            # Remove old requests
            pipe.zremrangebyscore(key, 0, now - time_window)
            
            # Count current requests
            pipe.zcard(key)
            
            # Set expiration
            pipe.expire(key, time_window)
            
            results = pipe.execute()
            current_count = results[2]
            
            if current_count <= max_requests:
                return True, max_requests - current_count
            else:
                return False, 0
                
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Fallback to memory
            return await self._check_memory_limit(key, max_requests, time_window)
    
    async def _check_memory_limit(self, key: str, max_requests: int, time_window: int) -> Tuple[bool, int]:
        """Check rate limit using memory"""
        limiter = self.memory_limits[key]
        return limiter.is_allowed()
    
    async def _record_request(
        self, limit_type: RateLimitType, user_id: Optional[int], 
        ip_address: Optional[str], session_id: Optional[str], 
        request_metadata: Optional[Dict[str, Any]]
    ):
        """Record request for abuse detection"""
        # This would typically store request data for pattern analysis
        # For now, we'll just log it
        logger.debug(f"Recorded request: {limit_type.value} from user {user_id}, IP {ip_address}")
    
    async def _detect_abuse_patterns(
        self, limit_type: RateLimitType, user_id: Optional[int], 
        ip_address: Optional[str], session_id: Optional[str]
    ) -> Optional[AbusePattern]:
        """Detect abuse patterns in request behavior"""
        # This is a simplified implementation
        # In production, you'd analyze historical request patterns
        
        identifier = user_id or ip_address or session_id
        if not identifier:
            return None
        
        # Check for rapid-fire requests
        rapid_fire_key = f"rapid_fire:{limit_type.value}:{identifier}"
        rapid_fire_count = await self._get_request_count(rapid_fire_key, 60)  # 1 minute
        
        if rapid_fire_count >= self.abuse_patterns["rapid_fire"]["threshold"]:
            return AbusePattern(
                pattern_type="rapid_fire",
                severity="high",
                description=f"Rapid-fire requests detected: {rapid_fire_count} in 1 minute",
                detected_at=time.time(),
                user_id=user_id,
                ip_address=ip_address,
                session_id=session_id,
                metadata={"count": rapid_fire_count, "window": 60}
            )
        
        return None
    
    async def _get_request_count(self, key: str, time_window: int) -> int:
        """Get request count for given time window"""
        if self.redis_client:
            try:
                now = time.time()
                return self.redis_client.zcount(key, now - time_window, now)
            except Exception:
                return 0
        else:
            # Memory fallback
            return len(self.memory_limits[key].requests)
    
    async def log_security_event(
        self, 
        session: AsyncSession, 
        event_type: str, 
        description: str, 
        severity: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log security event to database"""
        try:
            security_event = SecurityEvent(
                event_type=event_type,
                severity=severity,
                description=description,
                ip_address=ip_address,
                user_agent=None,  # Would be passed from request
                session_id=session_id,
                additional_data=json.dumps(additional_data) if additional_data else None
            )
            
            session.add(security_event)
            await session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")

# Global rate limiter instance
rate_limiter = AdvancedRateLimiter()

# Decorator for easy rate limiting
def rate_limit(limit_type: RateLimitType, get_user_id=None, get_ip=None, get_session=None):
    """Decorator for rate limiting endpoints"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract identifiers from request
            user_id = get_user_id(*args, **kwargs) if get_user_id else None
            ip_address = get_ip(*args, **kwargs) if get_ip else None
            session_id = get_session(*args, **kwargs) if get_session else None
            
            # Check rate limit
            status = await rate_limiter.check_rate_limit(
                limit_type, user_id, ip_address, session_id
            )
            
            if status.is_limited:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "reason": status.reason,
                        "reset_time": status.reset_time,
                        "limit_type": status.limit_type.value
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
