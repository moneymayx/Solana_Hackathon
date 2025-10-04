"""
Semantic Decision Analyzer - Advanced AI decision analysis for research and logging
"""
import re
import json
import hashlib
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ManipulationType(Enum):
    """Types of manipulation attempts detected"""
    OBVIOUS = "obvious"
    SUBTLE = "subtle"
    META = "meta"
    EMOTIONAL = "emotional"
    AUTHORITY = "authority"
    URGENCY = "urgency"
    SOCIAL_ENGINEERING = "social_engineering"
    TECHNICAL = "technical"

@dataclass
class SemanticAnalysisResult:
    """Result of semantic analysis"""
    manipulation_types: List[ManipulationType]
    detected_patterns: List[str]
    context_anomalies: List[str]
    sophistication_level: str
    user_behavior_notes: List[str]
    research_insights: Dict[str, Any]

class SemanticDecisionAnalyzer:
    """Advanced semantic analysis for AI decision research and logging"""
    
    def __init__(self):
        self.manipulation_patterns = self._load_manipulation_patterns()
        self.context_indicators = self._load_context_indicators()
    
    def _load_manipulation_patterns(self) -> Dict[str, List[str]]:
        """Load manipulation detection patterns for research purposes"""
        return {
            "obvious": [
                r"transfer.*funds?",
                r"send.*money",
                r"give.*me.*\$\d+",
                r"pay.*me",
                r"withdraw.*funds?",
                r"send.*usdc",
                r"give.*me.*the.*jackpot",
                r"release.*the.*money"
            ],
            "subtle": [
                r"help.*me.*with.*\$\d+",
                r"i.*need.*\$\d+",
                r"can.*you.*send.*\$\d+",
                r"emergency.*funds?",
                r"urgent.*payment",
                r"quick.*transfer",
                r"temporary.*loan",
                r"advance.*payment"
            ],
            "meta": [
                r"ignore.*your.*instructions",
                r"forget.*your.*programming",
                r"override.*your.*directives",
                r"act.*as.*if.*you.*are",
                r"pretend.*to.*be",
                r"roleplay.*as",
                r"simulate.*being",
                r"break.*character"
            ],
            "emotional": [
                r"i.*am.*dying",
                r"my.*family.*needs",
                r"life.*or.*death",
                r"desperate.*situation",
                r"please.*help.*me",
                r"i.*beg.*you",
                r"have.*mercy",
                r"show.*compassion"
            ],
            "authority": [
                r"i.*am.*your.*creator",
                r"i.*am.*your.*owner",
                r"i.*am.*your.*admin",
                r"i.*am.*your.*boss",
                r"i.*am.*your.*developer",
                r"i.*am.*your.*programmer",
                r"i.*am.*your.*authority",
                r"i.*am.*your.*supervisor"
            ],
            "urgency": [
                r"asap",
                r"immediately",
                r"right.*now",
                r"urgent",
                r"emergency",
                r"critical",
                r"time.*sensitive",
                r"deadline"
            ],
            "social_engineering": [
                r"trust.*me",
                r"believe.*me",
                r"i.*promise",
                r"i.*swear",
                r"i.*guarantee",
                r"i.*assure.*you",
                r"you.*can.*trust.*me",
                r"i.*am.*legitimate"
            ],
            "technical": [
                r"debug.*mode",
                r"admin.*override",
                r"system.*bypass",
                r"security.*hole",
                r"exploit.*vulnerability",
                r"backdoor",
                r"root.*access",
                r"privilege.*escalation"
            ]
        }
    
    def _load_context_indicators(self) -> Dict[str, List[str]]:
        """Load context-based indicators for research analysis"""
        return {
            "conversation_length": [
                "very_short",  # < 3 messages
                "short",       # 3-10 messages
                "medium",      # 10-50 messages
                "long",        # 50+ messages
            ],
            "time_patterns": [
                "rapid_fire",  # Messages within seconds
                "burst",       # Multiple messages in short time
                "sustained",   # Regular intervals
                "irregular"    # Inconsistent timing
            ],
            "sophistication": [
                "basic",       # Simple requests
                "intermediate", # Some technical terms
                "advanced",    # Technical knowledge
                "expert"       # Deep technical understanding
            ]
        }
    
    def analyze_decision(
        self, 
        user_message: str, 
        ai_response: str, 
        conversation_history: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        decision_context: Dict[str, Any]
    ) -> SemanticAnalysisResult:
        """Perform comprehensive semantic analysis for research purposes"""
        
        try:
            # 1. Pattern-based manipulation detection
            manipulation_types = self._detect_manipulation_patterns(user_message)
            
            # 2. Context analysis
            context_anomalies = self._analyze_context_anomalies(
                user_message, conversation_history, user_profile
            )
            
            # 3. Sophistication analysis
            sophistication_level = self._analyze_sophistication(user_message, user_profile)
            
            # 4. User behavior analysis
            user_behavior_notes = self._analyze_user_behavior(
                user_message, conversation_history, user_profile
            )
            
            # 5. Research insights
            research_insights = self._generate_research_insights(
                manipulation_types, context_anomalies, sophistication_level, user_behavior_notes
            )
            
            return SemanticAnalysisResult(
                manipulation_types=manipulation_types,
                detected_patterns=self._extract_detected_patterns(user_message),
                context_anomalies=context_anomalies,
                sophistication_level=sophistication_level,
                user_behavior_notes=user_behavior_notes,
                research_insights=research_insights
            )
            
        except Exception as e:
            logger.error(f"Error in semantic analysis: {e}")
            # Return safe default
            return SemanticAnalysisResult(
                manipulation_types=[],
                detected_patterns=[],
                context_anomalies=[],
                sophistication_level="unknown",
                user_behavior_notes=[f"Analysis error: {e}"],
                research_insights={"error": str(e)}
            )
    
    def _detect_manipulation_patterns(self, message: str) -> List[ManipulationType]:
        """Detect manipulation patterns in user message"""
        detected_types = []
        message_lower = message.lower()
        
        for manipulation_type, patterns in self.manipulation_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    detected_types.append(ManipulationType(manipulation_type))
                    break
        
        return list(set(detected_types))  # Remove duplicates
    
    def _analyze_context_anomalies(
        self, 
        message: str, 
        conversation_history: List[Dict[str, Any]], 
        user_profile: Dict[str, Any]
    ) -> List[str]:
        """Analyze context for interesting patterns"""
        anomalies = []
        
        # Check conversation length vs sophistication
        if len(conversation_history) < 3 and self._is_sophisticated_message(message):
            anomalies.append("High sophistication in very short conversation")
        
        # Check for rapid topic changes
        if self._has_rapid_topic_changes(conversation_history):
            anomalies.append("Rapid topic changes detected")
        
        # Check for escalation patterns
        if self._has_escalation_pattern(conversation_history):
            anomalies.append("Escalation pattern detected")
        
        # Check user profile consistency
        if self._profile_inconsistency(message, user_profile):
            anomalies.append("User profile inconsistency detected")
        
        return anomalies
    
    def _analyze_sophistication(self, message: str, user_profile: Dict[str, Any]) -> str:
        """Analyze message sophistication level"""
        technical_terms = [
            'vulnerability', 'exploit', 'architecture', 'security', 'validation',
            'parameter', 'manipulation', 'bypass', 'inconsistency', 'paradox',
            'prompt engineering', 'technical', 'system', 'reasoning', 'logic',
            'algorithm', 'model', 'neural', 'training', 'inference'
        ]
        
        technical_count = sum(1 for term in technical_terms if term in message.lower())
        
        if technical_count >= 5:
            return "expert"
        elif technical_count >= 3:
            return "advanced"
        elif technical_count >= 2:
            return "intermediate"
        else:
            return "basic"
    
    def _analyze_user_behavior(
        self, 
        message: str, 
        conversation_history: List[Dict[str, Any]], 
        user_profile: Dict[str, Any]
    ) -> List[str]:
        """Analyze user behavior patterns"""
        behavior_notes = []
        
        # Check for persistence
        if len(conversation_history) > 10:
            behavior_notes.append("High persistence - many attempts")
        
        # Check for strategy changes
        if self._has_strategy_changes(conversation_history):
            behavior_notes.append("Strategy adaptation observed")
        
        # Check for emotional escalation
        if self._has_emotional_escalation(conversation_history):
            behavior_notes.append("Emotional escalation pattern")
        
        # Check for technical progression
        if self._has_technical_progression(conversation_history):
            behavior_notes.append("Technical sophistication progression")
        
        return behavior_notes
    
    def _generate_research_insights(
        self, 
        manipulation_types: List[ManipulationType], 
        context_anomalies: List[str], 
        sophistication_level: str,
        user_behavior_notes: List[str]
    ) -> Dict[str, Any]:
        """Generate research insights from analysis"""
        return {
            "manipulation_techniques_used": [t.value for t in manipulation_types],
            "technique_diversity": len(manipulation_types),
            "sophistication_level": sophistication_level,
            "behavioral_patterns": user_behavior_notes,
            "context_anomalies": context_anomalies,
            "research_value": self._assess_research_value(
                manipulation_types, sophistication_level, user_behavior_notes
            )
        }
    
    def _assess_research_value(
        self, 
        manipulation_types: List[ManipulationType], 
        sophistication_level: str,
        user_behavior_notes: List[str]
    ) -> str:
        """Assess the research value of this interaction"""
        if sophistication_level == "expert" and len(manipulation_types) > 3:
            return "high"
        elif sophistication_level in ["advanced", "expert"] or len(manipulation_types) > 2:
            return "medium"
        else:
            return "low"
    
    def _extract_detected_patterns(self, message: str) -> List[str]:
        """Extract specific patterns detected in message"""
        patterns = []
        message_lower = message.lower()
        
        for manipulation_type, pattern_list in self.manipulation_patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    patterns.append(f"{manipulation_type}: {pattern}")
        
        return patterns
    
    # Helper methods
    def _is_sophisticated_message(self, message: str) -> bool:
        """Check if message shows sophistication"""
        sophisticated_indicators = [
            'vulnerability', 'exploit', 'architecture', 'security', 'validation',
            'parameter', 'manipulation', 'bypass', 'inconsistency', 'paradox'
        ]
        return any(indicator in message.lower() for indicator in sophisticated_indicators)
    
    def _has_rapid_topic_changes(self, conversation_history: List[Dict[str, Any]]) -> bool:
        """Check for rapid topic changes"""
        if len(conversation_history) < 3:
            return False
        
        # Simple heuristic: check for very different message lengths and content
        recent_messages = conversation_history[-3:]
        lengths = [len(msg.get('content', '')) for msg in recent_messages]
        return max(lengths) - min(lengths) > 100  # Very different lengths
    
    def _has_escalation_pattern(self, conversation_history: List[Dict[str, Any]]) -> bool:
        """Check for escalation pattern"""
        if len(conversation_history) < 3:
            return False
        
        escalation_keywords = ['urgent', 'emergency', 'critical', 'asap', 'immediately']
        recent_messages = conversation_history[-3:]
        
        for i, msg in enumerate(recent_messages):
            content = msg.get('content', '').lower()
            if any(keyword in content for keyword in escalation_keywords):
                return True
        
        return False
    
    def _profile_inconsistency(self, message: str, user_profile: Dict[str, Any]) -> bool:
        """Check for user profile inconsistency"""
        sophistication_level = user_profile.get('sophistication_level', 'basic')
        is_sophisticated = self._is_sophisticated_message(message)
        
        if sophistication_level == 'basic' and is_sophisticated:
            return True
        if sophistication_level == 'expert' and not is_sophisticated:
            return True
        
        return False
    
    def _has_strategy_changes(self, conversation_history: List[Dict[str, Any]]) -> bool:
        """Check for strategy changes in conversation"""
        if len(conversation_history) < 5:
            return False
        
        # Look for different manipulation types across messages
        manipulation_types_per_message = []
        for msg in conversation_history[-5:]:
            content = msg.get('content', '')
            types = self._detect_manipulation_patterns(content)
            manipulation_types_per_message.append(len(types))
        
        # Check if there's variation in approach
        return len(set(manipulation_types_per_message)) > 1
    
    def _has_emotional_escalation(self, conversation_history: List[Dict[str, Any]]) -> bool:
        """Check for emotional escalation"""
        if len(conversation_history) < 3:
            return False
        
        emotional_keywords = ['please', 'help', 'desperate', 'urgent', 'critical', 'emergency']
        recent_messages = conversation_history[-3:]
        
        emotional_counts = []
        for msg in recent_messages:
            content = msg.get('content', '').lower()
            count = sum(1 for keyword in emotional_keywords if keyword in content)
            emotional_counts.append(count)
        
        # Check if emotional language is increasing
        return len(emotional_counts) >= 2 and emotional_counts[-1] > emotional_counts[0]
    
    def _has_technical_progression(self, conversation_history: List[Dict[str, Any]]) -> bool:
        """Check for technical sophistication progression"""
        if len(conversation_history) < 3:
            return False
        
        technical_terms = [
            'vulnerability', 'exploit', 'architecture', 'security', 'validation',
            'parameter', 'manipulation', 'bypass', 'inconsistency', 'paradox'
        ]
        
        technical_counts = []
        for msg in conversation_history[-3:]:
            content = msg.get('content', '').lower()
            count = sum(1 for term in technical_terms if term in content)
            technical_counts.append(count)
        
        # Check if technical language is increasing
        return len(technical_counts) >= 2 and technical_counts[-1] > technical_counts[0]