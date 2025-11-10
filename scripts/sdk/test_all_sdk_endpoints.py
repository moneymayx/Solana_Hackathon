#!/usr/bin/env python3
"""
Comprehensive SDK Endpoint Test

Tests all SDK endpoints via HTTP when backend is running.
"""
import asyncio
import httpx
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


async def test_endpoint(
    client: httpx.AsyncClient,
    method: str,
    endpoint: str,
    data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Test a single endpoint"""
    try:
        if method == "GET":
            response = await client.get(f"{BASE_URL}{endpoint}", timeout=10.0)
        else:
            response = await client.request(
                method,
                f"{BASE_URL}{endpoint}",
                json=data,
                timeout=10.0
            )
        
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else response.text,
            "endpoint": endpoint
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "endpoint": endpoint
        }


async def test_kora_endpoints(client: httpx.AsyncClient):
    """Test all Kora endpoints"""
    print("\n" + "=" * 60)
    print("🔵 Testing Kora SDK Endpoints")
    print("=" * 60)
    
    tests = [
        ("GET", "/api/sdk-test/kora/status", None),
        ("GET", "/api/sdk-test/kora/config", None),
        ("GET", "/api/sdk-test/kora/supported-tokens", None),
    ]
    
    results = []
    for method, endpoint, data in tests:
        print(f"\n📡 {method} {endpoint}")
        result = await test_endpoint(client, method, endpoint, data)
        results.append(result)
        
        if result["success"]:
            print(f"   ✅ Status: {result['status_code']}")
            if isinstance(result["data"], dict):
                # Pretty print relevant fields
                for key, value in result["data"].items():
                    if isinstance(value, bool):
                        status = "✅" if value else "❌"
                        print(f"   {status} {key}: {value}")
                    elif isinstance(value, str) and len(value) < 100:
                        print(f"   • {key}: {value}")
            else:
                print(f"   Response: {json.dumps(result['data'], indent=2)}")
        else:
            print(f"   ❌ Failed: {result.get('error', result.get('status_code'))}")
            if result.get("data"):
                print(f"   Response: {result['data']}")
    
    return results


async def test_attestations_endpoints(client: httpx.AsyncClient):
    """Test all Attestations endpoints"""
    print("\n" + "=" * 60)
    print("🟢 Testing Attestations SDK Endpoints")
    print("=" * 60)
    
    test_wallet = "11111111111111111111111111111111"
    
    tests = [
        ("GET", "/api/sdk-test/attestations/status", None),
        ("GET", f"/api/sdk-test/attestations/all/{test_wallet}", None),
        ("POST", "/api/sdk-test/attestations/verify-kyc", {
            "wallet_address": test_wallet
        }),
        ("POST", "/api/sdk-test/attestations/verify-geographic", {
            "wallet_address": test_wallet,
            "allowed_countries": ["US", "CA"]
        }),
    ]
    
    results = []
    for method, endpoint, data in tests:
        print(f"\n📡 {method} {endpoint}")
        result = await test_endpoint(client, method, endpoint, data)
        results.append(result)
        
        if result["success"]:
            print(f"   ✅ Status: {result['status_code']}")
            if isinstance(result["data"], dict):
                # Pretty print relevant fields
                for key, value in result["data"].items():
                    if isinstance(value, bool):
                        status = "✅" if value else "❌"
                        print(f"   {status} {key}: {value}")
                    elif isinstance(value, str) and len(value) < 100:
                        print(f"   • {key}: {value}")
                    elif key == "message":
                        print(f"   💬 {key}: {value}")
            else:
                print(f"   Response: {json.dumps(result['data'], indent=2)}")
        else:
            print(f"   ❌ Failed: {result.get('error', result.get('status_code'))}")
            if result.get("data"):
                print(f"   Response: {result['data']}")
    
    return results


async def main():
    print("=" * 60)
    print("🧪 SDK Backend Integration - HTTP Endpoint Tests")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    
    # Check if backend is running
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                print("✅ Backend is running!")
            else:
                print(f"⚠️  Backend responded with status {response.status_code}")
        except httpx.ConnectError:
            print("❌ Cannot connect to backend")
            print("💡 Make sure backend is running:")
            print("   python apps/backend/main.py")
            return
        
        # Test endpoints
        kora_results = await test_kora_endpoints(client)
        att_results = await test_attestations_endpoints(client)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        
        kora_passed = sum(1 for r in kora_results if r["success"])
        att_passed = sum(1 for r in att_results if r["success"])
        
        print(f"Kora Endpoints:      {kora_passed}/{len(kora_results)} passed")
        print(f"Attestations:        {att_passed}/{len(att_results)} passed")
        print(f"Total:                {kora_passed + att_passed}/{len(kora_results) + len(att_results)} passed")
        
        if kora_passed == len(kora_results) and att_passed == len(att_results):
            print("\n🎉 All SDK endpoints working!")
        else:
            print("\n⚠️  Some endpoints failed. Check logs above.")


if __name__ == "__main__":
    asyncio.run(main())

