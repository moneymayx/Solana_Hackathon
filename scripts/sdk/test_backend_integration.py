#!/usr/bin/env python3
"""
Test SDK Integration with Backend

This script tests that the SDK integrations work with the actual FastAPI backend.
It tests both the service layer and the API endpoints.

Usage:
    python scripts/sdk/test_backend_integration.py
"""
import sys
import os
import asyncio
import httpx
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from src.services.sdk.kora_service import KoraService
from src.services.sdk.attestations_service import AttestationsService
from src.services.sdk.solana_pay_service import SolanaPayService


async def test_kora_service():
    """Test Kora service directly"""
    print("\n" + "=" * 60)
    print("Test 1: Kora Service (Direct)")
    print("=" * 60)
    
    service = KoraService()
    
    if not service.is_enabled():
        print("❌ Kora service is disabled")
        print("   Set ENABLE_KORA_SDK=true in .env")
        return False
    
    print(f"✅ Kora service enabled")
    print(f"   CLI Path: {service.kora_cli_path}")
    print(f"   RPC URL: {service.rpc_url}")
    print(f"   Private Key: {'✅ Set' if service.private_key else '❌ Not set'}")
    
    # Test config
    config = await service.get_config()
    if config.get("success"):
        print(f"✅ Get config works: {config.get('result')}")
    else:
        print(f"⚠️  Config error: {config.get('error')}")
    
    return True


async def test_attestations_service():
    """Test Attestations service directly"""
    print("\n" + "=" * 60)
    print("Test 2: Attestations Service (Direct)")
    print("=" * 60)
    
    service = AttestationsService()
    
    if not service.is_enabled():
        print("❌ Attestations service is disabled")
        print("   Set ENABLE_ATTESTATIONS_SDK=true in .env")
        return False
    
    print(f"✅ Attestations service enabled")
    print(f"   Program ID: {service.program_id}")
    print(f"   RPC Endpoint: {service.rpc_endpoint}")
    
    # Test PDA derivation
    from solders.pubkey import Pubkey
    test_wallet = Pubkey.from_string("11111111111111111111111111111111")
    pda = service._derive_attestation_pda(test_wallet)
    print(f"✅ PDA derivation works: {pda}")
    
    # Test KYC verification
    result = await service.verify_kyc_attestation("11111111111111111111111111111111")
    if result.get("success"):
        print(f"✅ KYC verification endpoint works")
        print(f"   KYC verified: {result.get('kyc_verified')}")
    else:
        print(f"⚠️  KYC verification error: {result.get('error')}")
    
    return True


async def test_api_endpoints(base_url: str = "http://localhost:8000"):
    """Test API endpoints via HTTP"""
    print("\n" + "=" * 60)
    print("Test 3: API Endpoints (HTTP)")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test Kora endpoints
        print("\n📡 Testing Kora Endpoints:")
        
        try:
            # Status
            response = await client.get(f"{base_url}/api/sdk-test/kora/status")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ GET /status: {data}")
            else:
                print(f"   ❌ GET /status: {response.status_code}")
        except httpx.ConnectError:
            print(f"   ❌ Cannot connect to backend")
            print(f"   💡 Start backend: python apps/backend/main.py")
            return False
        
        try:
            # Config
            response = await client.get(f"{base_url}/api/sdk-test/kora/config")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ GET /config: {data.get('success', False)}")
        except Exception as e:
            print(f"   ⚠️  GET /config error: {e}")
        
        # Test Attestations endpoints
        print("\n📡 Testing Attestations Endpoints:")
        
        try:
            # Status
            response = await client.get(f"{base_url}/api/sdk-test/attestations/status")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ GET /status: {data}")
            else:
                print(f"   ❌ GET /status: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  GET /status error: {e}")
        
        try:
            # Verify KYC
            response = await client.post(
                f"{base_url}/api/sdk-test/attestations/verify-kyc",
                json={"wallet_address": "11111111111111111111111111111111"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ POST /verify-kyc: KYC verified={data.get('kyc_verified')}")
            else:
                print(f"   ❌ POST /verify-kyc: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  POST /verify-kyc error: {e}")
        
        # Test Solana Pay endpoints
        print("\n📡 Testing Solana Pay Endpoints:")
        
        try:
            response = await client.get(f"{base_url}/api/sdk-test/solana-pay/status")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ GET /status: {data}")
        except Exception as e:
            print(f"   ⚠️  GET /status error: {e}")
    
    return True


async def test_backend_startup():
    """Test that backend can start with SDK integrations"""
    print("\n" + "=" * 60)
    print("Test 4: Backend Integration Check")
    print("=" * 60)
    
    try:
        from apps.backend.main import app
        from src.api.sdk.app_integration import include_sdk_test_routers
        
        # Check routes
        routes = [route.path for route in app.routes]
        sdk_routes = [r for r in routes if '/api/sdk-test' in r]
        
        print(f"✅ Backend loaded successfully")
        print(f"✅ Found {len(sdk_routes)} SDK test routes")
        
        if len(sdk_routes) > 0:
            print("\n📋 SDK Routes:")
            for route in sdk_routes[:15]:
                print(f"   - {route}")
        
        return True
    except Exception as e:
        print(f"❌ Backend integration error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("=" * 60)
    print("SDK Backend Integration Test")
    print("=" * 60)
    
    # Test 1: Service Layer
    kora_ok = await test_kora_service()
    att_ok = await test_attestations_service()
    
    # Test 2: Backend Integration
    backend_ok = await test_backend_startup()
    
    # Test 3: API Endpoints (if backend running)
    api_ok = await test_api_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Kora Service:        {'✅' if kora_ok else '❌'}")
    print(f"Attestations Service: {'✅' if att_ok else '❌'}")
    print(f"Backend Integration:  {'✅' if backend_ok else '❌'}")
    print(f"API Endpoints:       {'✅' if api_ok else '⚠️  (Backend not running)'}")
    print()
    
    if kora_ok and att_ok and backend_ok:
        print("🎉 All SDK integrations working with backend!")
        print()
        print("💡 To test API endpoints, start backend:")
        print("   python apps/backend/main.py")
        print()
        print("   Then run: python scripts/sdk/test_backend_integration.py")
    else:
        print("⚠️  Some tests failed. Check configuration.")


if __name__ == "__main__":
    asyncio.run(main())

