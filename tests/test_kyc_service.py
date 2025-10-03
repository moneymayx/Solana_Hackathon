"""
Test KYC Service functionality
"""
import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from src.kyc_service import KYCService
from src.models import User, EmailVerification
from src.database import get_db

@pytest.fixture
def kyc_service():
    """Create KYC service instance"""
    return KYCService()

@pytest_asyncio.fixture
async def test_user(session: AsyncSession):
    """Create test user"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        session_id=f"test_session_{unique_id}",
        email=f"test_{unique_id}@example.com",
        wallet_address=f"test_wallet_{unique_id}",
        kyc_status="pending",
        is_verified=True
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@pytest.fixture
def sample_moonpay_webhook():
    """Sample MoonPay webhook data"""
    return {
        "data": {
            "id": "moonpay_tx_123",
            "status": "completed",
            "walletAddress": "test_wallet_123",
            "customer": {
                "id": "customer_123",
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "dateOfBirth": "1990-01-01",
                "phone": {
                    "number": "+1234567890"
                },
                "address": {
                    "addressLine1": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "postalCode": "10001",
                    "country": "US"
                }
            },
            "verificationLevel": "level_2",
            "complianceTier": "tier_1",
            "riskLevel": "low"
        }
    }

class TestKYCService:
    """Test KYC Service functionality"""
    
    @pytest.mark.asyncio
    async def test_extract_moonpay_kyc_data(self, kyc_service, sample_moonpay_webhook):
        """Test MoonPay KYC data extraction"""
        kyc_data = kyc_service._extract_moonpay_kyc_data(sample_moonpay_webhook)
        
        assert kyc_data["full_name"] == "John Doe"
        assert kyc_data["date_of_birth"] == datetime(1990, 1, 1)
        assert kyc_data["phone_number"] == "+1234567890"
        assert kyc_data["address"] == "123 Main St, New York, NY, 10001, US"
        assert kyc_data["kyc_status"] == "verified"
        assert kyc_data["kyc_provider"] == "moonpay"
        assert kyc_data["kyc_reference_id"] == "moonpay_tx_123"
    
    def test_map_moonpay_status(self, kyc_service):
        """Test MoonPay status mapping"""
        assert kyc_service._map_moonpay_status("completed") == "verified"
        assert kyc_service._map_moonpay_status("pending") == "pending"
        assert kyc_service._map_moonpay_status("failed") == "rejected"
        assert kyc_service._map_moonpay_status("expired") == "expired"
        assert kyc_service._map_moonpay_status("cancelled") == "rejected"
        assert kyc_service._map_moonpay_status("unknown") == "pending"
    
    def test_parse_date(self, kyc_service):
        """Test date parsing functionality"""
        # Valid dates
        assert kyc_service._parse_date("1990-01-01") == datetime(1990, 1, 1)
        assert kyc_service._parse_date("1990-01-01T12:00:00") == datetime(1990, 1, 1, 12, 0, 0)
        assert kyc_service._parse_date("1990-01-01T12:00:00Z") == datetime(1990, 1, 1, 12, 0, 0)
        
        # Invalid dates
        assert kyc_service._parse_date("invalid") is None
        assert kyc_service._parse_date(None) is None
        assert kyc_service._parse_date("") is None
    
    def test_format_address(self, kyc_service):
        """Test address formatting"""
        address_data = {
            "addressLine1": "123 Main St",
            "addressLine2": "Apt 4B",
            "city": "New York",
            "state": "NY",
            "postalCode": "10001",
            "country": "US"
        }
        
        formatted = kyc_service._format_address(address_data)
        expected = "123 Main St, Apt 4B, New York, NY, 10001, US"
        assert formatted == expected
        
        # Test with missing fields
        partial_address = {
            "addressLine1": "123 Main St",
            "city": "New York",
            "country": "US"
        }
        
        formatted = kyc_service._format_address(partial_address)
        expected = "123 Main St, New York, US"
        assert formatted == expected
    
    @pytest.mark.asyncio
    async def test_process_moonpay_kyc_data(self, kyc_service, session: AsyncSession, test_user, sample_moonpay_webhook):
        """Test complete MoonPay KYC data processing"""
        # Update webhook to use test user's wallet address
        sample_moonpay_webhook["data"]["walletAddress"] = test_user.wallet_address
        
        result = await kyc_service.process_moonpay_kyc_data(session, sample_moonpay_webhook)
        
        assert result["success"] is True
        assert result["user_id"] == test_user.id
        assert result["kyc_status"] == "verified"
        
        # Verify user was updated
        updated_user = await session.get(User, test_user.id)
        assert updated_user.full_name == "John Doe"
        assert updated_user.kyc_status == "verified"
        assert updated_user.kyc_provider == "moonpay"
        assert updated_user.kyc_reference_id == "moonpay_tx_123"
    
    @pytest.mark.asyncio
    async def test_get_kyc_status(self, kyc_service, session: AsyncSession, test_user):
        """Test getting user KYC status"""
        result = await kyc_service.get_kyc_status(session, test_user.id)
        
        assert result["success"] is True
        assert result["kyc_status"] == "pending"
        assert result["kyc_provider"] is None
    
    @pytest.mark.asyncio
    async def test_get_kyc_statistics(self, kyc_service, session: AsyncSession, test_user):
        """Test KYC statistics generation"""
        stats = await kyc_service.get_kyc_statistics(session)
        
        assert "total_users" in stats
        assert "kyc_status_breakdown" in stats
        assert "provider_breakdown" in stats
        assert "verification_rate" in stats
        
        assert stats["total_users"] >= 1
        assert stats["kyc_status_breakdown"]["pending"] >= 1
    
    @pytest.mark.asyncio
    async def test_get_pending_kyc_reviews(self, kyc_service, session: AsyncSession, test_user):
        """Test getting pending KYC reviews"""
        pending = await kyc_service.get_pending_kyc_reviews(session, limit=10)
        
        assert isinstance(pending, list)
        if pending:  # If there are pending users
            user = pending[0]
            assert "user_id" in user
            assert "email" in user
            assert "kyc_status" in user
            assert user["kyc_status"] in ["pending", "under_review"]
    
    @pytest.mark.asyncio
    async def test_update_kyc_status(self, kyc_service, session: AsyncSession, test_user):
        """Test updating KYC status"""
        result = await kyc_service.update_kyc_status(
            session, test_user.id, "verified", "Test verification"
        )
        
        assert result["success"] is True
        assert result["user_id"] == test_user.id
        assert result["new_status"] == "verified"
        
        # Verify user was updated
        updated_user = await session.get(User, test_user.id)
        assert updated_user.kyc_status == "verified"
    
    @pytest.mark.asyncio
    async def test_update_kyc_status_invalid(self, kyc_service, session: AsyncSession, test_user):
        """Test updating KYC status with invalid status"""
        result = await kyc_service.update_kyc_status(
            session, test_user.id, "invalid_status", "Test"
        )
        
        assert result["success"] is False
        assert "Invalid KYC status" in result["error"]

if __name__ == "__main__":
    pytest.main([__file__])
