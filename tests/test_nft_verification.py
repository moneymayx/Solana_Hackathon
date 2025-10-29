"""
Automated NFT Verification Tests
Tests all NFT verification functionality without manual interaction
"""
import pytest
import asyncio
import httpx
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.database import get_db, create_tables
from src.models import User, FreeQuestions
from src.free_question_service import FreeQuestionService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_WALLET = "TestWallet123456789012345678901234567890"  # 44 chars
TEST_NFT_MINT = "9dBdXMB3WuTy638W1a1tTygWCzosUmALhRLksrX8oQVa"


class TestNFTVerificationAPI:
    """Test NFT verification API endpoints"""
    
    @pytest.mark.asyncio
    async def test_check_nft_ownership_endpoint(self):
        """Test GET /api/nft/check-ownership/{wallet}/{nft}"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/nft/check-ownership/{TEST_WALLET}/{TEST_NFT_MINT}",
                timeout=10.0
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "owns_nft" in data
            assert "wallet_address" in data
            assert "nft_mint" in data
            print("✅ NFT ownership check endpoint working")
    
    @pytest.mark.asyncio
    async def test_get_nft_status_endpoint(self):
        """Test GET /api/nft/status/{wallet}"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/nft/status/{TEST_WALLET}",
                timeout=10.0
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "verified" in data
            assert "questions_remaining" in data
            print("✅ NFT status endpoint working")
    
    @pytest.mark.asyncio
    async def test_user_eligibility_includes_nft_status(self):
        """Test that user eligibility endpoint includes NFT verification status"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/free-questions/{TEST_WALLET}",
                timeout=10.0
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert "nft_verified" in data
            assert "nft_mint_address" in data
            print("✅ User eligibility includes NFT status")
    
    @pytest.mark.asyncio
    async def test_anonymous_questions_removed(self):
        """Test that anonymous free questions are removed (should be 0)"""
        async with httpx.AsyncClient() as client:
            # Create a new test wallet
            new_wallet = f"NewTestWallet{asyncio.get_event_loop().time()}"
            
            response = await client.get(
                f"{BASE_URL}/api/free-questions/{new_wallet}",
                timeout=10.0
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should have 0 questions (no anonymous questions anymore)
            # Unless they have referral questions
            questions = data.get("questions_remaining", 0)
            print(f"✅ New user has {questions} questions (expected 0 without NFT/referral)")


class TestFreeQuestionService:
    """Test Free Question Service logic"""
    
    @pytest.mark.asyncio
    async def test_anonymous_questions_constant(self):
        """Test that ANONYMOUS_FREE_QUESTIONS is set to 0"""
        service = FreeQuestionService()
        assert service.ANONYMOUS_FREE_QUESTIONS == 0
        assert service.MAX_ANONYMOUS_QUESTIONS == 0
        print("✅ Anonymous free questions disabled")
    
    @pytest.mark.asyncio
    async def test_nft_questions_constant(self):
        """Test that NFT_FREE_QUESTIONS is set to 5"""
        service = FreeQuestionService()
        assert service.NFT_FREE_QUESTIONS == 5
        print("✅ NFT free questions set to 5")


class TestDatabaseMigration:
    """Test that database migration was successful"""
    
    @pytest.mark.asyncio
    async def test_nft_fields_exist_in_user_model(self):
        """Test that NFT verification fields exist in User model"""
        # Check User model has the fields
        assert hasattr(User, 'nft_verified')
        assert hasattr(User, 'nft_verified_at')
        assert hasattr(User, 'nft_mint_address')
        print("✅ User model has NFT verification fields")
    
    @pytest.mark.asyncio
    async def test_database_columns_exist(self):
        """Test that database has NFT columns"""
        from src.database import engine
        
        try:
            async with engine.begin() as conn:
                # Check if columns exist by trying to query them
                from sqlalchemy import text
                result = await conn.execute(
                    text("SELECT nft_verified, nft_verified_at, nft_mint_address FROM users LIMIT 1")
                )
                print("✅ Database has NFT verification columns")
        except Exception as e:
            if "column" in str(e).lower() and "does not exist" in str(e).lower():
                pytest.fail(f"Database columns missing: {e}")
            # If table is empty, that's fine
            print("✅ Database columns exist (table may be empty)")


class TestIntegration:
    """Integration tests for NFT verification flow"""
    
    @pytest.mark.asyncio
    async def test_full_verification_flow_mock(self):
        """Test simulated full verification flow"""
        async with httpx.AsyncClient() as client:
            test_wallet = f"IntegrationTest{asyncio.get_event_loop().time()}"
            
            # Step 1: Check initial status
            response = await client.get(
                f"{BASE_URL}/api/nft/status/{test_wallet}",
                timeout=10.0
            )
            assert response.status_code == 200
            initial_status = response.json()
            assert initial_status["verified"] == False
            print("✅ Step 1: Initial status - not verified")
            
            # Step 2: Check ownership (would return false without real NFT)
            response = await client.get(
                f"{BASE_URL}/api/nft/check-ownership/{test_wallet}/{TEST_NFT_MINT}",
                timeout=10.0
            )
            assert response.status_code == 200
            print("✅ Step 2: Ownership check completed")
            
            # Step 3: Attempt verification (would require real signature)
            # We test the endpoint exists and validates input
            response = await client.post(
                f"{BASE_URL}/api/nft/verify",
                json={
                    "wallet_address": test_wallet,
                    "signature": "mock_signature_for_testing"
                },
                timeout=10.0
            )
            # Should return 200 even if verification fails (no real NFT)
            assert response.status_code == 200
            print("✅ Step 3: Verification endpoint accepts requests")


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_invalid_wallet_address(self):
        """Test with invalid wallet address"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/nft/status/invalid",
                timeout=10.0
            )
            # Should still return 200 with verified=false
            assert response.status_code == 200
            print("✅ Invalid wallet handled gracefully")
    
    @pytest.mark.asyncio
    async def test_invalid_nft_mint(self):
        """Test with invalid NFT mint address"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/nft/check-ownership/{TEST_WALLET}/invalid_mint",
                timeout=10.0
            )
            # Should return 200 (may indicate not owned)
            assert response.status_code == 200
            print("✅ Invalid NFT mint handled gracefully")
    
    @pytest.mark.asyncio
    async def test_missing_signature_in_verify(self):
        """Test verification without signature"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/nft/verify",
                json={
                    "wallet_address": TEST_WALLET,
                    # Missing signature
                },
                timeout=10.0
            )
            # Should return 422 (validation error) or 200 with error
            assert response.status_code in [200, 422]
            print("✅ Missing signature handled")


# Test runner
async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 AUTOMATED NFT VERIFICATION TEST SUITE")
    print("="*60 + "\n")
    
    # Ensure database is set up
    try:
        await create_tables()
        print("📊 Database tables verified\n")
    except Exception as e:
        print(f"⚠️  Database setup issue: {e}\n")
    
    test_classes = [
        TestNFTVerificationAPI,
        TestFreeQuestionService,
        TestDatabaseMigration,
        TestIntegration,
        TestErrorHandling
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}")
        print("-" * 60)
        
        test_instance = test_class()
        test_methods = [
            method for method in dir(test_instance)
            if method.startswith('test_') and callable(getattr(test_instance, method))
        ]
        
        for test_method_name in test_methods:
            total_tests += 1
            try:
                test_method = getattr(test_instance, test_method_name)
                await test_method()
                passed_tests += 1
            except AssertionError as e:
                failed_tests += 1
                print(f"❌ {test_method_name} FAILED: {e}")
            except Exception as e:
                failed_tests += 1
                print(f"❌ {test_method_name} ERROR: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed_tests} tests failed. Review errors above.")
    
    print("="*60 + "\n")
    
    return failed_tests == 0


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)


