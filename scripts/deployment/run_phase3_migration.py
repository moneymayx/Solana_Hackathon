"""
Phase 3 Migration: Team Collaboration Tables

This script creates the database tables for Phase 3 team collaboration features:
- teams
- team_members
- team_invitations
- team_attempts
- team_messages
- team_funding
- team_prize_distributions
- team_member_prizes
"""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment variables
load_dotenv()

# Import database setup
from src.database import engine
from src.base import Base

# Import Phase 3 models to ensure they're registered
from src.models import (
    Team, TeamMember, TeamInvitation, TeamAttempt, TeamMessage, TeamFunding,
    TeamPrizeDistribution, TeamMemberPrize
)


async def create_phase3_tables():
    """Create Phase 3 team collaboration tables"""
    
    print("=" * 60)
    print("PHASE 3 MIGRATION: Team Collaboration Tables")
    print("=" * 60)
    print()
    
    # Verify DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        return
    
    print(f"✅ Database URL: {database_url.split('@')[1] if '@' in database_url else 'Not found'}")
    print()
    
    try:
        # Create all tables
        print("📊 Creating Phase 3 tables...")
        async with engine.begin() as conn:
            # Create tables (only creates if they don't exist)
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Phase 3 tables created successfully!")
        print()
        
        # Verify tables were created
        print("🔍 Verifying Phase 3 tables...")
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename IN (
                    'teams',
                    'team_members',
                    'team_invitations',
                    'team_attempts',
                    'team_messages',
                    'team_funding',
                    'team_prize_distributions',
                    'team_member_prizes'
                )
                ORDER BY tablename
            """))
            tables = result.fetchall()
            
            print("✅ Phase 3 Tables Created:")
            for table in tables:
                print(f"   • {table[0]}")
            print()
            
            if len(tables) == 8:
                print("✅ All Phase 3 tables created successfully!")
            else:
                print(f"⚠️  Expected 8 tables, found {len(tables)}")
        
        print()
        print("=" * 60)
        print("PHASE 3 MIGRATION COMPLETE! 🎉")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Implement TeamService (src/team_service.py)")
        print("2. Create Team API endpoints")
        print("3. Build frontend team UI")
        print()
        
    except Exception as e:
        print(f"❌ Error creating Phase 3 tables: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_phase3_tables())

