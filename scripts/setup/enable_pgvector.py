#!/usr/bin/env python3
"""
Enable pgvector extension in Supabase PostgreSQL
"""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

load_dotenv()

async def enable_pgvector():
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env file!")
        return False
    
    print("🔧 Enabling pgvector extension in PostgreSQL...")
    
    try:
        engine = create_async_engine(database_url, echo=False)
        
        async with engine.begin() as conn:
            # Enable pgvector extension
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            print("✅ pgvector extension enabled successfully!")
            
            # Verify it's installed
            result = await conn.execute(text("SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector'"))
            has_vector = result.fetchone()[0] > 0
            
            if has_vector:
                print("✅ Verification passed: pgvector is active")
            else:
                print("⚠️  Verification failed: pgvector not found after installation")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Failed to enable pgvector!")
        print(f"Error: {e}")
        print("\n💡 Try manually in Supabase SQL Editor:")
        print("   CREATE EXTENSION IF NOT EXISTS vector;")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("  Enable pgvector Extension")
    print("=" * 70)
    print()
    
    success = asyncio.run(enable_pgvector())
    
    print()
    print("=" * 70)
    if success:
        print("  🎉 pgvector is ready to use!")
    else:
        print("  ⚠️  Manual intervention may be required")
    print("=" * 70)

