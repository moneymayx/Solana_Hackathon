#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to PostgreSQL
Run this after setting up your PostgreSQL database on DigitalOcean
"""
import asyncio
import sqlite3
import sys
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.models import Base, User
from src.database import create_tables

# Load environment variables
load_dotenv(os.path.join(project_root, '.env'))

# Configuration
SQLITE_DB_PATH = os.path.join(project_root, 'billions.db')
POSTGRES_URL = os.getenv('DATABASE_URL')

if not POSTGRES_URL:
    print("❌ Error: DATABASE_URL not set in .env file")
    print("Please add your PostgreSQL connection string:")
    print("DATABASE_URL=postgresql+asyncpg://user:password@host:25060/billions_bounty?sslmode=require")
    sys.exit(1)

print(f"🔍 Source SQLite DB: {SQLITE_DB_PATH}")
print(f"🎯 Target PostgreSQL: {POSTGRES_URL[:50]}...")


async def migrate_data():
    """Migrate all data from SQLite to PostgreSQL"""
    
    # Step 1: Check if SQLite database exists
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"⚠️  Warning: SQLite database not found at {SQLITE_DB_PATH}")
        print("Creating fresh PostgreSQL database...")
        
        # Create PostgreSQL tables
        engine = create_async_engine(POSTGRES_URL, echo=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ PostgreSQL database initialized (no data to migrate)")
        return
    
    # Step 2: Connect to SQLite and read data
    print("\n📖 Reading data from SQLite...")
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]
    
    print(f"Found tables: {', '.join(tables)}")
    
    # Read all data
    table_data = {}
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        table_data[table] = [dict(row) for row in rows]
        print(f"  - {table}: {len(rows)} rows")
    
    sqlite_conn.close()
    
    # Step 3: Create PostgreSQL tables
    print("\n🏗️  Creating PostgreSQL tables...")
    engine = create_async_engine(POSTGRES_URL, echo=False)
    
    async with engine.begin() as conn:
        # Drop all tables first (clean slate)
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Tables created")
    
    # Step 4: Insert data into PostgreSQL
    print("\n📝 Inserting data into PostgreSQL...")
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        for table_name, rows in table_data.items():
            if not rows:
                continue
            
            print(f"\n  Migrating {table_name}...")
            
            # Build insert statements
            for row in rows:
                # Convert any datetime strings if needed
                # Build column names and placeholders
                columns = list(row.keys())
                placeholders = [f":{col}" for col in columns]
                
                insert_sql = f"""
                    INSERT INTO {table_name} ({', '.join(columns)})
                    VALUES ({', '.join(placeholders)})
                """
                
                try:
                    await session.execute(text(insert_sql), row)
                except Exception as e:
                    print(f"    ⚠️  Warning: Could not insert row: {e}")
                    continue
            
            await session.commit()
            print(f"    ✅ Migrated {len(rows)} rows")
    
    await engine.dispose()
    
    print("\n✅ Migration complete!")
    print(f"📊 Summary:")
    for table_name, rows in table_data.items():
        print(f"  - {table_name}: {len(rows)} rows")


async def verify_migration():
    """Verify the migration by checking row counts"""
    print("\n🔍 Verifying migration...")
    
    engine = create_async_engine(POSTGRES_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Check some key tables
        for table in ['users', 'conversations', 'prize_pools', 'referrals']:
            try:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  ✅ {table}: {count} rows")
            except Exception as e:
                print(f"  ⚠️  {table}: Table may not exist or error: {e}")
    
    await engine.dispose()


async def main():
    """Main migration function"""
    print("=" * 60)
    print("🚀 SQLite to PostgreSQL Migration")
    print("=" * 60)
    
    try:
        await migrate_data()
        await verify_migration()
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION SUCCESSFUL!")
        print("=" * 60)
        print("\n📝 Next steps:")
        print("1. Update your .env to use PostgreSQL (DATABASE_URL)")
        print("2. Test your backend locally with: uvicorn apps.backend.main:app --reload")
        print("3. Deploy to DigitalOcean App Platform")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

