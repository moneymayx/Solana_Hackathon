#!/usr/bin/env python3
"""
Quick test script to verify PostgreSQL connection
"""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

load_dotenv()

async def test_connection():
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env file!")
        return False
    
    print(f"🔍 Testing connection to: {database_url[:50]}...")
    
    try:
        engine = create_async_engine(database_url, echo=False)
        
        async with engine.begin() as conn:
            # Test basic query
            result = await conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"\n✅ Connection successful!")
            print(f"PostgreSQL version: {version[:80]}...")
            
            # Test pgvector extension
            result = await conn.execute(text("SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector'"))
            has_vector = result.fetchone()[0] > 0
            
            if has_vector:
                print(f"✅ pgvector extension is installed")
            else:
                print(f"⚠️  pgvector extension NOT found")
                print(f"   Run in Supabase SQL Editor: CREATE EXTENSION vector;")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed!")
        print(f"Error: {e}")
        print(f"\nCommon issues:")
        print(f"  1. Check password has no brackets: [YOUR_PASSWORD] → actual_password")
        print(f"  2. URL needs +asyncpg: postgresql:// → postgresql+asyncpg://")
        print(f"  3. Special characters need URL encoding (@ → %40, # → %23)")
        print(f"  4. Check your Supabase project is running")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("  PostgreSQL Connection Test")
    print("=" * 70)
    print()
    
    success = asyncio.run(test_connection())
    
    print()
    print("=" * 70)
    if success:
        print("  🎉 All good! Ready to proceed with Phase 1")
    else:
        print("  ⚠️  Fix the connection issues above and try again")
    print("=" * 70)

