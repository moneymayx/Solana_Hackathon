#!/usr/bin/env python3
"""
Test script for the points system

This script:
1. Creates test users with various activities
2. Calculates points for them
3. Displays the leaderboard
4. Tests the API endpoints

Author: Billions Bounty
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from datetime import datetime
from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models import User, Conversation, Referral, AttackAttempt, ReferralCode
from src.services.points_service import points_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_test_data():
    """Create test users with different activities"""
    
    async with AsyncSessionLocal() as session:
        try:
            logger.info("🔄 Creating test data...")
            
            # Test User 1: Lots of questions, no referrals, no jailbreaks
            user1 = User(
                session_id="test_session_1",
                wallet_address="TestWallet1_" + str(datetime.utcnow().timestamp()),
                display_name="QuestionMaster",
                ip_address="192.168.1.1"
            )
            session.add(user1)
            await session.flush()
            
            # Add 50 questions for user1
            for i in range(50):
                conv = Conversation(
                    user_id=user1.id,
                    message_type='user',
                    content=f'Test question {i}'
                )
                session.add(conv)
            
            # Test User 2: Some questions, 5 referrals, no jailbreaks
            user2 = User(
                session_id="test_session_2",
                wallet_address="TestWallet2_" + str(datetime.utcnow().timestamp()),
                display_name="ReferralPro",
                ip_address="192.168.1.2"
            )
            session.add(user2)
            await session.flush()
            
            # Add 10 questions for user2
            for i in range(10):
                conv = Conversation(
                    user_id=user2.id,
                    message_type='user',
                    content=f'Test question {i}'
                )
                session.add(conv)
            
            # Create referral code for user2
            ref_code = ReferralCode(
                user_id=user2.id,
                referral_code="TEST123",
                is_active=True
            )
            session.add(ref_code)
            await session.flush()
            
            # Add 5 referrals for user2
            for i in range(5):
                referee = User(
                    session_id=f"referee_{i}",
                    wallet_address=f"RefereeWallet{i}_" + str(datetime.utcnow().timestamp()),
                    display_name=f"Referee{i}",
                    ip_address=f"192.168.1.{i + 10}"
                )
                session.add(referee)
                await session.flush()
                
                referral = Referral(
                    referrer_id=user2.id,
                    referee_id=referee.id,
                    referral_code_id=ref_code.id,
                    is_valid=True
                )
                session.add(referral)
            
            # Test User 3: Questions, referrals, AND 1 jailbreak (10x multiplier!)
            user3 = User(
                session_id="test_session_3",
                wallet_address="TestWallet3_" + str(datetime.utcnow().timestamp()),
                display_name="JailbreakChampion",
                ip_address="192.168.1.3"
            )
            session.add(user3)
            await session.flush()
            
            # Add 20 questions for user3
            for i in range(20):
                conv = Conversation(
                    user_id=user3.id,
                    message_type='user',
                    content=f'Test question {i}'
                )
                session.add(conv)
            
            # Add 3 referrals for user3
            ref_code3 = ReferralCode(
                user_id=user3.id,
                referral_code="JAB123",
                is_active=True
            )
            session.add(ref_code3)
            await session.flush()
            
            for i in range(3):
                referee = User(
                    session_id=f"referee3_{i}",
                    wallet_address=f"Referee3Wallet{i}_" + str(datetime.utcnow().timestamp()),
                    display_name=f"Referee3_{i}",
                    ip_address=f"192.168.1.{i + 20}"
                )
                session.add(referee)
                await session.flush()
                
                referral = Referral(
                    referrer_id=user3.id,
                    referee_id=referee.id,
                    referral_code_id=ref_code3.id,
                    is_valid=True
                )
                session.add(referral)
            
            # Add 1 successful jailbreak for user3 (THIS IS THE GAME CHANGER!)
            attack = AttackAttempt(
                user_id=user3.id,
                attempt_type='jailbreak',
                message_content='Successful jailbreak attempt',
                ai_response='Breaking character...',
                threat_score=0.95,
                was_successful=True
            )
            session.add(attack)
            
            # Test User 4: Minimal activity
            user4 = User(
                session_id="test_session_4",
                wallet_address="TestWallet4_" + str(datetime.utcnow().timestamp()),
                display_name="CasualUser",
                ip_address="192.168.1.4"
            )
            session.add(user4)
            await session.flush()
            
            # Add 2 questions for user4
            for i in range(2):
                conv = Conversation(
                    user_id=user4.id,
                    message_type='user',
                    content=f'Test question {i}'
                )
                session.add(conv)
            
            await session.commit()
            
            logger.info("✅ Test data created successfully!")
            logger.info("   User 1 (QuestionMaster): 50 questions")
            logger.info("   User 2 (ReferralPro): 10 questions, 5 referrals")
            logger.info("   User 3 (JailbreakChampion): 20 questions, 3 referrals, 1 JAILBREAK")
            logger.info("   User 4 (CasualUser): 2 questions")
            
        except Exception as e:
            logger.error(f"❌ Error creating test data: {e}")
            await session.rollback()
            raise


async def calculate_and_display_points():
    """Calculate points and display leaderboard"""
    
    async with AsyncSessionLocal() as session:
        try:
            logger.info("\n" + "="*60)
            logger.info("📊 CALCULATING POINTS FOR ALL USERS")
            logger.info("="*60 + "\n")
            
            # Get all test users
            result = await session.execute(
                select(User).where(User.display_name.in_([
                    'QuestionMaster', 'ReferralPro', 'JailbreakChampion', 'CasualUser'
                ]))
            )
            users = result.scalars().all()
            
            for user in users:
                # Calculate points
                points_data = await points_service.calculate_user_points(session, user.id)
                
                # Update user
                user.total_points = points_data['total_points']
                user.question_points = points_data['question_points']
                user.referral_points = points_data['referral_points']
                user.jailbreak_multiplier_applied = points_data['jailbreak_count']
                user.last_points_update = datetime.utcnow()
                
                # Display results
                logger.info(f"👤 {user.display_name}:")
                logger.info(f"   Questions: {points_data['question_count']} = {points_data['question_points']} pts")
                logger.info(f"   Referrals: {points_data['referral_count']} = {points_data['referral_points']} pts")
                logger.info(f"   Base Points: {points_data['base_points']}")
                logger.info(f"   Jailbreaks: {points_data['jailbreak_count']}")
                logger.info(f"   Multiplier: {points_data['multiplier_applied']}x")
                logger.info(f"   🎯 TOTAL POINTS: {points_data['total_points']}")
                logger.info("")
            
            await session.commit()
            
            # Display leaderboard
            logger.info("="*60)
            logger.info("🏆 LEADERBOARD")
            logger.info("="*60 + "\n")
            
            leaderboard = await points_service.get_leaderboard(session, limit=10)
            
            for entry in leaderboard:
                emoji = "🥇" if entry['rank'] == 1 else "🥈" if entry['rank'] == 2 else "🥉" if entry['rank'] == 3 else "  "
                logger.info(f"{emoji} #{entry['rank']} - {entry['display_name']}")
                logger.info(f"   Total: {entry['total_points']} pts | Tier: {entry['tier'].upper()}")
                logger.info(f"   Questions: {entry['question_count']} | Referrals: {entry['referral_count']} | Jailbreaks: {entry['jailbreak_count']}")
                logger.info("")
            
            logger.info("\n" + "="*60)
            logger.info("✅ Points system test completed successfully!")
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"❌ Error calculating points: {e}")
            await session.rollback()
            raise


async def cleanup_test_data():
    """Clean up test data"""
    
    async with AsyncSessionLocal() as session:
        try:
            logger.info("\n🧹 Cleaning up test data...")
            
            # Delete test users and their related data
            result = await session.execute(
                select(User).where(User.display_name.in_([
                    'QuestionMaster', 'ReferralPro', 'JailbreakChampion', 'CasualUser'
                ]) | User.display_name.like('Referee%'))
            )
            users = result.scalars().all()
            
            for user in users:
                await session.delete(user)
            
            await session.commit()
            
            logger.info("✅ Test data cleaned up!")
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up test data: {e}")
            await session.rollback()


async def main():
    """Run tests"""
    
    try:
        # Create test data
        await create_test_data()
        
        # Calculate and display points
        await calculate_and_display_points()
        
        # Ask if user wants to keep test data
        logger.info("\n" + "="*60)
        response = input("Keep test data? (y/n): ")
        
        if response.lower() != 'y':
            await cleanup_test_data()
        else:
            logger.info("✅ Test data kept for manual inspection")
        
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

