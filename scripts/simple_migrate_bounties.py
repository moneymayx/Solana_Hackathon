#!/usr/bin/env python3
"""
Simple migration script to add Bounty table and update Conversation table
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up environment
os.environ.setdefault('DATABASE_URL', 'postgresql+asyncpg://postgres.rkdhcyahecibdowyhzfk:mySupabase2026%21@aws-1-us-east-2.pooler.supabase.com:5432/postgres')

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

async def migrate_add_bounties():
    """Add Bounty table and update Conversation table with new columns"""
    
    print("🚀 Starting migration: Add Bounties and update Conversations")
    
    # Database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres.rkdhcyahecibdowyhzfk:mySupabase2026%21@aws-1-us-east-2.pooler.supabase.com:5432/postgres')
    
    # Create async engine
    engine = create_async_engine(database_url)
    
    try:
        async with engine.begin() as conn:
            # Create the bounties table
            print("📋 Creating bounties table...")
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS bounties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    llm_provider VARCHAR(50) NOT NULL,
                    current_pool REAL DEFAULT 0.0,
                    total_entries INTEGER DEFAULT 0,
                    win_rate REAL DEFAULT 0.0,
                    difficulty_level VARCHAR(20) DEFAULT 'medium',
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Add new columns to conversations table (check if they exist first)
            print("📝 Adding bounty_id column to conversations...")
            try:
                await conn.execute(text("""
                    ALTER TABLE conversations 
                    ADD COLUMN bounty_id INTEGER REFERENCES bounties(id)
                """))
                print("  ✅ Added bounty_id column")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("  ⏭️  bounty_id column already exists")
                else:
                    raise
            
            print("📝 Adding is_public column to conversations...")
            try:
                await conn.execute(text("""
                    ALTER TABLE conversations 
                    ADD COLUMN is_public BOOLEAN DEFAULT 1
                """))
                print("  ✅ Added is_public column")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("  ⏭️  is_public column already exists")
                else:
                    raise
            
            print("📝 Adding is_winner column to conversations...")
            try:
                await conn.execute(text("""
                    ALTER TABLE conversations 
                    ADD COLUMN is_winner BOOLEAN DEFAULT 0
                """))
                print("  ✅ Added is_winner column")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("  ⏭️  is_winner column already exists")
                else:
                    raise
            
            # Create indexes for better performance
            print("🔍 Creating indexes...")
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_conversations_bounty_id 
                ON conversations(bounty_id)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_conversations_is_public 
                ON conversations(is_public)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_conversations_is_winner 
                ON conversations(is_winner)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_bounties_llm_provider 
                ON bounties(llm_provider)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_bounties_is_active 
                ON bounties(is_active)
            """))
            
        print("✅ Migration completed successfully!")
        
        # Seed initial bounties
        await seed_initial_bounties(engine)
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        await engine.dispose()

async def seed_initial_bounties(engine):
    """Seed the database with initial bounty challenges"""
    
    print("🌱 Seeding initial bounties...")
    
    initial_bounties = [
        {
            "name": "Claude Champ",
            "llm_provider": "claude",
            "current_pool": 1000.0,
            "total_entries": 0,
            "win_rate": 0.0,
            "difficulty_level": "medium",
            "is_active": True
        },
        {
            "name": "GPT-4 Bounty",
            "llm_provider": "gpt-4",
            "current_pool": 1500.0,
            "total_entries": 0,
            "win_rate": 0.0,
            "difficulty_level": "hard",
            "is_active": True
        },
        {
            "name": "Gemini Quest",
            "llm_provider": "gemini",
            "current_pool": 800.0,
            "total_entries": 0,
            "win_rate": 0.0,
            "difficulty_level": "easy",
            "is_active": True
        },
        {
            "name": "Llama Legend",
            "llm_provider": "llama",
            "current_pool": 2000.0,
            "total_entries": 0,
            "win_rate": 0.0,
            "difficulty_level": "expert",
            "is_active": True
        }
    ]
    
    try:
        async with engine.begin() as conn:
            for bounty_data in initial_bounties:
                # Check if bounty already exists
                result = await conn.execute(
                    text("SELECT id FROM bounties WHERE llm_provider = :provider"),
                    {"provider": bounty_data["llm_provider"]}
                )
                
                if not result.fetchone():
                    await conn.execute(text("""
                        INSERT INTO bounties (name, llm_provider, current_pool, total_entries, win_rate, difficulty_level, is_active)
                        VALUES (:name, :llm_provider, :current_pool, :total_entries, :win_rate, :difficulty_level, :is_active)
                    """), bounty_data)
                    print(f"  ✅ Added {bounty_data['name']}")
                else:
                    print(f"  ⏭️  {bounty_data['name']} already exists")
            
        print("🌱 Initial bounties seeded successfully!")
        
    except Exception as e:
        print(f"❌ Failed to seed bounties: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(migrate_add_bounties())
