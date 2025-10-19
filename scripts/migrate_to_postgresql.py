#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Script
=====================================

Migrates all data from SQLite (billions.db) to PostgreSQL.
Safe migration with verification and rollback capability.

Usage:
    python3 scripts/migrate_to_postgresql.py
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from src.base import Base
from src.models import (
    User, Conversation, AttackAttempt, Transaction, PrizePool, SecurityEvent,
    PaymentTransaction, BountyState, BountyEntry, BlacklistedPhrase,
    Winner, ConnectedWallet, WalletFundingSource, EmailVerification,
    ReferralCode, FundDeposit, FundTransfer, Referral, FreeQuestions
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseMigrator:
    """Handles migration from SQLite to PostgreSQL"""
    
    def __init__(self):
        self.sqlite_url = "sqlite+aiosqlite:///./billions.db"
        self.postgres_url = os.getenv("DATABASE_URL")
        
        if not self.postgres_url:
            raise ValueError("DATABASE_URL not set in .env file!")
        
        if "sqlite" in self.postgres_url.lower():
            raise ValueError("DATABASE_URL still points to SQLite! Update to PostgreSQL URL.")
        
        print(f"🔄 Migration Configuration:")
        print(f"  Source: {self.sqlite_url}")
        print(f"  Target: {self.postgres_url[:50]}...")
        print()
    
    async def verify_postgres_connection(self):
        """Verify PostgreSQL connection and pgvector extension"""
        print("🔍 Verifying PostgreSQL connection...")
        
        try:
            engine = create_async_engine(self.postgres_url)
            async with engine.begin() as conn:
                # Test connection
                result = await conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"  ✅ PostgreSQL connected: {version[:50]}...")
                
                # Check pgvector extension
                result = await conn.execute(text("SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector'"))
                has_pgvector = result.fetchone()[0] > 0
                
                if has_pgvector:
                    print(f"  ✅ pgvector extension installed")
                else:
                    print(f"  ⚠️  pgvector extension NOT installed")
                    print(f"  Run: CREATE EXTENSION vector;")
                    return False
            
            await engine.dispose()
            return True
            
        except Exception as e:
            print(f"  ❌ PostgreSQL connection failed: {e}")
            return False
    
    async def check_sqlite_data(self):
        """Check what data exists in SQLite"""
        print("\n📊 Analyzing SQLite database...")
        
        try:
            engine = create_async_engine(self.sqlite_url)
            async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            
            async with async_session() as session:
                counts = {}
                models = [
                    User, Conversation, AttackAttempt, Transaction, PrizePool,
                    SecurityEvent, PaymentTransaction, BountyState, BountyEntry,
                    BlacklistedPhrase, Winner, ConnectedWallet, WalletFundingSource,
                    EmailVerification, ReferralCode, FundDeposit, FundTransfer,
                    Referral, FreeQuestions
                ]
                
                for model in models:
                    try:
                        result = await session.execute(select(model))
                        count = len(result.scalars().all())
                        counts[model.__tablename__] = count
                        if count > 0:
                            print(f"  {model.__tablename__}: {count} records")
                    except Exception as e:
                        print(f"  {model.__tablename__}: Error - {e}")
                        counts[model.__tablename__] = 0
            
            await engine.dispose()
            
            total_records = sum(counts.values())
            print(f"\n  📈 Total records to migrate: {total_records}")
            
            return counts
            
        except Exception as e:
            print(f"  ❌ Failed to read SQLite: {e}")
            return {}
    
    async def create_postgres_schema(self):
        """Create all tables in PostgreSQL"""
        print("\n🏗️  Creating PostgreSQL schema...")
        
        try:
            engine = create_async_engine(self.postgres_url)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            await engine.dispose()
            
            print(f"  ✅ Schema created successfully")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to create schema: {e}")
            return False
    
    async def migrate_table(self, model_class, sqlite_session, postgres_session):
        """Migrate a single table"""
        table_name = model_class.__tablename__
        
        try:
            # Read from SQLite
            result = await sqlite_session.execute(select(model_class))
            records = result.scalars().all()
            
            if not records:
                return 0
            
            # Write to PostgreSQL
            migrated = 0
            for record in records:
                # Create new instance with all attributes
                new_record = model_class()
                for column in model_class.__table__.columns:
                    if hasattr(record, column.name):
                        setattr(new_record, column.name, getattr(record, column.name))
                
                postgres_session.add(new_record)
                migrated += 1
            
            await postgres_session.commit()
            return migrated
            
        except Exception as e:
            await postgres_session.rollback()
            print(f"    ❌ Error: {e}")
            raise
    
    async def migrate_all_data(self):
        """Migrate all data from SQLite to PostgreSQL"""
        print("\n🚀 Starting data migration...")
        
        sqlite_engine = create_async_engine(self.sqlite_url)
        postgres_engine = create_async_engine(self.postgres_url)
        
        sqlite_session_maker = async_sessionmaker(sqlite_engine, class_=AsyncSession, expire_on_commit=False)
        postgres_session_maker = async_sessionmaker(postgres_engine, class_=AsyncSession, expire_on_commit=False)
        
        async with sqlite_session_maker() as sqlite_session, postgres_session_maker() as postgres_session:
            # Order matters due to foreign keys
            models_to_migrate = [
                User,
                PrizePool,
                BountyState,
                Conversation,
                AttackAttempt,
                Transaction,
                BountyEntry,
                SecurityEvent,
                PaymentTransaction,
                BlacklistedPhrase,
                Winner,
                ConnectedWallet,
                WalletFundingSource,
                EmailVerification,
                ReferralCode,
                FundDeposit,
                FundTransfer,
                Referral,
                FreeQuestions
            ]
            
            migration_results = {}
            
            for model in models_to_migrate:
                table_name = model.__tablename__
                try:
                    print(f"\n  📦 Migrating {table_name}...", end=" ")
                    count = await self.migrate_table(model, sqlite_session, postgres_session)
                    migration_results[table_name] = {"status": "success", "count": count}
                    print(f"✅ {count} records")
                except Exception as e:
                    migration_results[table_name] = {"status": "failed", "error": str(e)}
                    print(f"❌ Failed: {e}")
        
        await sqlite_engine.dispose()
        await postgres_engine.dispose()
        
        return migration_results
    
    async def verify_migration(self, original_counts):
        """Verify data was migrated correctly"""
        print("\n🔍 Verifying migration...")
        
        engine = create_async_engine(self.postgres_url)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            all_match = True
            
            for table_name, original_count in original_counts.items():
                # Find corresponding model
                model = None
                for m in [User, Conversation, AttackAttempt, Transaction, PrizePool,
                         SecurityEvent, PaymentTransaction, BountyState, BountyEntry,
                         BlacklistedPhrase, Winner, ConnectedWallet, WalletFundingSource,
                         EmailVerification, ReferralCode, FundDeposit, FundTransfer,
                         Referral, FreeQuestions]:
                    if m.__tablename__ == table_name:
                        model = m
                        break
                
                if not model:
                    continue
                
                result = await session.execute(select(model))
                new_count = len(result.scalars().all())
                
                if new_count == original_count:
                    if original_count > 0:
                        print(f"  ✅ {table_name}: {new_count} records")
                else:
                    print(f"  ❌ {table_name}: Expected {original_count}, got {new_count}")
                    all_match = False
        
        await engine.dispose()
        
        if all_match:
            print(f"\n  🎉 All data verified successfully!")
        else:
            print(f"\n  ⚠️  Some data counts don't match!")
        
        return all_match
    
    async def run_migration(self):
        """Execute full migration process"""
        print("=" * 70)
        print("  SQLite → PostgreSQL Migration")
        print("  Billions Bounty Platform")
        print("=" * 70)
        print()
        
        # Step 1: Verify PostgreSQL connection
        if not await self.verify_postgres_connection():
            print("\n❌ Migration aborted: PostgreSQL verification failed")
            return False
        
        # Step 2: Check SQLite data
        original_counts = await self.check_sqlite_data()
        if not original_counts:
            print("\n❌ Migration aborted: Could not read SQLite database")
            return False
        
        # Ask for confirmation
        print("\n" + "=" * 70)
        print("⚠️  Ready to migrate. This will:")
        print("  1. Create all tables in PostgreSQL")
        print("  2. Copy all data from SQLite")
        print("  3. Verify data integrity")
        print()
        print("  Your SQLite database will NOT be modified.")
        print("=" * 70)
        
        response = input("\n  Proceed with migration? [y/N]: ")
        if response.lower() != 'y':
            print("\n  Migration cancelled by user.")
            return False
        
        # Step 3: Create schema
        if not await self.create_postgres_schema():
            print("\n❌ Migration aborted: Schema creation failed")
            return False
        
        # Step 4: Migrate data
        migration_results = await self.migrate_all_data()
        
        # Step 5: Verify migration
        verification_passed = await self.verify_migration(original_counts)
        
        # Summary
        print("\n" + "=" * 70)
        print("  MIGRATION SUMMARY")
        print("=" * 70)
        
        success_count = sum(1 for r in migration_results.values() if r["status"] == "success")
        failed_count = sum(1 for r in migration_results.values() if r["status"] == "failed")
        
        print(f"\n  ✅ Successful migrations: {success_count}")
        print(f"  ❌ Failed migrations: {failed_count}")
        print(f"  🔍 Verification: {'PASSED' if verification_passed else 'FAILED'}")
        
        if failed_count > 0:
            print("\n  Failed tables:")
            for table, result in migration_results.items():
                if result["status"] == "failed":
                    print(f"    - {table}: {result['error']}")
        
        if verification_passed and failed_count == 0:
            print("\n  🎉 Migration completed successfully!")
            print("\n  Next steps:")
            print("  1. Update DATABASE_URL in .env to use PostgreSQL")
            print("  2. Test your application")
            print("  3. Keep SQLite backup for safety")
            print("=" * 70)
            return True
        else:
            print("\n  ⚠️  Migration completed with issues!")
            print("  Review errors above and retry if needed.")
            print("=" * 70)
            return False


async def main():
    """Main migration entry point"""
    migrator = DatabaseMigrator()
    
    try:
        success = await migrator.run_migration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n  ⚠️  Migration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n  ❌ Migration failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())


