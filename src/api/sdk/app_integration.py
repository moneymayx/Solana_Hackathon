"""
SDK Test API Integration Module

This module exports SDK test routers for easy integration with the main FastAPI
application. These routers are isolated and only active when SDK features are
enabled via environment variables.

Usage in main.py:
    from src.api.sdk.app_integration import include_sdk_test_routers
    include_sdk_test_routers(app)
"""
from fastapi import FastAPI
import os
import logging

logger = logging.getLogger(__name__)

# Import SDK routers conditionally
try:
    from .kora_router import router as kora_router
    KORA_AVAILABLE = True
except ImportError:
    KORA_AVAILABLE = False
    logger.warning("Kora router not available")

try:
    from .attestations_router import router as attestations_router
    ATTESTATIONS_AVAILABLE = True
except ImportError:
    ATTESTATIONS_AVAILABLE = False
    logger.warning("Attestations router not available")

try:
    from .solana_pay_router import router as solana_pay_router
    SOLANA_PAY_AVAILABLE = True
except ImportError:
    SOLANA_PAY_AVAILABLE = False
    logger.warning("Solana Pay router not available")


def include_sdk_test_routers(app: FastAPI):
    """
    Include all SDK test routers in the FastAPI app
    
    These routers are isolated with /api/sdk-test/ prefix and only work
    when the corresponding SDK is enabled via environment variables.
    
    Args:
        app: FastAPI application instance
    """
    routers_added = []
    
    # Kora SDK Router
    if KORA_AVAILABLE and os.getenv("ENABLE_KORA_SDK", "false").lower() == "true":
        app.include_router(kora_router)
        routers_added.append("Kora SDK Test (/api/sdk-test/kora/*)")
        logger.info("✅ Kora SDK test router registered")
    else:
        logger.info("⏭️  Kora SDK test router skipped (disabled or not available)")
    
    # Attestations SDK Router
    if ATTESTATIONS_AVAILABLE and os.getenv("ENABLE_ATTESTATIONS_SDK", "false").lower() == "true":
        app.include_router(attestations_router)
        routers_added.append("Attestations SDK Test (/api/sdk-test/attestations/*)")
        logger.info("✅ Attestations SDK test router registered")
    else:
        logger.info("⏭️  Attestations SDK test router skipped (disabled or not available)")
    
    # Solana Pay SDK Router
    if SOLANA_PAY_AVAILABLE and os.getenv("ENABLE_SOLANA_PAY_SDK", "false").lower() == "true":
        app.include_router(solana_pay_router)
        routers_added.append("Solana Pay SDK Test (/api/sdk-test/solana-pay/*)")
        logger.info("✅ Solana Pay SDK test router registered")
    else:
        logger.info("⏭️  Solana Pay SDK test router skipped (disabled or not available)")
    
    if routers_added:
        logger.info(f"✅ SDK test routers registered: {len(routers_added)}")
        for router_name in routers_added:
            logger.info(f"   • {router_name}")
    else:
        logger.info("ℹ️  No SDK test routers registered (all disabled or not available)")


# Export routers for individual use if needed
__all__ = [
    "kora_router" if KORA_AVAILABLE else None,
    "attestations_router" if ATTESTATIONS_AVAILABLE else None,
    "solana_pay_router" if SOLANA_PAY_AVAILABLE else None,
    "include_sdk_test_routers",
]
__all__ = [x for x in __all__ if x is not None]

