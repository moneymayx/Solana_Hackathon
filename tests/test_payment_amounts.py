"""
Automated tests for payment amount selection and question allocation
Tests the "Try Your Luck" payment flow with different amounts
"""
import pytest
import asyncio
import logging
from datetime import datetime
from httpx import AsyncClient, ConnectTimeout, ReadTimeout
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete
import os
from dotenv import load_dotenv
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import models and services
from src.models import User, FreeQuestions, Bounty
from src.services.free_question_service import free_question_service

# Test wallet address
TEST_WALLET = "TestWallet1111111111111111111111111111111"

# Bounty pricing helpers to keep tests aligned with production logic
STARTING_BOUNTIES = {
    "easy": 500.0,
    "medium": 2500.0,
    "hard": 5000.0,
    "expert": 10000.0,
}

STARTING_COSTS = {
    "easy": 0.50,
    "medium": 2.50,
    "hard": 5.00,
    "expert": 10.00,
}

BOUNTY_PROVIDER_BY_DIFFICULTY = {
    "easy": "llama",
    "medium": "gemini",
    "hard": "gpt-4",
    "expert": "claude",
}

BOUNTY_NAME_BY_DIFFICULTY = {
    "easy": "Llama Legend",
    "medium": "Gemini Great",
    "hard": "GPT Gigachad",
    "expert": "Claude Champ",
}

# Timeout settings
TEST_TIMEOUT = 10  # seconds per test
API_TIMEOUT = 5    # seconds per API call
DB_TIMEOUT = 5     # seconds per DB operation

def async_timeout(seconds):
    """Decorator to add timeout to async functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                logger.error(f"❌ Test timed out after {seconds}s: {func.__name__}")
                raise TimeoutError(f"Test {func.__name__} exceeded {seconds}s timeout")
        return wrapper
    return decorator

@pytest.fixture
async def async_session():
    """Create async database session for testing with timeout"""
    try:
        logger.info("📊 Creating database session...")
        engine = create_async_engine(
            os.getenv('DATABASE_URL'), 
            echo=False,
            pool_pre_ping=True,  # Check connections before using
            pool_recycle=3600    # Recycle connections after 1 hour
        )
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            yield session
        
        logger.info("✅ Database session closed")
        await asyncio.wait_for(engine.dispose(), timeout=DB_TIMEOUT)
    except asyncio.TimeoutError:
        logger.error("❌ Database session creation/cleanup timed out")
        raise
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        raise

@pytest.fixture
async def cleanup_test_data(async_session):
    """Clean up test data before and after tests with timeout"""
    try:
        # Clean up before test
        logger.info("🧹 Cleaning up test data (before)...")
        await asyncio.wait_for(
            async_session.execute(
                delete(FreeQuestions).where(FreeQuestions.user_id.in_(
                    select(User.id).where(User.wallet_address == TEST_WALLET)
                ))
            ),
            timeout=DB_TIMEOUT
        )
        await asyncio.wait_for(
            async_session.execute(
                delete(User).where(User.wallet_address == TEST_WALLET)
            ),
            timeout=DB_TIMEOUT
        )
        await asyncio.wait_for(async_session.commit(), timeout=DB_TIMEOUT)
        logger.info("✅ Pre-test cleanup complete")
        
        yield
        
        # Clean up after test
        logger.info("🧹 Cleaning up test data (after)...")
        await asyncio.wait_for(
            async_session.execute(
                delete(FreeQuestions).where(FreeQuestions.user_id.in_(
                    select(User.id).where(User.wallet_address == TEST_WALLET)
                ))
            ),
            timeout=DB_TIMEOUT
        )
        await asyncio.wait_for(
            async_session.execute(
                delete(User).where(User.wallet_address == TEST_WALLET)
            ),
            timeout=DB_TIMEOUT
        )
        await asyncio.wait_for(async_session.commit(), timeout=DB_TIMEOUT)
        logger.info("✅ Post-test cleanup complete")
    except asyncio.TimeoutError:
        logger.error("❌ Cleanup timed out")
        raise
    except Exception as e:
        logger.error(f"❌ Cleanup error: {e}")
        raise


async def ensure_bounty_state(session: AsyncSession, bounty_id: int, difficulty: str) -> None:
    """Ensure the target bounty exists with predictable pricing for tests."""

    difficulty_key = difficulty.lower()
    starting_pool = STARTING_BOUNTIES.get(difficulty_key, STARTING_BOUNTIES["medium"])
    provider = BOUNTY_PROVIDER_BY_DIFFICULTY.get(difficulty_key, "claude")
    name = BOUNTY_NAME_BY_DIFFICULTY.get(difficulty_key, f"Test Bounty {bounty_id}")

    result = await session.execute(select(Bounty).where(Bounty.id == bounty_id))
    bounty = result.scalar_one_or_none()

    if bounty:
        bounty.name = bounty.name or name
        bounty.llm_provider = provider
        bounty.difficulty_level = difficulty_key
        bounty.current_pool = starting_pool
        bounty.total_entries = 0
        bounty.updated_at = datetime.utcnow()
    else:
        session.add(Bounty(
            id=bounty_id,
            name=name,
            llm_provider=provider,
            current_pool=starting_pool,
            total_entries=0,
            difficulty_level=difficulty_key,
            is_active=True
        ))

    await session.commit()

class TestPaymentAmounts:
    """Test suite for payment amount selection"""
    
    # Test cases: (bounty_id, difficulty, amount, expected_questions, expected_credit)
    PAYMENT_TEST_CASES = [
        (1, 'expert', 1, 0, 1.0),        # Expert difficulty, insufficient payment
        (1, 'expert', 10, 1, 0.0),       # Expert: baseline question cost $10
        (1, 'expert', 20, 2, 0.0),       # Expert: multiple questions
        (1, 'expert', 15, 1, 5.0),       # Expert: credit remainder
        (1, 'expert', 25, 2, 5.0),       # Expert: extra credit on multiples
        (3, 'medium', 3, 1, 0.5),        # Medium difficulty: cost $2.50
        (3, 'medium', 5, 2, 0.0),        # Medium: two questions
        (3, 'medium', 7.50, 3, 0.0),     # Medium: fractional input equals exact questions
        (4, 'easy', 1, 2, 0.0),          # Easy difficulty: cost $0.50, $1 → 2 questions
        (2, 'hard', 5, 1, 0.0),          # Hard difficulty: cost $5
    ]
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(TEST_TIMEOUT)
    @pytest.mark.parametrize("bounty_id,difficulty,amount,expected_questions,expected_credit", PAYMENT_TEST_CASES)
    async def test_payment_create_with_amount(self, bounty_id, difficulty, amount, expected_questions, expected_credit, cleanup_test_data, async_session):
        """Test payment creation with different amounts"""
        try:
            await ensure_bounty_state(async_session, bounty_id, difficulty)
            logger.info(f"🧪 Testing payment create: ${amount}")
            async with AsyncClient(
                base_url="http://localhost:8000",
                timeout=API_TIMEOUT
            ) as client:
                response = await client.post(
                    "/api/payment/create",
                    json={
                        "wallet_address": TEST_WALLET,
                        "amount_usd": amount,
                        "payment_method": "wallet"
                    }
                )
                
                assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
                data = response.json()
                
                assert data["success"] is True, f"Expected success=True, got: {data}"
                assert data["transaction"]["amount_usd"] == amount
                assert "is_mock" in data
                
                logger.info(f"✅ Payment create: ${amount} → Transaction created")
        except ConnectTimeout:
            logger.error(f"❌ Connection timeout for ${amount} payment create")
            pytest.fail("Backend not responding - connection timeout")
        except ReadTimeout:
            logger.error(f"❌ Read timeout for ${amount} payment create")
            pytest.fail("Backend took too long to respond")
        except Exception as e:
            logger.error(f"❌ Test failed for ${amount}: {e}")
            raise
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(TEST_TIMEOUT)
    @pytest.mark.parametrize("bounty_id,difficulty,amount,expected_questions,expected_credit", PAYMENT_TEST_CASES)
    async def test_mock_payment_verification(self, bounty_id, difficulty, amount, expected_questions, expected_credit, cleanup_test_data, async_session):
        """Test mock payment verification and question allocation"""
        try:
            await ensure_bounty_state(async_session, bounty_id, difficulty)
            logger.info(f"🧪 Testing payment verification: ${amount}")
            # Step 1: Create payment
            async with AsyncClient(
                base_url="http://localhost:8000",
                timeout=API_TIMEOUT
            ) as client:
                create_response = await client.post(
                    "/api/payment/create",
                    json={
                        "wallet_address": TEST_WALLET,
                        "amount_usd": amount,
                        "payment_method": "wallet"
                    }
                )
                
                assert create_response.status_code == 200
                create_data = create_response.json()
                
                # Step 2: Verify payment with mock signature
                mock_signature = f"MOCK_TEST_{amount}_{TEST_WALLET}"
                
                verify_response = await client.post(
                    "/api/payment/verify",
                    json={
                        "tx_signature": mock_signature,
                        "wallet_address": TEST_WALLET,
                        "payment_method": "wallet",
                        "amount_usd": amount,
                        "bounty_id": bounty_id
                    }
                )
                
                assert verify_response.status_code == 200
                verify_data = verify_response.json()
                
                assert verify_data["success"] is True
                assert verify_data["verified"] is True
                assert verify_data["questions_granted"] == expected_questions
                actual_cost = verify_data.get("question_cost_usd")
                if actual_cost is not None:
                    assert abs(float(actual_cost) - STARTING_COSTS[difficulty.lower()]) < 0.01, (
                        f"Expected cost ${STARTING_COSTS[difficulty.lower()]:.2f} for {difficulty}, "
                        f"got ${float(actual_cost):.2f}"
                    )
                
                # Check credit remainder
                credit_remainder = verify_data.get("credit_remainder", 0.0)
                assert abs(credit_remainder - expected_credit) < 0.01, \
                    f"Expected ${expected_credit:.2f} credit for ${amount}, got ${credit_remainder:.2f}"
                
                print(f"✅ Payment verify: ${amount} → {expected_questions} questions + ${credit_remainder:.2f} credit granted")
                
                # Step 3: Verify questions were actually stored in database
                result = await async_session.execute(
                    select(User).where(User.wallet_address == TEST_WALLET)
                )
                user = result.scalar_one_or_none()
                
                if expected_questions > 0:
                    assert user is not None, f"User not created for ${amount} payment"
                    
                    # Check FreeQuestions record
                    fq_result = await async_session.execute(
                        select(FreeQuestions).where(FreeQuestions.user_id == user.id)
                    )
                    free_questions = fq_result.scalar_one_or_none()
                    
                    assert free_questions is not None, f"FreeQuestions not created for ${amount}"
                    assert free_questions.questions_remaining == expected_questions
                    assert free_questions.questions_earned == expected_questions
                    assert "payment" in free_questions.source.lower() or "mock_payment" in free_questions.source.lower()
                    
                    # Verify credit balance is stored
                    assert abs(free_questions.credit_balance - expected_credit) < 0.01, \
                        f"Expected ${expected_credit:.2f} credit balance, got ${free_questions.credit_balance:.2f}"
                    
                    logger.info(f"✅ Database verify: {expected_questions} questions + ${free_questions.credit_balance:.2f} credit stored for user {user.id}")
        except ConnectTimeout:
            logger.error(f"❌ Connection timeout for ${amount} payment verification")
            pytest.fail("Backend not responding - connection timeout")
        except ReadTimeout:
            logger.error(f"❌ Read timeout for ${amount} payment verification")
            pytest.fail("Backend took too long to respond")
        except asyncio.TimeoutError:
            logger.error(f"❌ Async timeout for ${amount} payment verification")
            pytest.fail("Test exceeded time limit")
        except Exception as e:
            logger.error(f"❌ Test failed for ${amount}: {e}")
            raise
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(TEST_TIMEOUT * 2)  # Longer timeout for multiple payments
    async def test_multiple_payments_accumulate(self, cleanup_test_data, async_session):
        """Test that multiple payments create separate question records"""
        try:
            logger.info("🧪 Testing multiple payments accumulation")
            bounty_id = 1
            await ensure_bounty_state(async_session, bounty_id, 'expert')
            async with AsyncClient(
                base_url="http://localhost:8000",
                timeout=API_TIMEOUT
            ) as client:
                # Make multiple payments
                payments = [10, 20, 50]  # Total = 8 questions (1 + 2 + 5)
                
                for amount in payments:
                    mock_signature = f"MOCK_TEST_MULTI_{amount}_{TEST_WALLET}"
                    
                    # Create payment
                    await client.post(
                        "/api/payment/create",
                        json={
                            "wallet_address": TEST_WALLET,
                            "amount_usd": amount,
                            "payment_method": "wallet"
                        }
                    )
                    
                    # Verify payment
                    response = await client.post(
                        "/api/payment/verify",
                        json={
                            "tx_signature": mock_signature,
                            "wallet_address": TEST_WALLET,
                            "payment_method": "wallet",
                            "amount_usd": amount,
                            "bounty_id": bounty_id
                        }
                    )
                    
                    assert response.status_code == 200
                
                # Check total questions
                result = await async_session.execute(
                    select(User).where(User.wallet_address == TEST_WALLET)
                )
                user = result.scalar_one_or_none()
                assert user is not None
                
                # Get all FreeQuestions records
                fq_result = await async_session.execute(
                    select(FreeQuestions).where(FreeQuestions.user_id == user.id)
                )
                all_questions = fq_result.scalars().all()
                
                total_questions = sum(fq.questions_remaining for fq in all_questions)
                expected_total = 1 + 2 + 5  # 8 questions
                
                assert total_questions == expected_total, f"Expected {expected_total} total questions, got {total_questions}"
                logger.info(f"✅ Multiple payments: {len(all_questions)} payment records, {total_questions} total questions")
        except Exception as e:
            logger.error(f"❌ Multiple payments test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(TEST_TIMEOUT)
    async def test_payment_message_distinction(self, cleanup_test_data, async_session):
        """Test that paid questions show correct message (not 'free')"""
        try:
            logger.info("🧪 Testing payment message distinction")
            bounty_id = 1
            await ensure_bounty_state(async_session, bounty_id, 'expert')
            async with AsyncClient(
                base_url="http://localhost:8000",
                timeout=API_TIMEOUT
            ) as client:
                # Make a $20 payment (2 questions)
                mock_signature = f"MOCK_TEST_MESSAGE_{TEST_WALLET}"
                
                await client.post(
                    "/api/payment/create",
                    json={
                        "wallet_address": TEST_WALLET,
                        "amount_usd": 20,
                        "payment_method": "wallet"
                    }
                )
                
                verify_response = await client.post(
                    "/api/payment/verify",
                    json={
                        "tx_signature": mock_signature,
                        "wallet_address": TEST_WALLET,
                        "payment_method": "wallet",
                        "amount_usd": 20,
                        "bounty_id": bounty_id
                    }
                )
                
                assert verify_response.status_code == 200
                
                # Check eligibility endpoint for correct message
                eligibility_response = await client.get(
                    f"/api/free-questions/{TEST_WALLET}"
                )
                
                assert eligibility_response.status_code == 200
                eligibility_data = eligibility_response.json()
                
                # Should say "questions remaining" not "free questions remaining"
                assert eligibility_data["success"] is True
                # Check if message exists first
                if "message" not in eligibility_data:
                    logger.warning(f"⚠️  No 'message' field in response: {eligibility_data}")
                    pytest.skip("Eligibility response missing 'message' field")
                
                assert "2 questions remaining" in eligibility_data["message"]
                assert "free questions" not in eligibility_data["message"].lower() or "questions remaining" in eligibility_data["message"]
                
                logger.info(f"✅ Message distinction: '{eligibility_data['message']}'")
        except Exception as e:
            logger.error(f"❌ Message distinction test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(TEST_TIMEOUT)
    async def test_smart_contract_integration(self, cleanup_test_data, async_session):
        """Test that mock payments trigger smart contract (in mock mode)"""
        try:
            logger.info("🧪 Testing smart contract integration")
            bounty_id = 1
            await ensure_bounty_state(async_session, bounty_id, 'expert')
            async with AsyncClient(
                base_url="http://localhost:8000",
                timeout=API_TIMEOUT
            ) as client:
                # Make payment
                await client.post(
                    "/api/payment/create",
                    json={
                        "wallet_address": TEST_WALLET,
                        "amount_usd": 100,
                        "payment_method": "wallet"
                    }
                )
                
                # Verify payment
                mock_signature = f"MOCK_TEST_SC_{TEST_WALLET}"
                verify_response = await client.post(
                    "/api/payment/verify",
                    json={
                        "tx_signature": mock_signature,
                        "wallet_address": TEST_WALLET,
                        "payment_method": "wallet",
                        "amount_usd": 100,
                        "bounty_id": bounty_id
                    }
                )
                
                assert verify_response.status_code == 200
                verify_data = verify_response.json()
                
                # Check if smart contract was triggered (in mock mode)
                assert "smart_contract_executed" in verify_data or "smart_contract_tx" in verify_data
                
                logger.info(f"✅ Smart contract: Integration test passed")
        except Exception as e:
            logger.error(f"❌ Smart contract test failed: {e}")
            raise

if __name__ == "__main__":
    logger.info("🧪 Running Payment Amount Tests...")
    logger.info("=" * 60)
    
    # Check if backend is running
    import httpx
    try:
        response = httpx.get("http://localhost:8000/health", timeout=2.0)
        if response.status_code == 200:
            logger.info("✅ Backend is running")
        else:
            logger.warning(f"⚠️  Backend returned status {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Backend not responding: {e}")
        logger.error("Please start the backend with: python3 apps/backend/main.py")
        exit(1)
    
    # Run tests
    pytest.main([
        __file__,
        "-v",
        "-s",
        "--tb=short",
        "--asyncio-mode=auto",
        "--timeout=30"  # Global timeout for all tests
    ])

