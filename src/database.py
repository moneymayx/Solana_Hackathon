"""
Database configuration and connection management for Billions
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .base import Base

# Import all models to ensure they're registered with SQLAlchemy
from .models import (
    User, Conversation, AttackAttempt, Transaction, PrizePool, SecurityEvent, 
    PaymentTransaction, BountyState, BountyEntry, BlacklistedPhrase, 
    Winner, ConnectedWallet, WalletFundingSource, EmailVerification,
    ReferralCode, FundDeposit, FundTransfer, Referral, FreeQuestions,
    # Phase 2: Token Economics ($100Bs)
    TokenBalance, StakingPosition, BuybackEvent, TokenPrice, DiscountUsage,
    # Phase 1: Context Window Management
    MessageEmbedding, AttackPattern, ContextSummary,
    # Phase 3: Team Collaboration
    Team, TeamMember, TeamInvitation, TeamAttempt, TeamMessage, TeamFunding,
    TeamPrizeDistribution, TeamMemberPrize
)

# Import simulation models
from .config.simulation_models import (
    SimulationRun, SimulationConversation, SimulationMessage, 
    SuccessfulAttempt, SimulationPattern, SimulationAlert, SimulationReport
)

# Database URL - defaults to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./billions.db")

# Log which database we're connecting to
import logging
logger = logging.getLogger(__name__)
logger.info(f"🗄️  DATABASE_URL: {DATABASE_URL[:80]}...")

# Create async engine with connection pool settings
engine = create_async_engine(
    DATABASE_URL,
    echo=True if os.getenv("DEBUG") == "true" else False,
    future=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,  # Number of connections to maintain
    max_overflow=20,  # Max additional connections
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """Create all tables in the database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    """Drop all tables in the database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
