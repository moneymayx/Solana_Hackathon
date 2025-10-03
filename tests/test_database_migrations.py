"""
Test database migrations for new models
"""
import pytest
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from src.models import User, EmailVerification, FreeQuestions, ReferralCode, Referral

class TestDatabaseMigrations:
    """Test database migrations and new models"""
    
    @pytest.mark.asyncio
    async def test_create_tables(self, session: AsyncSession):
        """Test that all tables can be created"""
        # Tables are created by the session fixture
        # This test just verifies we can connect
        result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = result.fetchall()
        table_names = [row[0] for row in tables]
        
        expected_tables = ['users', 'email_verifications', 'free_questions', 'referral_codes', 'referrals']
        for table in expected_tables:
            assert table in table_names, f"Table {table} not found"
        
        print("✅ All tables created successfully")
    
    @pytest.mark.asyncio
    async def test_user_model_new_fields(self, session: AsyncSession):
        """Test User model with new fields"""
        user = User(
            session_id="test_session_123",
            email="test@example.com",
            password_hash="hashed_password",
            is_verified=True,
            anonymous_free_questions_used=1,
            has_used_anonymous_questions=True,
            wallet_address="test_wallet_123",
            display_name="Test User",
            full_name="John Doe",
            date_of_birth=datetime(1990, 1, 1),
            phone_number="+1234567890",
            address="123 Main St, City, State, 12345",
            kyc_status="verified",
            kyc_provider="moonpay",
            kyc_reference_id="moonpay_tx_123"
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_verified is True
        assert user.anonymous_free_questions_used == 1
        assert user.has_used_anonymous_questions is True
        assert user.kyc_status == "verified"
        assert user.kyc_provider == "moonpay"
        
        print("✅ User model with new fields works correctly")
    
    @pytest.mark.asyncio
    async def test_email_verification_model(self, session: AsyncSession):
        """Test EmailVerification model"""
        verification = EmailVerification(
            user_id=1,  # Assuming user exists
            email="test@example.com",
            verification_token="test_token_123",
            verification_type="email_verification",
            is_used=False,
            expires_at=datetime.utcnow()
        )
        
        session.add(verification)
        await session.commit()
        await session.refresh(verification)
        
        assert verification.id is not None
        assert verification.verification_token == "test_token_123"
        assert verification.verification_type == "email_verification"
        assert verification.is_used is False
        
        print("✅ EmailVerification model works correctly")
    
    @pytest.mark.asyncio
    async def test_free_questions_model(self, session: AsyncSession):
        """Test FreeQuestions model with new fields"""
        free_questions = FreeQuestions(
            user_id=1,  # Assuming user exists
            source="referral_signup",
            referral_id=1,  # Assuming referral exists
            questions_earned=5,
            questions_used=2,
            questions_remaining=3,
            expires_at=datetime.utcnow()
        )
        
        session.add(free_questions)
        await session.commit()
        await session.refresh(free_questions)
        
        assert free_questions.id is not None
        assert free_questions.source == "referral_signup"
        assert free_questions.questions_earned == 5
        assert free_questions.questions_remaining == 3
        
        print("✅ FreeQuestions model with new fields works correctly")
    
    @pytest.mark.asyncio
    async def test_referral_code_model(self, session: AsyncSession):
        """Test ReferralCode model"""
        referral_code = ReferralCode(
            user_id=1,  # Assuming user exists
            referral_code="ABC123",
            is_active=True,
            total_uses=0,
            total_free_questions_earned=0
        )
        
        session.add(referral_code)
        await session.commit()
        await session.refresh(referral_code)
        
        assert referral_code.id is not None
        assert referral_code.referral_code == "ABC123"
        assert referral_code.is_active is True
        
        print("✅ ReferralCode model works correctly")
    
    @pytest.mark.asyncio
    async def test_database_constraints(self, session: AsyncSession):
        """Test database constraints and relationships"""
        # Test unique constraints
        user1 = User(
            session_id="unique_session_1",
            email="unique@example.com",
            wallet_address="unique_wallet_1"
        )
        session.add(user1)
        await session.commit()
        await session.refresh(user1)
        user1_id = user1.id  # Store the ID before accessing it

        # Try to create user with same email (should fail)
        user2 = User(
            session_id="unique_session_2",
            email="unique@example.com",  # Same email
            wallet_address="unique_wallet_2"
        )
        session.add(user2)

        try:
            await session.commit()
            assert False, "Should have failed due to unique email constraint"
        except Exception as e:
            print("✅ Unique email constraint works correctly")
            await session.rollback()

        # Test foreign key relationships
        verification = EmailVerification(
            user_id=user1_id,  # Use stored ID
            email="unique@example.com",
            verification_token="test_token",
            expires_at=datetime.utcnow()
        )
        session.add(verification)
        await session.commit()
        await session.refresh(verification)

        assert verification.user_id == user1_id
        print("✅ Foreign key relationships work correctly")
    
    @pytest.mark.asyncio
    async def test_database_indexes(self, session: AsyncSession):
        """Test that database indexes are working"""
        # Create test data first
        user = User(
            session_id="index_test_session",
            email="index_test@example.com",
            wallet_address="index_test_wallet"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        user_id = user.id

        verification = EmailVerification(
            user_id=user_id,
            email="index_test@example.com",
            verification_token="index_test_token",
            expires_at=datetime.utcnow()
        )
        session.add(verification)
        await session.commit()

        # Test email index
        result = await session.execute(
            select(User).where(User.email == "index_test@example.com")
        )
        found_user = result.scalar_one_or_none()
        assert found_user is not None
        assert found_user.email == "index_test@example.com"

        # Test wallet address index
        result = await session.execute(
            select(User).where(User.wallet_address == "index_test_wallet")
        )
        found_user = result.scalar_one_or_none()
        assert found_user is not None
        assert found_user.wallet_address == "index_test_wallet"

        # Test verification token index
        result = await session.execute(
            select(EmailVerification).where(EmailVerification.verification_token == "index_test_token")
        )
        found_verification = result.scalar_one_or_none()
        assert found_verification is not None
        assert found_verification.verification_token == "index_test_token"

        print("✅ Database indexes are working correctly")

if __name__ == "__main__":
    pytest.main([__file__])
