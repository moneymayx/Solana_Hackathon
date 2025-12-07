#!/usr/bin/env python3
"""
Comprehensive migration to sync users table with model definition

This adds all missing columns to match the current User model.
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


async def sync_user_table():
    """Add all missing columns to users table"""
    
    async with AsyncSessionLocal() as session:
        try:
            logger.info("🔄 Syncing users table with model definition...")
            
            # Get existing columns
            result = await session.execute(text("PRAGMA table_info(users);"))
            existing_columns = [row[1] for row in result.fetchall()]
            
            logger.info(f"📝 Found {len(existing_columns)} existing columns")
            
            # Define all columns that should exist
            all_columns = [
                ("total_points", "ALTER TABLE users ADD COLUMN total_points INTEGER DEFAULT 0;"),
                ("question_points", "ALTER TABLE users ADD COLUMN question_points INTEGER DEFAULT 0;"),
                ("referral_points", "ALTER TABLE users ADD COLUMN referral_points INTEGER DEFAULT 0;"),
                ("jailbreak_multiplier_applied", "ALTER TABLE users ADD COLUMN jailbreak_multiplier_applied INTEGER DEFAULT 0;"),
                ("last_points_update", "ALTER TABLE users ADD COLUMN last_points_update TIMESTAMP;"),
                ("nft_verified", "ALTER TABLE users ADD COLUMN nft_verified BOOLEAN DEFAULT 0;"),
                ("nft_verified_at", "ALTER TABLE users ADD COLUMN nft_verified_at TIMESTAMP;"),
                ("nft_mint_address", "ALTER TABLE users ADD COLUMN nft_mint_address VARCHAR(255);"),
                ("full_name", "ALTER TABLE users ADD COLUMN full_name VARCHAR(255);"),
                ("date_of_birth", "ALTER TABLE users ADD COLUMN date_of_birth TIMESTAMP;"),
                ("phone_number", "ALTER TABLE users ADD COLUMN phone_number VARCHAR(50);"),
                ("address", "ALTER TABLE users ADD COLUMN address TEXT;"),
                ("kyc_status", "ALTER TABLE users ADD COLUMN kyc_status VARCHAR(50) DEFAULT 'pending';"),
                ("kyc_provider", "ALTER TABLE users ADD COLUMN kyc_provider VARCHAR(50);"),
                ("kyc_reference_id", "ALTER TABLE users ADD COLUMN kyc_reference_id VARCHAR(255);"),
            ]
            
            # Add missing columns
            added_count = 0
            for column_name, query in all_columns:
                if column_name not in existing_columns:
                    logger.info(f"  ➕ Adding column: {column_name}")
                    await session.execute(text(query))
                    added_count += 1
                else:
                    logger.info(f"  ✓ Column {column_name} already exists")
            
            await session.commit()
            
            logger.info(f"\n✅ Migration completed!")
            logger.info(f"   Added {added_count} new columns")
            logger.info(f"   Total columns: {len(existing_columns) + added_count}")
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            await session.rollback()
            raise


async def main():
    """Run migration"""
    
    try:
        await sync_user_table()
        
        logger.info("\n" + "="*50)
        logger.info("🎉 Users table synced successfully!")
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

