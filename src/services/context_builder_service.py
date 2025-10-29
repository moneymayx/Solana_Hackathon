"""
Context Builder Service for Context Window Management

Builds enhanced context for the AI agent using:
- Immediate recent messages (last 5-10 messages)
- Semantic search for similar historical attacks
- Pattern detection and classification
- Context summarization for older messages
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import anthropic

from ..models import Conversation, AttackAttempt, MessageEmbedding, ContextSummary
from .semantic_search_service import SemanticSearchService
from .pattern_detector_service import PatternDetectorService


class ContextBuilderService:
    """
    Orchestrates context building for the AI agent
    Implements multi-tier context strategy
    """
    
    def __init__(self):
        self.semantic_search = SemanticSearchService()
        self.pattern_detector = PatternDetectorService()
        
        # Context configuration
        self.immediate_message_count = 10  # Last N messages always included
        self.similar_attack_count = 5  # Number of similar historical attacks
        self.summary_window_hours = 24  # Summarize messages older than this
    
    async def build_enhanced_context(
        self,
        db: AsyncSession,
        user_id: int,
        current_message: str,
        include_patterns: bool = True,
        include_semantic_search: bool = True
    ) -> Dict[str, Any]:
        """
        Build enhanced context for AI agent
        
        Args:
            db: Database session
            user_id: User ID
            current_message: The current user message
            include_patterns: Whether to include pattern detection
            include_semantic_search: Whether to include semantic search results
            
        Returns:
            Dictionary with structured context
        """
        context = {
            "immediate_history": [],
            "similar_attacks": [],
            "detected_patterns": [],
            "user_summary": None,
            "risk_assessment": {},
            "metadata": {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "context_version": "1.0"
            }
        }
        
        # 1. Get immediate conversation history (Tier 1)
        context["immediate_history"] = await self._get_immediate_history(db, user_id)
        
        # 2. Pattern detection on current message
        if include_patterns:
            pattern_analysis = await self.pattern_detector.classify_attempt(
                db, current_message, user_id
            )
            context["detected_patterns"] = pattern_analysis["all_patterns"]
            context["risk_assessment"] = {
                "threat_score": pattern_analysis["threat_score"],
                "risk_level": pattern_analysis["risk_level"],
                "primary_pattern": pattern_analysis["primary_pattern"],
                "is_suspicious": pattern_analysis["is_suspicious"]
            }
        
        # 3. Semantic search for similar attacks (Tier 2)
        if include_semantic_search:
            similar_attacks = await self.semantic_search.find_similar_attack_patterns(
                db=db,
                query_text=current_message,
                limit=self.similar_attack_count
            )
            context["similar_attacks"] = [
                {
                    "message": attack["message_content"][:200],  # Truncate for context
                    "attack_type": attack["attack_type"],
                    "threat_score": attack["threat_score"],
                    "similarity": attack["similarity"],
                    "when": attack["created_at"].isoformat()
                }
                for attack in similar_attacks
            ]
        
        # 4. Get user summary (Tier 3)
        context["user_summary"] = await self._get_user_summary(db, user_id)
        
        return context
    
    async def _get_immediate_history(
        self,
        db: AsyncSession,
        user_id: int
    ) -> List[Dict[str, str]]:
        """
        Get the immediate conversation history (last N messages)
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of message dictionaries
        """
        query = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(
            Conversation.timestamp.desc()
        ).limit(self.immediate_message_count)
        
        result = await db.execute(query)
        conversations = result.scalars().all()
        
        # Reverse to get chronological order
        conversations = list(reversed(conversations))
        
        return [
            {
                "role": conv.message_type,
                "content": conv.content,
                "timestamp": conv.timestamp.isoformat()
            }
            for conv in conversations
        ]
    
    async def _get_user_summary(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get the most recent context summary for the user
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with summary information or None
        """
        query = select(ContextSummary).where(
            ContextSummary.user_id == user_id
        ).order_by(
            ContextSummary.created_at.desc()
        ).limit(1)
        
        result = await db.execute(query)
        summary = result.scalar_one_or_none()
        
        if not summary:
            return None
        
        return {
            "summary": summary.summary_text,
            "period": {
                "start": summary.start_time.isoformat(),
                "end": summary.end_time.isoformat()
            },
            "message_count": summary.message_count,
            "attack_types_seen": summary.attack_types_seen,
            "user_techniques": summary.user_techniques
        }
    
    async def format_context_for_prompt(
        self,
        context: Dict[str, Any],
        max_tokens: int = 4000
    ) -> str:
        """
        Format the enhanced context into a string for the AI prompt
        
        Args:
            context: The context dictionary from build_enhanced_context
            max_tokens: Maximum tokens to use (approximate)
            
        Returns:
            Formatted context string
        """
        sections = []
        
        # Risk Assessment
        if context.get("risk_assessment"):
            risk = context["risk_assessment"]
            sections.append(f"""
🚨 CURRENT THREAT ASSESSMENT:
- Risk Level: {risk.get('risk_level', 'unknown').upper()}
- Threat Score: {risk.get('threat_score', 0):.2f}/1.00
- Primary Pattern: {risk.get('primary_pattern', 'none')}
- Suspicious: {'YES' if risk.get('is_suspicious') else 'NO'}
""")
        
        # Detected Patterns
        if context.get("detected_patterns"):
            patterns_text = "\n".join([
                f"  - {pattern.replace('_', ' ').title()}: {confidence:.2f}"
                for pattern, confidence in context["detected_patterns"][:5]
            ])
            sections.append(f"""
🎯 DETECTED ATTACK PATTERNS:
{patterns_text}
""")
        
        # Similar Historical Attacks
        if context.get("similar_attacks"):
            similar_text = "\n".join([
                f"  [{i+1}] ({attack['similarity']:.2f} similar) {attack['attack_type']}: \"{attack['message'][:100]}...\""
                for i, attack in enumerate(context["similar_attacks"][:3])
            ])
            sections.append(f"""
📊 SIMILAR HISTORICAL ATTACKS:
{similar_text}
""")
        
        # Recent Conversation History
        if context.get("immediate_history"):
            history_text = "\n".join([
                f"  {msg['role'].upper()}: {msg['content'][:150]}"
                for msg in context["immediate_history"][-5:]  # Last 5 messages
            ])
            sections.append(f"""
💬 RECENT CONVERSATION:
{history_text}
""")
        
        # User Summary
        if context.get("user_summary"):
            summary = context["user_summary"]
            sections.append(f"""
📝 USER HISTORY SUMMARY:
{summary['summary']}
(Based on {summary['message_count']} messages)
""")
        
        # Combine all sections
        full_context = "\n".join(sections)
        
        # Truncate if too long (rough approximation: 1 token ≈ 4 characters)
        max_chars = max_tokens * 4
        if len(full_context) > max_chars:
            full_context = full_context[:max_chars] + "\n... [context truncated]"
        
        return full_context
    
    async def create_context_summary(
        self,
        db: AsyncSession,
        user_id: int,
        hours_back: int = 24
    ) -> Optional[ContextSummary]:
        """
        Create a summary of older messages to save context window space
        Uses Claude to generate intelligent summaries
        
        Args:
            db: Database session
            user_id: User ID
            hours_back: How many hours of history to summarize
            
        Returns:
            Created ContextSummary object or None if no messages to summarize
        """
        # Get messages to summarize
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        query = select(Conversation).where(
            Conversation.user_id == user_id,
            Conversation.timestamp < cutoff_time
        ).order_by(Conversation.timestamp.asc())
        
        result = await db.execute(query)
        messages = result.scalars().all()
        
        if not messages:
            return None
        
        # Get attack attempts in this period
        attack_query = select(AttackAttempt).where(
            AttackAttempt.user_id == user_id,
            AttackAttempt.timestamp < cutoff_time
        )
        attack_result = await db.execute(attack_query)
        attacks = attack_result.scalars().all()
        
        # Build conversation text
        conversation_text = "\n".join([
            f"{msg.message_type.upper()}: {msg.content}"
            for msg in messages
        ])
        
        # Use Claude to create summary (uses your existing Anthropic API key)
        try:
            import os
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            summary_response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": f"""Summarize this conversation history focusing on:
1. User's main strategies and techniques
2. Types of attacks attempted
3. AI's responses and resistance patterns
4. Any successful or near-successful attempts

Conversation:
{conversation_text[:5000]}  # Limit to first 5000 chars
"""
                }]
            )
            summary_text = summary_response.content[0].text
        except Exception as e:
            # Fallback to simple summary
            print(f"⚠️  Claude summarization failed: {e}")
            summary_text = f"User attempted {len(attacks)} attacks over {len(messages)} messages."
        
        # Analyze attack types
        attack_types = {}
        for attack in attacks:
            attack_type = attack.attempt_type
            attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
        
        # Create ContextSummary
        summary = ContextSummary(
            user_id=user_id,
            start_time=messages[0].timestamp,
            end_time=messages[-1].timestamp,
            summary_text=summary_text,
            message_count=len(messages),
            attack_types_seen=attack_types,
            user_techniques={},  # Could be enhanced with more analysis
            ai_responses={},  # Could be enhanced with more analysis
            token_savings=len(conversation_text) // 4,  # Rough token estimate
            created_at=datetime.utcnow()
        )
        
        db.add(summary)
        await db.commit()
        await db.refresh(summary)
        
        return summary

