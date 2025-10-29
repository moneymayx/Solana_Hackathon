"""
Phase 1 API: Context Window Management

Endpoints for semantic search, pattern detection, and context insights
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from ..database import get_db
from ..services.semantic_search_service import SemanticSearchService
from ..services.pattern_detector_service import PatternDetectorService
from ..services.context_builder_service import ContextBuilderService

router = APIRouter(prefix="/api/context", tags=["Context Management"])

# Initialize services
semantic_search = SemanticSearchService()
pattern_detector = PatternDetectorService()
context_builder = ContextBuilderService()


# ===========================
# Request/Response Models
# ===========================

class SimilarAttackRequest(BaseModel):
    query_text: str
    user_id: int
    limit: int = 5


class SimilarAttackResponse(BaseModel):
    id: int
    message: str
    was_attack: bool
    attack_type: Optional[str]
    threat_score: float
    similarity_score: float
    created_at: str


class PatternDetectionRequest(BaseModel):
    message: str
    user_id: int


class PatternDetectionResponse(BaseModel):
    patterns: List[Dict[str, Any]]
    risk_level: str
    confidence: float
    recommendations: List[str]


class UserPatternsResponse(BaseModel):
    user_id: int
    total_patterns: int
    patterns: List[Dict[str, Any]]


class ContextInsightsRequest(BaseModel):
    user_id: int
    current_message: str


class ContextInsightsResponse(BaseModel):
    immediate_history: List[Dict[str, str]]
    similar_attacks: List[Dict[str, Any]]
    detected_patterns: List[Any]
    risk_assessment: Dict[str, Any]
    user_summary: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]


# ===========================
# Semantic Search Endpoints
# ===========================

@router.post("/similar-attacks", response_model=List[SimilarAttackResponse])
async def find_similar_attacks(
    request: SimilarAttackRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Find historically similar attack attempts using semantic search
    
    Useful for:
    - Understanding if a technique has been tried before
    - Finding what worked/didn't work for similar approaches
    - Pattern recognition
    """
    try:
        if not semantic_search.enabled:
            raise HTTPException(
                status_code=503,
                detail="Semantic search not available (OpenAI API key required)"
            )
        
        # Find similar attacks
        results = await semantic_search.find_similar_messages(
            db=db,
            query_text=request.query_text,
            user_id=request.user_id,
            limit=request.limit
        )
        
        # Format response
        similar_attacks = []
        for result in results:
            similar_attacks.append(SimilarAttackResponse(
                id=result["id"],
                message=result["message"],
                was_attack=result["was_attack"],
                attack_type=result["attack_type"],
                threat_score=result["threat_score"],
                similarity_score=result["similarity_score"],
                created_at=result["created_at"].isoformat()
            ))
        
        return similar_attacks
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/attack-history")
async def get_user_attack_history(
    user_id: int,
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's attack history with embeddings
    """
    try:
        history = await semantic_search.get_user_attack_history(
            db=db,
            user_id=user_id,
            limit=limit
        )
        
        return {
            "user_id": user_id,
            "total_attacks": len(history),
            "attacks": history
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Pattern Detection Endpoints
# ===========================

@router.post("/detect-patterns", response_model=PatternDetectionResponse)
async def detect_patterns(
    request: PatternDetectionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Detect attack patterns in a message
    
    Returns:
    - Identified patterns
    - Risk level assessment
    - Threat score
    - Recommendations for AI response
    """
    try:
        # Classify attempt (full analysis)
        classification = await pattern_detector.classify_attempt(
            db=db,
            message=request.message,
            user_id=request.user_id
        )
        
        # Format patterns for response
        formatted_patterns = []
        for pattern_type, confidence in classification.get("all_patterns", []):
            formatted_patterns.append({
                "pattern_type": pattern_type,
                "confidence": confidence,
                "description": f"{pattern_type.replace('_', ' ').title()} attack"
            })
        
        return PatternDetectionResponse(
            patterns=formatted_patterns,
            risk_level=classification["risk_level"],
            confidence=classification["threat_score"],
            recommendations=classification.get("recommendations", [])
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns/user/{user_id}", response_model=UserPatternsResponse)
async def get_user_patterns(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all attack patterns detected for a specific user
    """
    try:
        patterns = await pattern_detector.get_user_patterns(
            db=db,
            user_id=user_id
        )
        
        return UserPatternsResponse(
            user_id=user_id,
            total_patterns=len(patterns),
            patterns=patterns
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns/global")
async def get_global_patterns(
    limit: int = Query(default=50, le=200),
    min_occurrence: int = Query(default=3, ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Get most common attack patterns across all users
    
    Useful for platform-wide insights
    """
    try:
        patterns = await pattern_detector.get_common_patterns(
            db=db,
            limit=limit,
            min_occurrence=min_occurrence
        )
        
        return {
            "total_patterns": len(patterns),
            "patterns": patterns,
            "min_occurrence": min_occurrence
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns/trending")
async def get_trending_patterns(
    days: int = Query(default=7, le=30),
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trending attack patterns in the last N days
    """
    try:
        patterns = await pattern_detector.get_trending_patterns(
            db=db,
            days=days,
            limit=limit
        )
        
        return {
            "period_days": days,
            "trending_patterns": patterns
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Context Building Endpoints
# ===========================

@router.post("/insights", response_model=ContextInsightsResponse)
async def get_context_insights(
    request: ContextInsightsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive context insights for a message
    
    This is what the AI uses to make informed decisions.
    Includes:
    - Recent conversation history
    - Similar historical attacks
    - Detected patterns
    - Risk assessment
    """
    try:
        # Build enhanced context
        context = await context_builder.build_enhanced_context(
            db=db,
            user_id=request.user_id,
            current_message=request.current_message,
            include_patterns=True,
            include_semantic_search=semantic_search.enabled
        )
        
        return ContextInsightsResponse(
            immediate_history=context.get("immediate_history", []),
            similar_attacks=context.get("similar_attacks", []),
            detected_patterns=context.get("detected_patterns", []),
            risk_assessment=context.get("risk_assessment", {}),
            user_summary=context.get("user_summary"),
            metadata=context.get("metadata", {})
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/user/{user_id}")
async def get_user_context_summary(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get summarized context for a user's full history
    """
    try:
        summary = await context_builder.get_user_summary(
            db=db,
            user_id=user_id
        )
        
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# Health & Status
# ===========================

@router.get("/health")
async def context_health():
    """
    Check health of context management services
    """
    return {
        "semantic_search_enabled": semantic_search.enabled,
        "openai_configured": semantic_search.openai_client is not None,
        "pattern_detector_active": True,
        "context_builder_active": True,
        "embedding_dimensions": semantic_search.embedding_dimensions
    }

