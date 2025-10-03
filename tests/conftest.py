"""
Test configuration and fixtures
"""
import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from src.database import Base
from src.models import User, EmailVerification, FreeQuestions, ReferralCode, Referral

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    await engine.dispose()

@pytest_asyncio.fixture
async def session(engine):
    """Create test database session"""
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def test_user(session: AsyncSession):
    """Create a test user"""
    user = User(
        session_id="test_session_123",
        email="test@example.com",
        password_hash="hashed_password",
        is_verified=True,
        wallet_address="test_wallet_123",
        display_name="Test User"
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
