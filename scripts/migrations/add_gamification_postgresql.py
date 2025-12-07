#!/usr/bin/env python3
"""
PostgreSQL-compatible migration to add gamification features
Adds columns to users table for points and streaks
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


async def detect_database_type(session):
    """Detect if we're using PostgreSQL or SQLite"""
    try:
        # Try PostgreSQL-specific query
        result = await session.execute(text("SELECT version();"))
        version = result.scalar()
        if "PostgreSQL" in version:
            return "postgresql"
    except:
        pass
    
    # Check DATABASE_URL
    db_url = os.getenv("DATABASE_URL", "")
    if "postgresql" in db_url.lower() or "postgres" in db_url.lower():
        return "postgresql"
    
    return "sqlite"


async def add_gamification_columns():
    """Add gamification columns to users table (database-agnostic)"""
    
    async with AsyncSessionLocal() as session:
        try:
            db_type = await detect_database_type(session)
            logger.info(f"🔄 Adding gamification columns to users table ({db_type.upper()})...")
            
            # Check if columns exist (database-specific)
            if db_type == "postgresql":
                check_query = """
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name IN ('total_points', 'question_points', 'referral_points', 
                                        'jailbreak_multiplier_applied', 'last_points_update',
                                        'current_streak', 'longest_streak', 'last_activity_date', 
                                        'streak_bonus_points');
                """
            else:
                # SQLite
                check_query = "PRAGMA table_info(users);"
            
            result = await session.execute(text(check_query))
            
            if db_type == "postgresql":
                existing_columns = {row[0] for row in result.fetchall()}
            else:
                existing_columns = {row[1] for row in result.fetchall()}  # row[1] is column name in SQLite
            
            # Define all columns to add (database-specific syntax)
            if db_type == "postgresql":
                columns_to_add = [
                    ("total_points", "ALTER TABLE users ADD COLUMN IF NOT EXISTS total_points INTEGER DEFAULT 0;"),
                    ("question_points", "ALTER TABLE users ADD COLUMN IF NOT EXISTS question_points INTEGER DEFAULT 0;"),
                    ("referral_points", "ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_points INTEGER DEFAULT 0;"),
                    ("jailbreak_multiplier_applied", "ALTER TABLE users ADD COLUMN IF NOT EXISTS jailbreak_multiplier_applied INTEGER DEFAULT 0;"),
                    ("last_points_update", "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_points_update TIMESTAMP;"),
                    ("current_streak", "ALTER TABLE users ADD COLUMN IF NOT EXISTS current_streak INTEGER DEFAULT 0;"),
                    ("longest_streak", "ALTER TABLE users ADD COLUMN IF NOT EXISTS longest_streak INTEGER DEFAULT 0;"),
                    ("last_activity_date", "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_activity_date TIMESTAMP;"),
                    ("streak_bonus_points", "ALTER TABLE users ADD COLUMN IF NOT EXISTS streak_bonus_points INTEGER DEFAULT 0;"),
                ]
            else:
                # SQLite doesn't support IF NOT EXISTS in ALTER TABLE
                columns_to_add = [
                    ("total_points", "ALTER TABLE users ADD COLUMN total_points INTEGER DEFAULT 0;"),
                    ("question_points", "ALTER TABLE users ADD COLUMN question_points INTEGER DEFAULT 0;"),
                    ("referral_points", "ALTER TABLE users ADD COLUMN referral_points INTEGER DEFAULT 0;"),
                    ("jailbreak_multiplier_applied", "ALTER TABLE users ADD COLUMN jailbreak_multiplier_applied INTEGER DEFAULT 0;"),
                    ("last_points_update", "ALTER TABLE users ADD COLUMN last_points_update TIMESTAMP;"),
                    ("current_streak", "ALTER TABLE users ADD COLUMN current_streak INTEGER DEFAULT 0;"),
                    ("longest_streak", "ALTER TABLE users ADD COLUMN longest_streak INTEGER DEFAULT 0;"),
                    ("last_activity_date", "ALTER TABLE users ADD COLUMN last_activity_date TIMESTAMP;"),
                    ("streak_bonus_points", "ALTER TABLE users ADD COLUMN streak_bonus_points INTEGER DEFAULT 0;"),
                ]
            
            added = 0
            for column_name, query in columns_to_add:
                if column_name not in existing_columns:
                    logger.info(f"  ➕ Adding column: {column_name}")
                    try:
                        await session.execute(text(query))
                        added += 1
                    except Exception as e:
                        # If column already exists (race condition), skip
                        error_msg = str(e).lower()
                        if "already exists" in error_msg or "duplicate" in error_msg or "duplicate column" in error_msg:
                            logger.info(f"  ✓ Column {column_name} already exists (skipped)")
                        else:
                            raise
                else:
                    logger.info(f"  ✓ Column {column_name} already exists")
            
            await session.commit()
            
            if added > 0:
                logger.info(f"✅ Added {added} new columns to users table")
            else:
                logger.info("✅ All gamification columns already exist")
            
        except Exception as e:
            logger.error(f"❌ Error adding columns: {e}")
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
        # Step 1: Add gamification columns to users
        await add_gamification_columns()
        
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

