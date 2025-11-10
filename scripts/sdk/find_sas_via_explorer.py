#!/usr/bin/env python3
"""
Find SAS Program ID by searching Solana Explorer

This script provides instructions and attempts to query Solana RPC
for programs that might be the Attestations service.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
import asyncio


async def search_programs(rpc_url: str = "https://api.devnet.solana.com"):
    """
    Search for programs that might be SAS
    
    Note: This is limited - we need the actual program ID
    """
    print(f"🔍 Searching for SAS Program on {rpc_url}")
    print("=" * 60)
    
    client = AsyncClient(rpc_url, commitment=Confirmed)
    
    print("\n⚠️  RPC Limitations:")
    print("   - Cannot directly search by program name")
    print("   - Need program ID from official sources")
    print("   - Solana Explorer search is required")
    
    print("\n📋 Manual Search Instructions:")
    print("\n1. Visit Solana Explorer:")
    print("   Devnet: https://explorer.solana.com/?cluster=devnet")
    print("   Mainnet: https://explorer.solana.com/?cluster=mainnet-beta")
    
    print("\n2. Search for:")
    print("   - 'attestations'")
    print("   - 'SAS'")
    print("   - 'Solana Attestations Service'")
    print("   - 'verifiable credentials'")
    
    print("\n3. Look for:")
    print("   - Program accounts (not regular accounts)")
    print("   - Recent deployments")
    print("   - Accounts owned by the program")
    
    print("\n4. Verify it's SAS:")
    print("   - Check program data for 'attestation' references")
    print("   - Look for credential/schema mentions")
    print("   - Check transaction history")
    
    print("\n📚 Alternative Sources:")
    print("   - Official docs: https://launch.solana.com/docs/attestations")
    print("   - GitHub: Search 'solana-foundation/attestations'")
    print("   - npm: Check @solana-foundation/sas-lib examples")
    print("   - Contact: Solana Foundation support")
    
    print("\n💡 Once Found:")
    print("   Update .env with:")
    print("   ATTESTATIONS_PROGRAM_ID_DEVNET=<found_devnet_id>")
    print("   ATTESTATIONS_PROGRAM_ID_MAINNET=<found_mainnet_id>")
    
    await client.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Search for SAS program ID")
    parser.add_argument(
        "--network",
        choices=["devnet", "mainnet"],
        default="devnet",
        help="Network to search (default: devnet)"
    )
    
    args = parser.parse_args()
    
    if args.network == "mainnet":
        rpc_url = "https://api.mainnet-beta.solana.com"
    else:
        rpc_url = "https://api.devnet.solana.com"
    
    asyncio.run(search_programs(rpc_url))

