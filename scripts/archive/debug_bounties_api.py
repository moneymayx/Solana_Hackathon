#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, '/Users/jaybrantley/myenv/Hackathon/Billions_Bounty')

from src.database import AsyncSessionLocal
from src.repositories import BountyRepository

async def debug_bounties():
    print("🔍 Debugging bounties API...")
    
    try:
        # Get database session
        async with AsyncSessionLocal() as session:
            print(f"✅ Database session created: {session}")
            
            # Test direct database query
            from sqlalchemy import text
            result = await session.execute(text("SELECT COUNT(*) FROM bounties"))
            count = result.scalar()
            print(f"🔍 Direct SQL count: {count}")
            
            # Create repository
            bounty_repo = BountyRepository(session)
            print(f"✅ BountyRepository created: {bounty_repo}")
            
            # Test repository method
            bounties = await bounty_repo.get_all_bounties()
            print(f"🔍 Repository returned {len(bounties)} bounties")
            
            for bounty in bounties:
                print(f"  - {bounty.name} ({bounty.llm_provider}): ${bounty.current_pool}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_bounties())
