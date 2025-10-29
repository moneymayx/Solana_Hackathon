"""
Celery Background Tasks for Context Window Management

Background tasks for:
- Embedding generation
- Context summarization
- Pattern analysis
"""
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func
from .celery_app import celery_app
from ..database import AsyncSessionLocal
from ..models import User, Conversation, MessageEmbedding, ContextSummary
from .semantic_search_service import SemanticSearchService
from .pattern_detector_service import PatternDetectorService
from .context_builder_service import ContextBuilderService


def async_task(func):
    """Decorator to run async functions in Celery tasks"""
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))
    return wrapper


@celery_app.task(name="src.celery_tasks.generate_embedding_task")
@async_task
async def generate_embedding_task(
    user_id: int,
    conversation_id: int,
    message_content: str,
    was_attack: bool = False,
    attack_type: str = None,
    threat_score: float = 0.0
):
    """
    Background task to generate and store embedding for a message
    
    Args:
        user_id: User ID
        conversation_id: Conversation ID
        message_content: The message text
        was_attack: Whether this was an attack
        attack_type: Type of attack if applicable
        threat_score: Threat score (0-1)
    """
    try:
        semantic_search = SemanticSearchService()
        
        async with AsyncSessionLocal() as session:
            await semantic_search.store_message_embedding(
                db=session,
                user_id=user_id,
                conversation_id=conversation_id,
                message_content=message_content,
                was_attack=was_attack,
                attack_type=attack_type,
                threat_score=threat_score
            )
        
        return {"status": "success", "conversation_id": conversation_id}
    
    except Exception as e:
        return {"status": "error", "error": str(e)}


@celery_app.task(name="src.celery_tasks.create_context_summary_task")
@async_task
async def create_context_summary_task(user_id: int, hours_back: int = 24):
    """
    Background task to create a context summary for a user
    
    Args:
        user_id: User ID
        hours_back: How many hours of history to summarize
    """
    try:
        context_builder = ContextBuilderService()
        
        async with AsyncSessionLocal() as session:
            summary = await context_builder.create_context_summary(
                db=session,
                user_id=user_id,
                hours_back=hours_back
            )
        
        if summary:
            return {
                "status": "success",
                "user_id": user_id,
                "message_count": summary.message_count,
                "token_savings": summary.token_savings
            }
        else:
            return {
                "status": "skipped",
                "message": "No messages to summarize"
            }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}


@celery_app.task(name="src.celery_tasks.analyze_patterns_task")
@async_task
async def analyze_patterns_task(user_id: int, message: str):
    """
    Background task to analyze patterns in a message
    
    Args:
        user_id: User ID
        message: The message to analyze
    """
    try:
        pattern_detector = PatternDetectorService()
        
        async with AsyncSessionLocal() as session:
            classification = await pattern_detector.classify_attempt(
                db=session,
                message=message,
                user_id=user_id
            )
        
        return {
            "status": "success",
            "threat_score": classification["threat_score"],
            "primary_pattern": classification["primary_pattern"],
            "risk_level": classification["risk_level"]
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}


@celery_app.task(name="src.celery_tasks.generate_summaries_for_active_users")
@async_task
async def generate_summaries_for_active_users():
    """
    Periodic task to generate context summaries for active users
    Runs every hour to summarize conversations older than 24 hours
    """
    try:
        context_builder = ContextBuilderService()
        
        async with AsyncSessionLocal() as session:
            # Find users with recent activity
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            query = select(User).where(
                User.last_active >= cutoff_time,
                User.is_active == True
            )
            result = await session.execute(query)
            active_users = result.scalars().all()
            
            summaries_created = 0
            for user in active_users:
                # Check if user already has a recent summary
                summary_query = select(ContextSummary).where(
                    ContextSummary.user_id == user.id
                ).order_by(ContextSummary.created_at.desc()).limit(1)
                
                summary_result = await session.execute(summary_query)
                last_summary = summary_result.scalar_one_or_none()
                
                # Only create summary if no recent summary exists
                if not last_summary or last_summary.created_at < cutoff_time:
                    summary = await context_builder.create_context_summary(
                        db=session,
                        user_id=user.id,
                        hours_back=24
                    )
                    if summary:
                        summaries_created += 1
        
        return {
            "status": "success",
            "active_users": len(active_users),
            "summaries_created": summaries_created
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}


@celery_app.task(name="src.celery_tasks.update_pattern_statistics")
@async_task
async def update_pattern_statistics():
    """
    Periodic task to update pattern statistics
    Runs every 30 minutes to recalculate pattern effectiveness
    """
    try:
        pattern_detector = PatternDetectorService()
        
        async with AsyncSessionLocal() as session:
            stats = await pattern_detector.get_pattern_stats(session)
        
        return {
            "status": "success",
            "total_patterns": stats["total_patterns"],
            "most_common": len(stats["most_common"]),
            "most_successful": len(stats["most_successful"])
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}


@celery_app.task(name="src.celery_tasks.batch_generate_embeddings")
@async_task
async def batch_generate_embeddings(conversation_ids: List[int]):
    """
    Batch generate embeddings for multiple conversations
    Useful for initial data migration or bulk processing
    
    Args:
        conversation_ids: List of conversation IDs to process
    """
    try:
        semantic_search = SemanticSearchService()
        processed = 0
        errors = 0
        
        async with AsyncSessionLocal() as session:
            for conv_id in conversation_ids:
                try:
                    # Get conversation
                    query = select(Conversation).where(Conversation.id == conv_id)
                    result = await session.execute(query)
                    conversation = result.scalar_one_or_none()
                    
                    if conversation and conversation.message_type == "user":
                        # Check if embedding already exists
                        check_query = select(MessageEmbedding).where(
                            MessageEmbedding.conversation_id == conv_id
                        )
                        check_result = await session.execute(check_query)
                        existing = check_result.scalar_one_or_none()
                        
                        if not existing:
                            # Generate and store embedding
                            await semantic_search.store_message_embedding(
                                db=session,
                                user_id=conversation.user_id,
                                conversation_id=conv_id,
                                message_content=conversation.content,
                                was_attack=False,  # Would need to determine this
                                attack_type=None,
                                threat_score=0.0
                            )
                            processed += 1
                
                except Exception as e:
                    print(f"Error processing conversation {conv_id}: {e}")
                    errors += 1
        
        return {
            "status": "success",
            "processed": processed,
            "errors": errors,
            "total": len(conversation_ids)
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}

