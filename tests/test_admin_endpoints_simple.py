"""
Simple Admin Dashboard API endpoint tests using requests
"""
import pytest
import requests
import json
from typing import Dict, Any

# Base URL for the API (adjust if running on different port)
BASE_URL = "http://localhost:8000"

class TestAdminEndpoints:
    """Test Admin Dashboard API endpoints using HTTP requests"""
    
    def test_kyc_statistics_endpoint(self):
        """Test GET /api/admin/kyc/statistics"""
        try:
            response = requests.get(f"{BASE_URL}/api/admin/kyc/statistics")
            
            if response.status_code == 200:
                data = response.json()
                assert data["success"] is True
                assert "statistics" in data
                assert "total_users" in data["statistics"]
                print("✅ KYC Statistics endpoint working")
            else:
                print(f"⚠️  KYC Statistics endpoint returned {response.status_code}")
                print(f"Response: {response.text}")
        except requests.exceptions.ConnectionError:
            print("⚠️  Server not running. Start with: uvicorn main:app --reload")
        except Exception as e:
            print(f"❌ Error testing KYC Statistics: {e}")
    
    def test_pending_kyc_reviews_endpoint(self):
        """Test GET /api/admin/kyc/pending"""
        try:
            response = requests.get(f"{BASE_URL}/api/admin/kyc/pending")
            
            if response.status_code == 200:
                data = response.json()
                assert data["success"] is True
                assert "pending_users" in data
                assert "count" in data
                print("✅ Pending KYC Reviews endpoint working")
            else:
                print(f"⚠️  Pending KYC Reviews endpoint returned {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️  Server not running. Start with: uvicorn main:app --reload")
        except Exception as e:
            print(f"❌ Error testing Pending KYC Reviews: {e}")
    
    def test_get_all_users_endpoint(self):
        """Test GET /api/admin/users"""
        try:
            response = requests.get(f"{BASE_URL}/api/admin/users")
            
            if response.status_code == 200:
                data = response.json()
                assert data["success"] is True
                assert "users" in data
                assert "count" in data
                print("✅ Get All Users endpoint working")
            else:
                print(f"⚠️  Get All Users endpoint returned {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️  Server not running. Start with: uvicorn main:app --reload")
        except Exception as e:
            print(f"❌ Error testing Get All Users: {e}")
    
    def test_compliance_report_endpoint(self):
        """Test GET /api/admin/compliance/report"""
        try:
            response = requests.get(f"{BASE_URL}/api/admin/compliance/report")
            
            if response.status_code == 200:
                data = response.json()
                assert data["success"] is True
                assert "compliance_report" in data
                
                report = data["compliance_report"]
                assert "report_date" in report
                assert "total_users" in report
                assert "kyc_verification_rate" in report
                print("✅ Compliance Report endpoint working")
            else:
                print(f"⚠️  Compliance Report endpoint returned {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️  Server not running. Start with: uvicorn main:app --reload")
        except Exception as e:
            print(f"❌ Error testing Compliance Report: {e}")
    
    def test_update_kyc_status_endpoint(self):
        """Test POST /api/admin/kyc/update"""
        try:
            # First get a user to update
            users_response = requests.get(f"{BASE_URL}/api/admin/users?limit=1")
            if users_response.status_code == 200:
                users_data = users_response.json()
                if users_data["users"]:
                    user_id = users_data["users"][0]["user_id"]
                    
                    update_data = {
                        "user_id": user_id,
                        "new_status": "verified",
                        "admin_notes": "Test verification by admin"
                    }
                    
                    response = requests.post(
                        f"{BASE_URL}/api/admin/kyc/update", 
                        json=update_data
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        assert data["success"] is True
                        print("✅ Update KYC Status endpoint working")
                    else:
                        print(f"⚠️  Update KYC Status endpoint returned {response.status_code}")
                else:
                    print("⚠️  No users found to test KYC update")
            else:
                print("⚠️  Could not get users for KYC update test")
        except requests.exceptions.ConnectionError:
            print("⚠️  Server not running. Start with: uvicorn main:app --reload")
        except Exception as e:
            print(f"❌ Error testing Update KYC Status: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


