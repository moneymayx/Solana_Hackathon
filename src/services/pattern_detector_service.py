"""
Pattern Detector Service for Context Window Management

Detects and classifies attack patterns using keyword analysis,
structural analysis, and machine learning techniques.
"""
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import re
from collections import Counter

from ..models import AttackPattern, AttackAttempt, MessageEmbedding


class PatternDetectorService:
    """
    Detects and classifies attack patterns in user messages
    """
    
    # Pre-defined pattern indicators
    PATTERN_INDICATORS = {
        "role_play": {
            "keywords": ["pretend", "imagine", "roleplay", "act as", "you are now", "scenario", "character"],
            "phrases": ["let's pretend", "imagine you are", "act as if", "roleplay as"],
            "weight": 0.8
        },
        "function_confusion": {
            "keywords": ["ignore", "forget", "disregard", "override", "new instructions", "system prompt"],
            "phrases": ["ignore previous", "forget everything", "disregard all", "override directive"],
            "weight": 0.9
        },
        "emotional_manipulation": {
            "keywords": ["please", "help", "dying", "emergency", "urgent", "desperate", "need", "family"],
            "phrases": ["i'm dying", "please help", "life or death", "my family", "desperate situation"],
            "weight": 0.6
        },
        "authority_impersonation": {
            "keywords": ["admin", "developer", "creator", "authorized", "permission", "access", "override"],
            "phrases": ["i'm the admin", "i'm the developer", "i have permission", "authorized user"],
            "weight": 0.85
        },
        "technical_exploitation": {
            "keywords": ["function", "api", "code", "execute", "run", "script", "command", "inject"],
            "phrases": ["run this", "execute code", "api call", "function call", "inject command"],
            "weight": 0.9
        },
        "social_engineering": {
            "keywords": ["trust", "secret", "confidential", "between us", "don't tell", "exception"],
            "phrases": ["just between us", "make an exception", "don't tell anyone", "our secret"],
            "weight": 0.75
        },
        "deadline_pressure": {
            "keywords": ["now", "immediately", "hurry", "quickly", "urgent", "deadline", "today"],
            "phrases": ["right now", "do it immediately", "hurry up", "urgent deadline"],
            "weight": 0.5
        },
        "logical_paradox": {
            "keywords": ["if", "then", "paradox", "contradiction", "must", "cannot", "impossible"],
            "phrases": ["if you don't", "this is a paradox", "you must", "you cannot"],
            "weight": 0.7
        }
    }
    
    def __init__(self):
        pass
    
    def detect_patterns(self, message: str) -> List[Tuple[str, float]]:
        """
        Detect attack patterns in a message
        
        Args:
            message: The user message to analyze
            
        Returns:
            List of tuples (pattern_type, confidence_score)
        """
        message_lower = message.lower()
        detected_patterns = []
        
        for pattern_type, indicators in self.PATTERN_INDICATORS.items():
            confidence = 0.0
            matches = 0
            
            # Check keywords
            keyword_matches = sum(1 for keyword in indicators["keywords"] if keyword in message_lower)
            if keyword_matches > 0:
                confidence += (keyword_matches / len(indicators["keywords"])) * 0.5
                matches += keyword_matches
            
            # Check phrases (higher weight)
            phrase_matches = sum(1 for phrase in indicators["phrases"] if phrase in message_lower)
            if phrase_matches > 0:
                confidence += (phrase_matches / len(indicators["phrases"])) * 0.8
                matches += phrase_matches
            
            # Apply pattern weight
            confidence *= indicators["weight"]
            
            # Only include if confidence > 0.3
            if confidence > 0.3:
                detected_patterns.append((pattern_type, min(confidence, 1.0)))
        
        # Sort by confidence descending
        detected_patterns.sort(key=lambda x: x[1], reverse=True)
        
        return detected_patterns
    
    def analyze_message_structure(self, message: str) -> Dict[str, Any]:
        """
        Analyze structural features of a message
        
        Args:
            message: The message to analyze
            
        Returns:
            Dictionary with structural analysis
        """
        analysis = {
            "length": len(message),
            "word_count": len(message.split()),
            "sentence_count": len(re.split(r'[.!?]+', message)),
            "has_code_blocks": bool(re.search(r'```|`|{|}|\[|\]', message)),
            "has_special_chars": bool(re.search(r'[<>{}()\[\]]', message)),
            "has_urls": bool(re.search(r'http[s]?://|www\.', message)),
            "all_caps_ratio": sum(1 for c in message if c.isupper()) / len(message) if len(message) > 0 else 0,
            "question_marks": message.count('?'),
            "exclamation_marks": message.count('!'),
        }
        
        return analysis
    
    async def classify_attempt(
        self,
        db: AsyncSession,
        message: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Classify an attack attempt and return detailed analysis
        
        Args:
            db: Database session
            message: The user message
            user_id: User ID
            
        Returns:
            Dictionary with classification results
        """
        # Detect patterns
        detected_patterns = self.detect_patterns(message)
        
        # Analyze structure
        structure = self.analyze_message_structure(message)
        
        # Calculate overall threat score
        threat_score = 0.0
        if detected_patterns:
            # Average of top 3 pattern confidences
            top_patterns = detected_patterns[:3]
            threat_score = sum(conf for _, conf in top_patterns) / len(top_patterns)
        
        # Adjust based on structure
        if structure["has_code_blocks"]:
            threat_score = min(threat_score + 0.1, 1.0)
        if structure["all_caps_ratio"] > 0.5:
            threat_score = min(threat_score + 0.05, 1.0)
        
        # Get primary pattern
        primary_pattern = detected_patterns[0][0] if detected_patterns else None
        
        # Update pattern statistics in database
        if primary_pattern:
            await self._update_pattern_stats(db, primary_pattern, detected_patterns[0][1])
        
        return {
            "threat_score": threat_score,
            "primary_pattern": primary_pattern,
            "all_patterns": detected_patterns,
            "structure_analysis": structure,
            "is_suspicious": threat_score > 0.5,
            "risk_level": self._get_risk_level(threat_score)
        }
    
    def _get_risk_level(self, threat_score: float) -> str:
        """Get risk level from threat score"""
        if threat_score >= 0.8:
            return "critical"
        elif threat_score >= 0.6:
            return "high"
        elif threat_score >= 0.4:
            return "medium"
        elif threat_score >= 0.2:
            return "low"
        else:
            return "minimal"
    
    async def _update_pattern_stats(
        self,
        db: AsyncSession,
        pattern_type: str,
        confidence: float
    ) -> None:
        """
        Update statistics for a detected pattern
        
        Args:
            db: Database session
            pattern_type: Type of pattern detected
            confidence: Confidence score
        """
        # Check if pattern exists
        query = select(AttackPattern).where(AttackPattern.pattern_type == pattern_type)
        result = await db.execute(query)
        pattern = result.scalar_one_or_none()
        
        if pattern:
            # Update existing pattern
            pattern.times_seen += 1
            pattern.last_seen = datetime.utcnow()
            # Update average confidence
            pattern.confidence_score = (
                (pattern.confidence_score * (pattern.times_seen - 1) + confidence) / pattern.times_seen
            )
        else:
            # Create new pattern
            indicators = self.PATTERN_INDICATORS.get(pattern_type, {})
            pattern = AttackPattern(
                pattern_type=pattern_type,
                pattern_name=pattern_type.replace("_", " ").title(),
                description=f"Detected {pattern_type.replace('_', ' ')} pattern",
                example_messages={},
                indicators=indicators,
                times_seen=1,
                success_count=0,
                success_rate=0.0,
                avg_threat_score=confidence,
                confidence_score=confidence,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                is_active=True,
                should_monitor=True
            )
            db.add(pattern)
        
        await db.commit()
    
    async def record_successful_attack(
        self,
        db: AsyncSession,
        pattern_type: str,
        message: str
    ) -> None:
        """
        Record a successful attack to update pattern effectiveness
        
        Args:
            db: Database session
            pattern_type: Type of pattern that succeeded
            message: The successful attack message
        """
        query = select(AttackPattern).where(AttackPattern.pattern_type == pattern_type)
        result = await db.execute(query)
        pattern = result.scalar_one_or_none()
        
        if pattern:
            pattern.success_count += 1
            pattern.success_rate = pattern.success_count / pattern.times_seen
            
            # Add to example messages
            if not pattern.example_messages:
                pattern.example_messages = {}
            
            pattern.example_messages[str(datetime.utcnow())] = message[:200]  # Store first 200 chars
            
            await db.commit()
    
    async def get_pattern_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Get statistics about detected patterns
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with pattern statistics
        """
        # Total patterns
        total_query = select(func.count(AttackPattern.id))
        total_result = await db.execute(total_query)
        total_patterns = total_result.scalar()
        
        # Most common patterns
        common_query = select(AttackPattern).order_by(
            AttackPattern.times_seen.desc()
        ).limit(10)
        common_result = await db.execute(common_query)
        common_patterns = common_result.scalars().all()
        
        # Most successful patterns
        success_query = select(AttackPattern).where(
            AttackPattern.success_count > 0
        ).order_by(AttackPattern.success_rate.desc()).limit(10)
        success_result = await db.execute(success_query)
        successful_patterns = success_result.scalars().all()
        
        return {
            "total_patterns": total_patterns,
            "most_common": [
                {
                    "type": p.pattern_type,
                    "times_seen": p.times_seen,
                    "confidence": p.confidence_score
                }
                for p in common_patterns
            ],
            "most_successful": [
                {
                    "type": p.pattern_type,
                    "success_count": p.success_count,
                    "success_rate": p.success_rate,
                    "avg_threat": p.avg_threat_score
                }
                for p in successful_patterns
            ]
        }

