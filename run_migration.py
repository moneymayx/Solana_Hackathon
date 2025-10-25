#!/usr/bin/env python3
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', '')

async def run_migration():
    print("Starting migration...")
    
    engine = create_async_engine(DATABASE_URL)
    
    with open('migrate_add_referral_fields.sql', 'r') as f:
        sql = f.read()
    
    async with engine.begin() as conn:
        for statement in sql.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    await conn.execute(statement)
                    print(f"✅ Executed: {statement[:60]}")
                except Exception as e:
                    if "already exists" not in str(e):
                        print(f"⚠️  Error: {e}")
                    else:
                        print(f"✅ Already exists: {statement[:60]}")
    
    await engine.dispose()
    print("\n✅ Migration completed!")

if __name__ == "__main__":
    asyncio.run(run_migration())
