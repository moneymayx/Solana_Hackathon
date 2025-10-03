"""
Test Admin Dashboard API endpoints
"""
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from src.models import User, EmailVerification, FreeQuestions

# Create test client
client = TestClient(app)

@pytest_asyncio.fixture
async def admin_user(session: AsyncSession):
    """Create an admin test user"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        session_id=f"admin_session_{unique_id}",
        email=f"admin_{unique_id}@example.com",
        wallet_address=f"admin_wallet_{unique_id}",
        kyc_status="verified",
        is_verified=True,
        display_name="Admin User"
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@pytest_asyncio.fixture
async def test_users(session: AsyncSession):
    """Create multiple test users for admin testing"""
    import uuid
    users = []
    for i in range(5):
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            session_id=f"test_session_{unique_id}",
            email=f"user_{i}_{unique_id}@example.com",
            wallet_address=f"test_wallet_{unique_id}",
            kyc_status="pending" if i % 2 == 0 else "verified",
            is_verified=i % 2 == 1,
            display_name=f"Test User {i}"
        )
        session.add(user)
        users.append(user)
    
    await session.commit()
    for user in users:
        await session.refresh(user)
    return users

class TestAdminAPI:
    """Test Admin Dashboard API endpoints"""
    
    def test_kyc_statistics_endpoint(self):
        """Test GET /api/admin/kyc/statistics"""
        response = client.get("/api/admin/kyc/statistics")
        
        if response.status_code != 200:
            print(f"❌ Error response: {response.status_code}")
            print(f"Response text: {response.text}")
            try:
                error_data = response.json()
                print(f"Error JSON: {error_data}")
            except:
                pass
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "statistics" in data
        assert "total_users" in data["statistics"]
        assert "kyc_status_breakdown" in data["statistics"]
        assert "provider_breakdown" in data["statistics"]
        assert "verification_rate" in data["statistics"]
        
        print("✅ KYC Statistics endpoint working")
    
    def test_pending_kyc_reviews_endpoint(self):
        """Test GET /api/admin/kyc/pending"""
        response = client.get("/api/admin/kyc/pending")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "pending_users" in data
        assert "count" in data
        assert isinstance(data["pending_users"], list)
        
        print("✅ Pending KYC Reviews endpoint working")
    
    def test_pending_kyc_reviews_with_limit(self):
        """Test GET /api/admin/kyc/pending with limit parameter"""
        response = client.get("/api/admin/kyc/pending?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["pending_users"]) <= 10
        
        print("✅ Pending KYC Reviews with limit working")
    
    def test_user_kyc_status_endpoint(self, admin_user):
        """Test GET /api/admin/kyc/user/{user_id}"""
        response = client.get(f"/api/admin/kyc/user/{admin_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "kyc_status" in data
        assert "kyc_provider" in data
        assert "is_verified" in data
        
        print("✅ User KYC Status endpoint working")
    
    def test_user_kyc_status_not_found(self):
        """Test GET /api/admin/kyc/user/{user_id} with non-existent user"""
        response = client.get("/api/admin/kyc/user/99999")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "error" in data
        
        print("✅ User KYC Status not found handling working")
    
    def test_update_kyc_status_endpoint(self, admin_user):
        """Test POST /api/admin/kyc/update"""
        update_data = {
            "user_id": admin_user.id,
            "new_status": "verified",
            "admin_notes": "Test verification by admin"
        }
        
        response = client.post("/api/admin/kyc/update", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["user_id"] == admin_user.id
        assert data["new_status"] == "verified"
        
        print("✅ Update KYC Status endpoint working")
    
    def test_update_kyc_status_invalid(self, admin_user):
        """Test POST /api/admin/kyc/update with invalid status"""
        update_data = {
            "user_id": admin_user.id,
            "new_status": "invalid_status",
            "admin_notes": "Test invalid status"
        }
        
        response = client.post("/api/admin/kyc/update", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "Invalid KYC status" in data["error"]
        
        print("✅ Update KYC Status validation working")
    
    def test_get_all_users_endpoint(self):
        """Test GET /api/admin/users"""
        response = client.get("/api/admin/users")
        
        if response.status_code != 200:
            print(f"❌ Error response: {response.status_code}")
            print(f"Response text: {response.text}")
            try:
                error_data = response.json()
                print(f"Error JSON: {error_data}")
            except:
                pass
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "users" in data
        assert "count" in data
        assert isinstance(data["users"], list)
        
        print("✅ Get All Users endpoint working")
    
    def test_get_all_users_with_pagination(self):
        """Test GET /api/admin/users with pagination"""
        response = client.get("/api/admin/users?limit=5&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert len(data["users"]) <= 5
        assert data["offset"] == 0
        assert data["limit"] == 5
        
        print("✅ Get All Users pagination working")
    
    def test_get_all_users_with_kyc_filter(self):
        """Test GET /api/admin/users with KYC status filter"""
        response = client.get("/api/admin/users?kyc_status=verified")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        # All returned users should have verified status
        for user in data["users"]:
            assert user["kyc_status"] == "verified"
        
        print("✅ Get All Users KYC filter working")
    
    def test_compliance_report_endpoint(self):
        """Test GET /api/admin/compliance/report"""
        response = client.get("/api/admin/compliance/report")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "compliance_report" in data
        
        report = data["compliance_report"]
        assert "report_date" in report
        assert "total_users" in report
        assert "kyc_verification_rate" in report
        assert "kyc_status_breakdown" in report
        assert "provider_breakdown" in report
        assert "recent_verifications" in report
        assert "compliance_metrics" in report
        
        print("✅ Compliance Report endpoint working")
    
    def test_compliance_report_structure(self):
        """Test compliance report data structure"""
        response = client.get("/api/admin/compliance/report")
        data = response.json()
        report = data["compliance_report"]
        
        # Test compliance metrics structure
        metrics = report["compliance_metrics"]
        assert "verified_users" in metrics
        assert "pending_reviews" in metrics
        assert "rejected_users" in metrics
        assert "moonpay_verifications" in metrics
        
        # Test that all values are numbers
        assert isinstance(metrics["verified_users"], int)
        assert isinstance(metrics["pending_reviews"], int)
        assert isinstance(metrics["rejected_users"], int)
        assert isinstance(metrics["moonpay_verifications"], int)
        
        print("✅ Compliance Report structure validation working")

if __name__ == "__main__":
    pytest.main([__file__])
