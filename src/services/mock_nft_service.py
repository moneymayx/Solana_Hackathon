"""
Mock NFT Service - For Testing Without Real NFTs
Similar to mock payment service, allows testing NFT verification without owning NFTs
"""
import os
import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockNftService:
    """
    Mock NFT verification service for testing.
    In mock mode, always returns that user has eligible NFTs.
    """
    
    def __init__(self):
        logger.info("🎨 Mock NFT Service initialized")
    
    async def check_nft_ownership(
        self,
        session: AsyncSession,
        wallet_address: str
    ) -> Dict[str, Any]:
        """
        Mock check for NFT ownership.
        Always returns true in mock mode for testing.
        """
        try:
            logger.info(f"🎨 MOCK NFT verification for {wallet_address}")
            
            # In mock mode, user always "has" an NFT
            return {
                "success": True,
                "has_nft": True,
                "nft_count": 1,
                "eligible_nfts": [
                    {
                        "mint": "MOCK_NFT_11111111111111111111111111111",
                        "name": "Test NFT #1",
                        "collection": "Billions Bounty Test Collection",
                        "is_mock": True
                    }
                ],
                "is_mock": True,
                "message": "🎨 TEST MODE: Mock NFT detected. In production, this would verify real NFTs."
            }
            
        except Exception as e:
            logger.error(f"Error in mock NFT check: {e}")
            return {
                "success": False,
                "has_nft": False,
                "error": str(e),
                "is_mock": True
            }
    
    async def verify_and_grant_questions(
        self,
        session: AsyncSession,
        wallet_address: str,
        questions_to_grant: int = 5
    ) -> Dict[str, Any]:
        """
        Verify NFT ownership and grant free questions.
        In mock mode, always succeeds.
        """
        try:
            logger.info(f"🎨 MOCK NFT verification + question grant for {wallet_address}")
            
            # Check NFT ownership (mock)
            nft_check = await self.check_nft_ownership(session, wallet_address)
            
            if not nft_check["has_nft"]:
                return {
                    "success": False,
                    "verified": False,
                    "error": "No eligible NFTs found",
                    "is_mock": True
                }
            
            # Grant free questions
            from .free_question_service import free_question_service
            from ..models import User
            from sqlalchemy import select
            
            # Get user by wallet address
            user_result = await session.execute(
                select(User).where(User.wallet_address == wallet_address)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                # Create user if doesn't exist
                logger.warning(f"⚠️ User not found for wallet {wallet_address}, creating new user")
                from src.repositories import UserRepository
                import uuid
                user_repo = UserRepository(session)
                
                # Create user with session_id
                user = await user_repo.create_user(
                    session_id=str(uuid.uuid4())
                )
                
                # Then update the wallet address
                await user_repo.update_user_wallet(user.id, wallet_address)
                
                # Refresh user to get updated wallet address
                await session.refresh(user)
                
                logger.info(f"✅ Created new user {user.id} for wallet {wallet_address}")
            
            # Grant free questions
            result = await free_question_service.grant_nft_questions(
                session=session,
                user_id=user.id,
                nft_mint="MOCK_NFT_11111111111111111111111111111"
            )
            logger.info(f"✅ Grant result for user {user.id}: {result}")
            
            # Check if granting was successful
            if not result.get("success"):
                logger.warning(f"⚠️ Failed to grant questions: {result.get('error')}")
                return {
                    "success": False,
                    "verified": False,
                    "error": result.get("error", "Failed to grant questions"),
                    "is_mock": True
                }
            
            return {
                "success": True,
                "verified": True,
                "has_nft": True,
                "questions_granted": result.get("questions_granted", questions_to_grant),
                "nft_info": nft_check["eligible_nfts"][0],
                "is_mock": True,
                "message": f"🎨 TEST: NFT verified! Granted {result.get('questions_granted', questions_to_grant)} free questions (no real NFT required)"
            }
            
        except Exception as e:
            logger.error(f"Error verifying mock NFT: {e}")
            return {
                "success": False,
                "verified": False,
                "error": str(e),
                "is_mock": True
            }

# Global instance
mock_nft_service = MockNftService()

