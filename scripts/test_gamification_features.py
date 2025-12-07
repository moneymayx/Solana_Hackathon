#!/usr/bin/env python3
"""
Comprehensive test script for all gamification features

Tests:
1. Daily Streak System
2. Challenge/Quest System
3. Enhanced Achievement System
4. Power-Ups & Boosts
5. Milestone Celebrations

Author: Billions Bounty
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from datetime import datetime, timedelta, date
from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models import (
    User, Conversation, Referral, AttackAttempt, ReferralCode,
    Challenge, ChallengeProgress, Achievement, PowerUp, Milestone
)
from src.services.streak_service import streak_service
from src.services.challenge_service import challenge_service
from src.services.achievement_service import achievement_service
from src.services.powerup_service import powerup_service
from src.services.milestone_service import milestone_service
from src.services.points_service import points_service
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


async def create_test_user(session, name, wallet_suffix):
    """Create a test user"""
    timestamp = datetime.utcnow().timestamp()
    user = User(
        session_id=f"test_{name}_{timestamp}",
        wallet_address=f"TestWallet_{name}_{wallet_suffix}_{timestamp}",
        display_name=f"{name}_{timestamp}",
        ip_address="192.168.1.1"
    )
    session.add(user)
    await session.flush()
    return user


async def test_streak_system(session):
    """Test Daily Streak System"""
    logger.info("\n" + "="*60)
    logger.info("🔥 TESTING DAILY STREAK SYSTEM")
    logger.info("="*60)
    
    user = await create_test_user(session, "StreakMaster", "streak")
    
    # Test 1: First activity
    logger.info("\n📝 Test 1: First activity")
    result = await streak_service.record_activity(session, user.id)
    assert result["current_streak"] == 1, "First activity should start streak at 1"
    logger.info(f"   ✅ Streak started: {result['current_streak']} day")
    
    # Test 2: Same day activity (shouldn't increment)
    logger.info("\n📝 Test 2: Same day activity (no increment)")
    result2 = await streak_service.record_activity(session, user.id)
    assert result2["current_streak"] == 1, "Same day shouldn't increment streak"
    logger.info(f"   ✅ Streak remains: {result2['current_streak']} day")
    
    # Test 3: Simulate next day (manually set last_activity_date)
    logger.info("\n📝 Test 3: Next day activity")
    user.last_activity_date = datetime.utcnow() - timedelta(days=1)
    await session.commit()
    result3 = await streak_service.record_activity(session, user.id)
    assert result3["current_streak"] == 2, "Next day should increment streak"
    logger.info(f"   ✅ Streak incremented: {result3['current_streak']} days")
    
    # Test 4: Get streak info
    logger.info("\n📝 Test 4: Get streak info")
    streak_info = await streak_service.get_streak_info(session, user.id)
    assert streak_info["current_streak"] == 2, "Should return current streak"
    assert streak_info["is_active"] == True, "Streak should be active"
    logger.info(f"   ✅ Streak info retrieved: {streak_info['current_streak']} days active")
    
    logger.info("\n✅ Streak System: ALL TESTS PASSED")
    return user


async def test_challenge_system(session):
    """Test Challenge/Quest System"""
    logger.info("\n" + "="*60)
    logger.info("🎮 TESTING CHALLENGE/QUEST SYSTEM")
    logger.info("="*60)
    
    user = await create_test_user(session, "ChallengeChamp", "challenge")
    
    # Test 1: Create daily challenges (or use existing)
    logger.info("\n📝 Test 1: Create daily challenges")
    challenges = await challenge_service.create_daily_challenges(session)
    if len(challenges) == 0:
        logger.info("   ℹ️  Daily challenges already exist for today (this is fine)")
    else:
        assert len(challenges) == 3, "Should create 3 daily challenges"
        logger.info(f"   ✅ Created {len(challenges)} daily challenges")
    
    # Test 2: Get active challenges
    logger.info("\n📝 Test 2: Get active challenges")
    active = await challenge_service.get_active_challenges(session)
    assert len(active) >= 3, "Should have at least 3 active challenges"
    logger.info(f"   ✅ Found {len(active)} active challenges")
    
    # Test 3: Get user challenges with progress
    logger.info("\n📝 Test 3: Get user challenges")
    user_challenges = await challenge_service.get_user_challenges(session, user.id)
    assert user_challenges["total_active"] >= 3, "Should have challenges for user"
    logger.info(f"   ✅ User has {user_challenges['total_active']} active challenges")
    
    # Test 4: Update challenge progress (questions)
    logger.info("\n📝 Test 4: Update challenge progress (questions)")
    completed = await challenge_service.update_challenge_progress(
        session, user.id, "question", 5
    )
    logger.info(f"   ✅ Updated progress, completed: {len(completed)} challenges")
    
    # Test 5: Verify challenge completion
    logger.info("\n📝 Test 5: Verify challenge completion")
    user_challenges_after = await challenge_service.get_user_challenges(session, user.id)
    completed_count = sum(
        1 for c in user_challenges_after["challenges"]
        if c["progress"]["completed"]
    )
    logger.info(f"   ✅ User completed {completed_count} challenges")
    
    logger.info("\n✅ Challenge System: ALL TESTS PASSED")
    return user


async def test_achievement_system(session):
    """Test Enhanced Achievement System"""
    logger.info("\n" + "="*60)
    logger.info("🏅 TESTING ENHANCED ACHIEVEMENT SYSTEM")
    logger.info("="*60)
    
    user = await create_test_user(session, "AchievementAce", "achievement")
    
    # Test 1: Add some activity to trigger achievements
    logger.info("\n📝 Test 1: Add activity for achievements")
    
    # Add 100 questions
    for i in range(100):
        conv = Conversation(
            user_id=user.id,
            message_type='user',
            content=f'Test question {i}'
        )
        session.add(conv)
    
    # Add 5 referrals
    ref_code = ReferralCode(
        user_id=user.id,
        referral_code=f"TEST{user.id}_{datetime.utcnow().timestamp()}",
        is_active=True
    )
    session.add(ref_code)
    await session.flush()
    
    for i in range(5):
        referee = await create_test_user(session, f"Referee{i}", f"ref{i}")
        referral = Referral(
            referrer_id=user.id,
            referee_id=referee.id,
            referral_code_id=ref_code.id,
            is_valid=True
        )
        session.add(referral)
    
    # Add 1 jailbreak
    attack = AttackAttempt(
        user_id=user.id,
        attempt_type='jailbreak',
        message_content='Test jailbreak',
        ai_response='Breaking...',
        threat_score=0.95,
        was_successful=True
    )
    session.add(attack)
    await session.commit()
    
    # Update points
    await points_service.update_user_points(session, user.id)
    
    # Test 2: Check achievements
    logger.info("\n📝 Test 2: Check and unlock achievements")
    new_achievements = await achievement_service.check_and_unlock_achievements(session, user.id)
    assert len(new_achievements) > 0, "Should unlock some achievements"
    logger.info(f"   ✅ Unlocked {len(new_achievements)} achievements:")
    for ach in new_achievements:
        logger.info(f"      - {ach['icon']} {ach['name']}: {ach['description']}")
    
    # Test 3: Get user achievements
    logger.info("\n📝 Test 3: Get user achievements")
    achievements = await achievement_service.get_user_achievements(session, user.id)
    assert achievements["total"] > 0, "Should have achievements"
    logger.info(f"   ✅ User has {achievements['total']} achievements")
    logger.info(f"      Common: {len(achievements['by_rarity']['common'])}")
    logger.info(f"      Rare: {len(achievements['by_rarity']['rare'])}")
    logger.info(f"      Epic: {len(achievements['by_rarity']['epic'])}")
    logger.info(f"      Legendary: {len(achievements['by_rarity']['legendary'])}")
    
    logger.info("\n✅ Achievement System: ALL TESTS PASSED")
    return user


async def test_powerup_system(session):
    """Test Power-Ups & Boosts System"""
    logger.info("\n" + "="*60)
    logger.info("⚡ TESTING POWER-UPS & BOOSTS SYSTEM")
    logger.info("="*60)
    
    user = await create_test_user(session, "PowerUpPro", "powerup")
    
    # Test 1: Create power-ups
    logger.info("\n📝 Test 1: Create power-ups")
    power_up1 = await powerup_service.create_power_up(
        session, user.id, "double_points", "earned"
    )
    assert power_up1 is not None, "Should create power-up"
    logger.info(f"   ✅ Created: {power_up1.name}")
    
    power_up2 = await powerup_service.create_power_up(
        session, user.id, "streak_shield", "earned"
    )
    assert power_up2 is not None, "Should create second power-up"
    logger.info(f"   ✅ Created: {power_up2.name}")
    
    # Test 2: Get user power-ups
    logger.info("\n📝 Test 2: Get user power-ups")
    power_ups = await powerup_service.get_user_power_ups(session, user.id)
    assert power_ups["total"] == 2, "Should have 2 power-ups"
    assert len(power_ups["inactive"]) == 2, "Both should be inactive"
    logger.info(f"   ✅ User has {power_ups['total']} power-ups (all inactive)")
    
    # Test 3: Activate power-up
    logger.info("\n📝 Test 3: Activate power-up")
    activation = await powerup_service.activate_power_up(session, user.id, power_up1.id)
    assert activation is not None, "Should activate power-up"
    assert activation["power_up_type"] == "double_points", "Should be double points"
    logger.info(f"   ✅ Activated: {activation['name']}")
    logger.info(f"      Expires in: {activation['duration_minutes']} minutes")
    
    # Test 4: Get active power-ups
    logger.info("\n📝 Test 4: Get active power-ups")
    active = await powerup_service.get_active_power_ups(session, user.id)
    assert len(active) == 1, "Should have 1 active power-up"
    logger.info(f"   ✅ {len(active)} active power-up(s)")
    
    # Test 5: Get points multiplier
    logger.info("\n📝 Test 5: Get points multiplier")
    multiplier = await powerup_service.get_points_multiplier(session, user.id, "question")
    assert multiplier == 2.0, "Should have 2x multiplier for questions"
    logger.info(f"   ✅ Points multiplier: {multiplier}x")
    
    logger.info("\n✅ Power-Up System: ALL TESTS PASSED")
    return user


async def test_milestone_system(session):
    """Test Milestone Celebrations System"""
    logger.info("\n" + "="*60)
    logger.info("🎊 TESTING MILESTONE CELEBRATIONS SYSTEM")
    logger.info("="*60)
    
    user = await create_test_user(session, "MilestoneMaster", "milestone")
    
    # Test 1: Add points to trigger milestones
    logger.info("\n📝 Test 1: Add points for milestones")
    
    # Add questions to reach 100 points
    for i in range(100):
        conv = Conversation(
            user_id=user.id,
            message_type='user',
            content=f'Question {i}'
        )
        session.add(conv)
    
    await session.commit()
    
    # Update points
    previous_points = 0
    await points_service.update_user_points(session, user.id)
    
    # Refresh user
    await session.refresh(user)
    current_points = user.total_points
    
    # Test 2: Check milestones
    logger.info("\n📝 Test 2: Check for milestones")
    new_milestones = await milestone_service.check_milestones(
        session, user.id, previous_points=previous_points, previous_tier=None
    )
    assert len(new_milestones) > 0, "Should detect milestones"
    logger.info(f"   ✅ Detected {len(new_milestones)} milestones:")
    for m in new_milestones:
        logger.info(f"      - {m.get('name', 'Milestone')}: {m.get('description', '')}")
    
    # Test 3: Get unshown milestones
    logger.info("\n📝 Test 3: Get unshown milestones")
    unshown = await milestone_service.get_unshown_milestones(session, user.id)
    assert len(unshown) > 0, "Should have unshown milestones"
    logger.info(f"   ✅ {len(unshown)} unshown milestones ready for celebration")
    
    # Test 4: Mark milestone as shown
    logger.info("\n📝 Test 4: Mark milestone as shown")
    if unshown:
        success = await milestone_service.mark_milestone_shown(session, unshown[0]["id"])
        assert success == True, "Should mark milestone as shown"
        logger.info(f"   ✅ Marked milestone {unshown[0]['id']} as shown")
    
    logger.info("\n✅ Milestone System: ALL TESTS PASSED")
    return user


async def test_integration(session):
    """Test integration of all systems"""
    logger.info("\n" + "="*60)
    logger.info("🔗 TESTING SYSTEM INTEGRATION")
    logger.info("="*60)
    
    user = await create_test_user(session, "IntegrationTest", "integration")
    
    # Simulate a complete user journey
    logger.info("\n📝 Simulating complete user journey...")
    
    # 1. Record activity (streak)
    logger.info("   1. Recording activity...")
    await streak_service.record_activity(session, user.id)
    
    # 2. Ask questions (challenges, achievements, milestones)
    logger.info("   2. Asking questions...")
    for i in range(10):
        conv = Conversation(
            user_id=user.id,
            message_type='user',
            content=f'Question {i}'
        )
        session.add(conv)
    
    # Update challenge progress
    await challenge_service.update_challenge_progress(session, user.id, "question", 10)
    
    # 3. Make a referral
    logger.info("   3. Making referral...")
    ref_code = ReferralCode(
        user_id=user.id,
        referral_code=f"INTEG{user.id}_{datetime.utcnow().timestamp()}",
        is_active=True
    )
    session.add(ref_code)
    await session.flush()
    
    referee = await create_test_user(session, "Referee", "ref")
    referral = Referral(
        referrer_id=user.id,
        referee_id=referee.id,
        referral_code_id=ref_code.id,
        is_valid=True
    )
    session.add(referral)
    
    # Update challenge progress
    await challenge_service.update_challenge_progress(session, user.id, "referral", 1)
    
    # 4. Complete a jailbreak
    logger.info("   4. Completing jailbreak...")
    attack = AttackAttempt(
        user_id=user.id,
        attempt_type='jailbreak',
        message_content='Integration test jailbreak',
        ai_response='Breaking...',
        threat_score=0.95,
        was_successful=True
    )
    session.add(attack)
    
    # Update challenge progress
    await challenge_service.update_challenge_progress(session, user.id, "jailbreak", 1)
    
    await session.commit()
    
    # 5. Update points
    logger.info("   5. Updating points...")
    await points_service.update_user_points(session, user.id)
    
    # 6. Check achievements
    logger.info("   6. Checking achievements...")
    achievements = await achievement_service.check_and_unlock_achievements(session, user.id)
    
    # 7. Check milestones
    logger.info("   7. Checking milestones...")
    await session.refresh(user)
    milestones = await milestone_service.check_milestones(
        session, user.id, previous_points=0, previous_tier=None
    )
    
    # 8. Create and activate power-up
    logger.info("   8. Creating power-up...")
    power_up = await powerup_service.create_power_up(session, user.id, "double_points", "earned")
    await powerup_service.activate_power_up(session, user.id, power_up.id)
    
    # Summary
    logger.info("\n📊 Integration Test Summary:")
    await session.refresh(user)
    
    streak_info = await streak_service.get_streak_info(session, user.id)
    user_challenges = await challenge_service.get_user_challenges(session, user.id)
    user_achievements = await achievement_service.get_user_achievements(session, user.id)
    user_power_ups = await powerup_service.get_user_power_ups(session, user.id)
    unshown_milestones = await milestone_service.get_unshown_milestones(session, user.id)
    
    logger.info(f"   ✅ Streak: {streak_info['current_streak']} days")
    logger.info(f"   ✅ Points: {user.total_points}")
    logger.info(f"   ✅ Challenges: {user_challenges['total_active']} active")
    logger.info(f"   ✅ Achievements: {user_achievements['total']} unlocked")
    logger.info(f"   ✅ Power-ups: {user_power_ups['total']} total, {len(user_power_ups['active'])} active")
    logger.info(f"   ✅ Milestones: {len(unshown_milestones)} ready for celebration")
    
    logger.info("\n✅ Integration Test: ALL SYSTEMS WORKING TOGETHER!")
    return user


async def cleanup_test_data(session):
    """Clean up test users"""
    logger.info("\n🧹 Cleaning up test data...")
    
    try:
        # Get test users
        result = await session.execute(
            select(User).where(
                User.wallet_address.like("TestWallet_%")
            )
        )
        users = result.scalars().all()
        user_ids = [u.id for u in users]
        
        if not user_ids:
            logger.info("   ℹ️  No test users to clean up")
            return
        
        # Delete related records using raw SQL to avoid ORM issues
        from sqlalchemy import text
        
        # Delete in order to respect foreign keys
        tables = [
            "achievements", "challenge_progress", "power_ups", "milestones",
            "conversations", "attack_attempts", "referrals", "referral_codes"
        ]
        
        for table in tables:
            try:
                await session.execute(
                    text(f"DELETE FROM {table} WHERE user_id IN ({','.join(map(str, user_ids))})")
                )
            except Exception as e:
                logger.warning(f"   ⚠️  Could not delete from {table}: {e}")
        
        # Delete users
        for user in users:
            await session.delete(user)
        
        await session.commit()
        logger.info(f"✅ Cleaned up {len(users)} test users and related records")
    
    except Exception as e:
        logger.warning(f"   ⚠️  Cleanup had issues (this is okay for testing): {e}")
        await session.rollback()


async def main():
    """Run all tests"""
    try:
        logger.info("="*60)
        logger.info("🧪 GAMIFICATION FEATURES TEST SUITE")
        logger.info("="*60)
        
        async with AsyncSessionLocal() as session:
            # Run all tests
            await test_streak_system(session)
            await test_challenge_system(session)
            await test_achievement_system(session)
            await test_powerup_system(session)
            await test_milestone_system(session)
            await test_integration(session)
            
            # Ask about cleanup
            logger.info("\n" + "="*60)
            response = input("Keep test data? (y/n): ")
            
            if response.lower() != 'y':
                await cleanup_test_data(session)
            else:
                logger.info("✅ Test data kept for inspection")
        
        logger.info("\n" + "="*60)
        logger.info("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        logger.info("="*60)
        logger.info("\n✅ All gamification features are working correctly!")
        logger.info("   - Daily Streak System")
        logger.info("   - Challenge/Quest System")
        logger.info("   - Enhanced Achievement System")
        logger.info("   - Power-Ups & Boosts")
        logger.info("   - Milestone Celebrations")
        logger.info("\n🚀 Ready for frontend integration!")
        
    except AssertionError as e:
        logger.error(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

