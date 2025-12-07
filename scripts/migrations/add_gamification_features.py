#!/usr/bin/env python3
"""
Database migration to add gamification features

Adds tables for:
- Achievements
- Challenges & ChallengeProgress
- PowerUps
- Milestones

Also adds streak fields to users table.

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
from src.database import AsyncSessionLocal, create_tables
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def add_streak_columns():
    """Add streak columns to users table"""
    
    async with AsyncSessionLocal() as session:
        try:
            logger.info("🔄 Adding streak columns to users table...")
            
            # Get existing columns
            result = await session.execute(text("PRAGMA table_info(users);"))
            existing_columns = [row[1] for row in result.fetchall()]
            
            streak_columns = [
                ("current_streak", "ALTER TABLE users ADD COLUMN current_streak INTEGER DEFAULT 0;"),
                ("longest_streak", "ALTER TABLE users ADD COLUMN longest_streak INTEGER DEFAULT 0;"),
                ("last_activity_date", "ALTER TABLE users ADD COLUMN last_activity_date TIMESTAMP;"),
                ("streak_bonus_points", "ALTER TABLE users ADD COLUMN streak_bonus_points INTEGER DEFAULT 0;"),
            ]
            
            added = 0
            for column_name, query in streak_columns:
                if column_name not in existing_columns:
                    logger.info(f"  ➕ Adding column: {column_name}")
                    await session.execute(text(query))
                    added += 1
                else:
                    logger.info(f"  ✓ Column {column_name} already exists")
            
            await session.commit()
            
            if added > 0:
                logger.info(f"✅ Added {added} streak columns")
            else:
                logger.info("✅ All streak columns already exist")
            
        except Exception as e:
            logger.error(f"❌ Error adding streak columns: {e}")
            await session.rollback()
            raise


async def create_gamification_tables():
    """Create all gamification tables"""
    
    try:
        logger.info("🔄 Creating gamification tables...")
        
        # This will create all tables defined in models
        await create_tables()
        
        logger.info("✅ Gamification tables created successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise


async def main():
    """Run migration"""
    
    try:
        # Step 1: Add streak columns to users
        await add_streak_columns()
        
        # Step 2: Create gamification tables
        await create_gamification_tables()
        
        logger.info("\n" + "="*50)
        logger.info("🎉 Gamification features migration completed!")
        logger.info("="*50)
        logger.info("\nNew features available:")
        logger.info("  ✅ Daily Streak System")
        logger.info("  ✅ Challenge/Quest System")
        logger.info("  ✅ Enhanced Achievement System")
        logger.info("  ✅ Power-Ups & Boosts")
        logger.info("  ✅ Milestone Celebrations")
        
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

