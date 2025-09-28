#!/usr/bin/env python3
"""
Test database setup utilities
"""
import asyncio
import os
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.base import Base
from src.models import (
    User, Conversation, AttackAttempt, Transaction, PrizePool, SecurityEvent, 
    PaymentTransaction, BountyState, BountyEntry, BlacklistedPhrase, 
    Winner, ConnectedWallet, WalletFundingSource
)

# Test database URL - use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def create_test_tables():
    """Create all tables in the test database"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_test_tables():
    """Drop all tables in the test database"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def get_test_db():
    """Get a test database session"""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def setup_test_database():
    """Setup test database with initial data"""
    # Clear existing data first
    await drop_test_tables()
    await create_test_tables()
    
    # Create some initial test data
    async with TestSessionLocal() as session:
        # Create a test user
        test_user = User(
            session_id="test-session-123",
            ip_address="127.0.0.1",
            user_agent="test-agent",
            wallet_address="test-wallet-address-123",
            display_name="Test User"
        )
        session.add(test_user)
        
        # Create a test bounty state
        bounty_state = BountyState(
            current_jackpot_usd=1000.0,
            total_entries_this_period=0,
            is_active=True
        )
        session.add(bounty_state)
        
        # Create a test prize pool
        prize_pool = PrizePool(
            current_amount=1000.0,
            total_contributions=1000.0,
            total_queries=0,
            base_query_cost=10.0,
            escalation_rate=0.0078,
            max_query_cost=4500.0
        )
        session.add(prize_pool)
        
        await session.commit()

def run_test_database_setup():
    """Run the test database setup"""
    async def _setup():
        await setup_test_database()
        print("✅ Test database setup completed successfully!")
    
    asyncio.run(_setup())

if __name__ == "__main__":
    run_test_database_setup()
