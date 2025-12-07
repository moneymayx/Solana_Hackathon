#!/usr/bin/env python3
"""
Database migration to add points system fields to users table

This migration adds:
- total_points: Total gamification points
- question_points: Points from questions
- referral_points: Points from referrals
- jailbreak_multiplier_applied: Number of 10x multipliers applied
- last_points_update: Timestamp of last points update

Author: Billions Bounty
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from sqlalchemy import text
from src.database import AsyncSessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def add_points_columns():
    """Add points system columns to users table"""
    
    async with AsyncSessionLocal() as session:
        try:
            logger.info("🔄 Starting migration: Adding points system columns...")
            
            # Check if columns already exist (SQLite-compatible)
            check_query = "PRAGMA table_info(users);"
            
            result = await session.execute(text(check_query))
            existing_columns = [row[1] for row in result.fetchall()]  # row[1] is the column name
            
            target_columns = ['total_points', 'question_points', 'referral_points', 'jailbreak_multiplier_applied', 'last_points_update']
            missing_columns = [col for col in target_columns if col not in existing_columns]
            
            if not missing_columns:
                logger.info("✅ All points columns already exist. Migration skipped.")
                return
            
            logger.info(f"📝 Found {len(target_columns) - len(missing_columns)} existing columns. Adding {len(missing_columns)} missing columns...")
            
            # Add columns if they don't exist
            migrations = [
                ("total_points", "ALTER TABLE users ADD COLUMN total_points INTEGER DEFAULT 0;"),
                ("question_points", "ALTER TABLE users ADD COLUMN question_points INTEGER DEFAULT 0;"),
                ("referral_points", "ALTER TABLE users ADD COLUMN referral_points INTEGER DEFAULT 0;"),
                ("jailbreak_multiplier_applied", "ALTER TABLE users ADD COLUMN jailbreak_multiplier_applied INTEGER DEFAULT 0;"),
                ("last_points_update", "ALTER TABLE users ADD COLUMN last_points_update TIMESTAMP;"),
            ]
            
            for column_name, query in migrations:
                if column_name in missing_columns:
                    logger.info(f"  Adding column: {column_name}")
                    await session.execute(text(query))
                else:
                    logger.info(f"  ✓ Column {column_name} already exists")
            
            await session.commit()
            
            logger.info("✅ Migration completed successfully!")
            logger.info("📊 Points system columns are now available in the users table.")
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            await session.rollback()
            raise


async def recalculate_all_points():
    """Recalculate points for all existing users"""
    
    from src.services.points_service import points_service
    
    async with AsyncSessionLocal() as session:
        try:
            logger.info("🔄 Recalculating points for all users...")
            
            result = await points_service.recalculate_all_user_points(session)
            
            logger.info(f"✅ Points recalculation completed!")
            logger.info(f"   Total users: {result['total_users']}")
            logger.info(f"   Updated: {result['updated']}")
            logger.info(f"   Errors: {result['errors']}")
            
        except Exception as e:
            logger.error(f"❌ Points recalculation failed: {e}")
            raise


async def main():
    """Run migration"""
    
    try:
        # Step 1: Add columns
        await add_points_columns()
        
        # Step 2: Recalculate points for existing users
        logger.info("\n")
        await recalculate_all_points()
        
        logger.info("\n" + "="*50)
        logger.info("🎉 Points system migration completed successfully!")
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

