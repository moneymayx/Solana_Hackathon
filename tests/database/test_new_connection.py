import asyncio
import os
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres.rkdhcyahecibdowyhzfk:mySupabase2026%21@aws-1-us-east-2.pooler.supabase.com:5432/postgres"

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test():
    engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"PostgreSQL: {version[:80]}")
            
            result = await conn.execute(text("SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector'"))
            has_vector = result.fetchone()[0] > 0
            print(f"{'✅' if has_vector else '❌'} pgvector: {'Installed' if has_vector else 'Not found'}")
        
        await engine.dispose()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

asyncio.run(test())
