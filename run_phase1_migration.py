#!/usr/bin/env python3
"""
Phase 1 Migration Script
Creates all database tables including Phase 1 Context Window Management tables
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.base import Base

# Import all models to register them with SQLAlchemy
from src.models import (
    User, Conversation, AttackAttempt, Transaction, PrizePool, SecurityEvent,
    PaymentTransaction, BountyState, BountyEntry, BlacklistedPhrase,
    Winner, ConnectedWallet, WalletFundingSource, EmailVerification,
    ReferralCode, FundDeposit, FundTransfer, Referral, FreeQuestions,
    # Phase 1: Context Window Management
    MessageEmbedding, AttackPattern, ContextSummary
)

from src.simulation_models import (
    SimulationRun, SimulationConversation, SimulationMessage,
    SuccessfulAttempt, SimulationPattern, SimulationAlert, SimulationReport
)

async def run_migration():
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in .env")
        return False
    
    print("=" * 70)
    print("  PHASE 1 DATABASE MIGRATION")
    print("=" * 70)
    print()
    print(f"🔧 Database: {DATABASE_URL[:50]}...")
    print()
    
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        print("📦 Creating all tables (this may take a minute)...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Tables created successfully!")
        print()
        
        # Verify Phase 1 tables exist
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename IN ('message_embeddings', 'attack_patterns', 'context_summaries')
                ORDER BY tablename
            """))
            phase1_tables = result.fetchall()
            
            print("📊 Phase 1 Tables:")
            if phase1_tables:
                for table in phase1_tables:
                    print(f"   ✅ {table[0]}")
            else:
                print("   ⚠️  No Phase 1 tables found")
            
            print()
            
            # Get count of all public tables
            result = await conn.execute(text("""
                SELECT COUNT(*) 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            table_count = result.scalar()
            
            print(f"📋 Total tables in database: {table_count}")
            
            # Verify pgvector extension
            result = await conn.execute(text("""
                SELECT COUNT(*) 
                FROM pg_extension 
                WHERE extname = 'vector'
            """))
            has_vector = result.scalar() > 0
            
            print(f"🔌 pgvector extension: {'✅ Installed' if has_vector else '❌ Not found'}")
        
        await engine.dispose()
        
        print()
        print("=" * 70)
        print("  🎉 MIGRATION COMPLETE!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        await engine.dispose()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_migration())
    exit(0 if success else 1)

