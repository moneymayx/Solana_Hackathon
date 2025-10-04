#!/usr/bin/env python3
"""
Simple test to verify database connection works
"""
import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

async def test_db_connection():
    """Test database connection and table creation"""
    try:
        print("🔍 Testing database connection...")
        
        # Import database modules
        from src.database import create_tables, AsyncSessionLocal
        from src.models import User
        
        print("✅ Database modules imported successfully")
        
        # Test table creation
        await create_tables()
        print("✅ Database tables created successfully")
        
        # Test session creation
        async with AsyncSessionLocal() as session:
            print("✅ Database session created successfully")
            
            # Test a simple query
            from sqlalchemy import select
            result = await session.execute(select(User).limit(1))
            users = result.scalars().all()
            print(f"✅ Database query successful - found {len(users)} users")
        
        print("🎉 Database connection test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_db_connection())
    if not success:
        sys.exit(1)
