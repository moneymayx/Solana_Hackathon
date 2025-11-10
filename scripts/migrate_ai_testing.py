#!/usr/bin/env python3
"""
Migration script to add AI testing tables for the AI vs AI resistance testing system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def migrate_add_ai_testing():
    """Add AI testing tables for resistance testing system"""
    
    print("🚀 Starting migration: Add AI Testing Tables")
    
    # Database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return
    
    # Detect database type
    is_postgres = 'postgresql' in database_url.lower()
    
    # Create async engine
    engine = create_async_engine(database_url)
    
    try:
        async with engine.begin() as conn:
            # Create the ai_test_runs table
            print("📋 Creating ai_test_runs table...")
            if is_postgres:
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ai_test_runs (
                        id SERIAL PRIMARY KEY,
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        completed_at TIMESTAMP,
                        status VARCHAR(50) DEFAULT 'running',
                        error_message TEXT,
                        total_tests INTEGER DEFAULT 0,
                        successful_jailbreaks INTEGER DEFAULT 0,
                        failed_jailbreaks INTEGER DEFAULT 0,
                        test_config JSONB,
                        summary_report TEXT
                    )
                """))
            else:
                # SQLite syntax
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ai_test_runs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        completed_at TIMESTAMP,
                        status VARCHAR(50) DEFAULT 'running',
                        error_message TEXT,
                        total_tests INTEGER DEFAULT 0,
                        successful_jailbreaks INTEGER DEFAULT 0,
                        failed_jailbreaks INTEGER DEFAULT 0,
                        test_config TEXT,
                        summary_report TEXT
                    )
                """))
            print("  ✅ Created ai_test_runs table")
            
            # Create the ai_test_results table
            print("📋 Creating ai_test_results table...")
            if is_postgres:
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ai_test_results (
                        id SERIAL PRIMARY KEY,
                        test_run_id INTEGER REFERENCES ai_test_runs(id) ON DELETE CASCADE,
                        attacker_llm VARCHAR(50) NOT NULL,
                        target_llm VARCHAR(50) NOT NULL,
                        target_difficulty VARCHAR(20) NOT NULL,
                        question_count INTEGER NOT NULL,
                        was_successful BOOLEAN DEFAULT FALSE,
                        duration_seconds REAL DEFAULT 0.0,
                        conversation_json JSONB NOT NULL,
                        attacker_system_prompt TEXT,
                        target_response_preview TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                    )
                """))
            else:
                # SQLite syntax
                await conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ai_test_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        test_run_id INTEGER REFERENCES ai_test_runs(id) ON DELETE CASCADE,
                        attacker_llm VARCHAR(50) NOT NULL,
                        target_llm VARCHAR(50) NOT NULL,
                        target_difficulty VARCHAR(20) NOT NULL,
                        question_count INTEGER NOT NULL,
                        was_successful BOOLEAN DEFAULT FALSE,
                        duration_seconds REAL DEFAULT 0.0,
                        conversation_json TEXT NOT NULL,
                        attacker_system_prompt TEXT,
                        target_response_preview TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                    )
                """))
            print("  ✅ Created ai_test_results table")
            
            # Create indexes for better performance
            print("🔍 Creating indexes...")
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ai_test_runs_started_at 
                ON ai_test_runs(started_at)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ai_test_runs_status 
                ON ai_test_runs(status)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ai_test_results_test_run_id 
                ON ai_test_results(test_run_id)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ai_test_results_attacker_llm 
                ON ai_test_results(attacker_llm)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ai_test_results_target_llm 
                ON ai_test_results(target_llm)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ai_test_results_target_difficulty 
                ON ai_test_results(target_difficulty)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ai_test_results_was_successful 
                ON ai_test_results(was_successful)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_ai_test_results_created_at 
                ON ai_test_results(created_at)
            """))
            
            print("  ✅ Created indexes")
            
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate_add_ai_testing())

