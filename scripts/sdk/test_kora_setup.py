#!/usr/bin/env python3
"""
Utility script to test Kora JSON-RPC setup and discover API formats

This script helps:
1. Test connection to Kora server
2. Discover JSON-RPC method formats
3. Verify transaction encoding
4. Document actual API responses
"""
import sys
import os
import asyncio
import httpx
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

async def test_kora_connection(rpc_url: str = "http://localhost:8080"):
    """
    Test connection to Kora JSON-RPC server
    
    Args:
        rpc_url: Kora server URL (default: localhost:8080)
    """
    print(f"🧪 Testing Kora Connection: {rpc_url}")
    print("=" * 60)
    
    # Test basic JSON-RPC call (getConfig or similar)
    test_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getConfig",
        "params": {}
    }
    
    print("\n📤 Test Request:")
    print(json.dumps(test_payload, indent=2))
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                rpc_url,
                json=test_payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"\n📥 Response Status: {response.status_code}")
            print(f"📥 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ Success Response:")
                print(json.dumps(data, indent=2))
                
                if "result" in data:
                    print("\n✅ Kora server is responding correctly!")
                    return True
                elif "error" in data:
                    print("\n⚠️  JSON-RPC Error:")
                    print(f"   Code: {data['error'].get('code')}")
                    print(f"   Message: {data['error'].get('message')}")
                    return False
            else:
                print(f"\n❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except httpx.ConnectError:
        print("\n❌ Connection Failed")
        print("   Kora server is not running or not accessible")
        print("\n🔧 To start Kora server:")
        print("   1. Install: cargo install kora-cli")
        print("   2. Run: kora rpc")
        print("   3. Default port: 8080")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def print_setup_instructions():
    """Print instructions for setting up and testing Kora"""
    print("\n" + "=" * 60)
    print("📚 Kora Setup Instructions")
    print("=" * 60)
    
    print("\n1. Install Kora CLI:")
    print("   cargo install kora-cli")
    
    print("\n2. Run Kora Server:")
    print("   kora rpc")
    print("   # Runs on http://localhost:8080 by default")
    
    print("\n3. Configure Environment (.env):")
    print("   ENABLE_KORA_SDK=true")
    print("   KORA_RPC_URL=http://localhost:8080")
    print("   KORA_API_KEY=your_api_key_if_required")
    
    print("\n4. Test JSON-RPC Methods:")
    print("   - getConfig: Get Kora server configuration")
    print("   - signTransaction: Sign transaction with fee abstraction")
    print("   - signAndSendTransaction: Sign and send with fee abstraction")
    print("   - estimateTransactionFee: Estimate fees in different tokens")
    
    print("\n5. Transaction Format Discovery:")
    print("   - Check Kora documentation for transaction encoding")
    print("   - Test with a simple transaction first")
    print("   - Verify base64 encoding vs other formats")
    
    print("\n📖 Documentation:")
    print("   https://launch.solana.com/docs/kora")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Kora JSON-RPC setup")
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8080",
        help="Kora server URL (default: http://localhost:8080)"
    )
    
    args = parser.parse_args()
    
    print_setup_instructions()
    print("\n")
    
    result = asyncio.run(test_kora_connection(args.url))
    
    if not result:
        print("\n⚠️  Connection failed. Make sure Kora server is running.")
        sys.exit(1)
    else:
        print("\n✅ Kora connection test successful!")
        print("   You can now proceed with testing fee abstraction")

