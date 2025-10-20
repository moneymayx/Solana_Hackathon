"""
Create a test user in PostgreSQL database
"""
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
project_root = Path(__file__).parent
load_dotenv(dotenv_path=project_root / ".env")

from src.database import engine
from sqlalchemy import text


async def create_user():
    db_url = os.getenv("DATABASE_URL", "not found")
    print(f"🔍 Database: {db_url.split('@')[1][:60] if '@' in db_url else db_url[:60]}...\n")
    
    async with engine.begin() as conn:
        # Check if user exists
        result = await conn.execute(text("SELECT COUNT(*) FROM users WHERE id = 1"))
        count = result.scalar()
        
        if count > 0:
            print("✅ User with ID 1 already exists!")
            result = await conn.execute(text("SELECT id, email, display_name FROM users WHERE id = 1"))
            user = result.fetchone()
            print(f"   • ID: {user[0]}")
            print(f"   • Email: {user[1]}")
            print(f"   • Display Name: {user[2]}")
        else:
            print("📝 Creating test user in PostgreSQL...")
            
            await conn.execute(text("""
                INSERT INTO users (
                    session_id, email, display_name, is_verified,
                    created_at, last_active, total_attempts, total_cost,
                    is_active, anonymous_free_questions_used,
                    has_used_anonymous_questions, kyc_status
                )
                VALUES (
                    'api-test-session-001', 'apiuser@example.com', 'API Test User', true,
                    NOW(), NOW(), 0, 0.0, true, 0, false, 'pending'
                )
            """))
            
            print("✅ User created successfully!")
            
            result = await conn.execute(text("SELECT id, email, display_name FROM users WHERE email = 'apiuser@example.com'"))
            user = result.fetchone()
            print(f"   • ID: {user[0]}")
            print(f"   • Email: {user[1]}")
            print(f"   • Display Name: {user[2]}")
        
        print("\n💡 Use this user_id when creating teams: 1")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_user())

