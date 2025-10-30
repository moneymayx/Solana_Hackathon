"""
API Integration Module

This module exports all enhancement API routers for easy integration
with the main FastAPI application.

Usage in main.py:
    from src.api.app_integration import include_enhancement_routers
    include_enhancement_routers(app)
"""
from fastapi import FastAPI
from .context_router import router as context_router
from .team_router import router as team_router


def include_enhancement_routers(app: FastAPI):
    """
    Include all enhancement API routers in the FastAPI app
    
    Args:
        app: FastAPI application instance
    """
    # Phase 1: Context Window Management
    app.include_router(context_router)
    
    # Phase 2: Token Economics - REMOVED (token discount functionality discontinued)
    # app.include_router(token_router)
    
    # Phase 3: Team Collaboration
    app.include_router(team_router)
    
    print("✅ Enhancement API routers registered:")
    print("   • Phase 1: Context Management (/api/context/*)")
    print("   • Phase 2: Token Economics (/api/token/*) - REMOVED")
    print("   • Phase 3: Team Collaboration (/api/teams/*)")


# Export routers for individual use if needed
__all__ = [
    "context_router",
    "team_router",
    "include_enhancement_routers"
]

