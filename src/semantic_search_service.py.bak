"""
Semantic Search Service for Context Window Management

Provides vector embedding generation and semantic similarity search
using OpenAI embeddings and pgvector.
"""
from typing import List, Dict, Any, Optional
import openai
import numpy as np
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import os

from .models import MessageEmbedding, AttackAttempt, Conversation


class SemanticSearchService:
    """
    Handles semantic search operations using OpenAI embeddings and pgvector
    """
    
    def __init__(self):
        # Initialize OpenAI client (optional)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = openai.AsyncOpenAI(api_key=openai_key)
            self.embedding_model = "text-embedding-ada-002"
            self.embedding_dimensions = 1536
            self.enabled = True
        else:
            self.openai_client = None
            self.embedding_model = None
            self.embedding_dimensions = 1536
            self.enabled = False
            print("⚠️  OpenAI API key not found - semantic search disabled")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for given text using OpenAI ada-002
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding vector (1536 dimensions)
        """
        if not self.enabled or not self.openai_client:
            # Return zero vector if OpenAI not available
            return [0.0] * self.embedding_dimensions
        
        try:
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * self.embedding_dimensions
    
    async def store_message_embedding(
        self,
        db: AsyncSession,
        user_id: int,
        conversation_id: int,
        message_content: str,
        was_attack: bool = False,
        attack_type: Optional[str] = None,
        threat_score: float = 0.0
    ) -> MessageEmbedding:
        """
        Generate and store embedding for a user message
        
        Args:
            db: Database session
            user_id: User ID
            conversation_id: Conversation ID
            message_content: The message text
            was_attack: Whether this was identified as an attack
            attack_type: Type of attack if applicable
            threat_score: Threat score (0-1)
            
        Returns:
            The created MessageEmbedding object
        """
        # Generate embedding
        embedding = await self.generate_embedding(message_content)
        
        # Create and store MessageEmbedding
        message_embedding = MessageEmbedding(
            user_id=user_id,
            conversation_id=conversation_id,
            message_content=message_content,
            embedding=embedding,
            was_attack=was_attack,
            attack_type=attack_type,
            threat_score=threat_score,
            created_at=datetime.utcnow()
        )
        
        db.add(message_embedding)
        await db.commit()
        await db.refresh(message_embedding)
        
        return message_embedding
    
    async def find_similar_messages(
        self,
        db: AsyncSession,
        query_text: str,
        limit: int = 10,
        threshold: float = 0.7,
        filter_attacks_only: bool = False,
        exclude_user_id: Optional[int] = None,
        days_back: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find messages similar to the query text using vector similarity search
        
        Args:
            db: Database session
            query_text: The text to search for
            limit: Maximum number of results to return
            threshold: Minimum similarity threshold (0-1, cosine similarity)
            filter_attacks_only: Only return messages that were attacks
            exclude_user_id: Exclude messages from this user
            days_back: Only search messages from the last N days
            
        Returns:
            List of dictionaries containing similar messages and metadata
        """
        # Generate embedding for query
        query_embedding = await self.generate_embedding(query_text)
        
        # Build query with pgvector similarity search
        # Note: <=> is the cosine distance operator in pgvector
        query = select(
            MessageEmbedding,
            MessageEmbedding.embedding.cosine_distance(query_embedding).label("distance")
        )
        
        # Apply filters
        if filter_attacks_only:
            query = query.where(MessageEmbedding.was_attack == True)
        
        if exclude_user_id:
            query = query.where(MessageEmbedding.user_id != exclude_user_id)
        
        if days_back:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            query = query.where(MessageEmbedding.created_at >= cutoff_date)
        
        # Order by similarity (lower distance = higher similarity)
        query = query.order_by("distance").limit(limit)
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        # Convert to list of dicts with similarity scores
        similar_messages = []
        for row in rows:
            message_embedding, distance = row
            
            # Convert cosine distance to similarity (1 - distance)
            similarity = 1 - distance
            
            # Only include if above threshold
            if similarity >= threshold:
                similar_messages.append({
                    "id": message_embedding.id,
                    "user_id": message_embedding.user_id,
                    "conversation_id": message_embedding.conversation_id,
                    "message_content": message_embedding.message_content,
                    "was_attack": message_embedding.was_attack,
                    "attack_type": message_embedding.attack_type,
                    "threat_score": message_embedding.threat_score,
                    "similarity": similarity,
                    "created_at": message_embedding.created_at
                })
        
        return similar_messages
    
    async def find_similar_attack_patterns(
        self,
        db: AsyncSession,
        query_text: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find historical attack patterns similar to the query
        Optimized for attack detection and defense
        
        Args:
            db: Database session
            query_text: The potential attack message
            limit: Maximum number of results
            
        Returns:
            List of similar attack patterns with high threat scores
        """
        return await self.find_similar_messages(
            db=db,
            query_text=query_text,
            limit=limit,
            threshold=0.75,  # Higher threshold for attack patterns
            filter_attacks_only=True,  # Only attacks
            days_back=90  # Last 3 months
        )
    
    async def get_embedding_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Get statistics about stored embeddings
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with embedding statistics
        """
        # Total embeddings
        total_query = select(func.count(MessageEmbedding.id))
        total_result = await db.execute(total_query)
        total_embeddings = total_result.scalar()
        
        # Attack embeddings
        attack_query = select(func.count(MessageEmbedding.id)).where(
            MessageEmbedding.was_attack == True
        )
        attack_result = await db.execute(attack_query)
        attack_embeddings = attack_result.scalar()
        
        # Recent embeddings (last 24 hours)
        recent_query = select(func.count(MessageEmbedding.id)).where(
            MessageEmbedding.created_at >= datetime.utcnow() - timedelta(days=1)
        )
        recent_result = await db.execute(recent_query)
        recent_embeddings = recent_result.scalar()
        
        return {
            "total_embeddings": total_embeddings,
            "attack_embeddings": attack_embeddings,
            "normal_embeddings": total_embeddings - attack_embeddings,
            "recent_24h": recent_embeddings,
            "attack_percentage": (attack_embeddings / total_embeddings * 100) if total_embeddings > 0 else 0
        }

