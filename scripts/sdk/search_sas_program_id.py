#!/usr/bin/env python3
"""
Search for SAS Program ID using multiple methods

This script attempts various approaches to find the Solana Attestations Service
program ID, but ultimately may require manual search on Solana Explorer.
"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solana.rpc.commitment import Confirmed
import httpx


async def method_1_query_known_accounts(rpc_url: str):
    """Try to find program by querying accounts that might be attestations"""
    print("\n📋 Method 1: Querying Known Account Patterns")
    print("-" * 60)
    
    client = AsyncClient(rpc_url, commitment=Confirmed)
    
    # If we knew a wallet with an attestation, we could:
    # 1. Query its accounts
    # 2. Find accounts with "attestation" data
    # 3. Get the owner program ID
    
    print("⚠️  Requires: Wallet with known attestation")
    print("   Without this, we can't query account ownership")
    
    await client.close()


async def method_2_check_documentation_urls():
    """Check if documentation URLs contain program IDs"""
    print("\n📋 Method 2: Checking Documentation")
    print("-" * 60)
    
    urls_to_check = [
        "https://launch.solana.com/docs/attestations",
        "https://attest.solana.com",
    ]
    
    print("Checking documentation URLs...")
    
    for url in urls_to_check:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    content = response.text
                    # Look for program ID pattern (44 char base58)
                    import re
                    # Base58 pattern: 32-44 chars, alphanumeric
                    program_id_pattern = r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b'
                    matches = re.findall(program_id_pattern, content)
                    
                    print(f"✅ {url} - Found {len(matches)} potential addresses")
                    print("   (May include non-program IDs, need to verify)")
                    
                    # Filter to likely program IDs (long base58 strings)
                    likely_programs = [m for m in matches if len(m) >= 40]
                    if likely_programs:
                        print(f"   Potential program IDs: {len(likely_programs)}")
                        for pid in likely_programs[:5]:  # Show first 5
                            print(f"   - {pid}")
        except Exception as e:
            print(f"⚠️  Could not check {url}: {e}")


async def method_3_web_search_results():
    """Analyze web search results for program IDs"""
    print("\n📋 Method 3: Web Search Analysis")
    print("-" * 60)
    
    print("Recent web searches suggest:")
    print("  - SAS is deployed but program ID not easily found")
    print("  - Check official GitHub repositories")
    print("  - Look in example code from sas-lib")
    
    print("\n💡 Recommended Sources:")
    print("  1. GitHub: solana-foundation/attestations (if public)")
    print("  2. npm: @solana-foundation/sas-lib package examples")
    print("  3. Official docs: https://launch.solana.com/docs/attestations")
    print("  4. Solana Explorer: Manual search")


def print_manual_search_instructions():
    """Print detailed manual search instructions"""
    print("\n" + "=" * 60)
    print("📋 MANUAL SEARCH INSTRUCTIONS (Most Reliable Method)")
    print("=" * 60)
    
    print("\n🎯 Step-by-Step:")
    print("\n1. Open Solana Explorer:")
    print("   Devnet: https://explorer.solana.com/?cluster=devnet")
    print("   Mainnet: https://explorer.solana.com/?cluster=mainnet-beta")
    
    print("\n2. Use Search Bar (top right):")
    print("   Try searching for:")
    print("   - 'attestations'")
    print("   - 'SAS'")
    print("   - 'Solana Attestations Service'")
    print("   - 'verifiable credentials'")
    print("   - 'credential'")
    
    print("\n3. Filter Results:")
    print("   - Look for 'Program' type results (not Account or Transaction)")
    print("   - Program addresses are 44 characters (base58)")
    print("   - Example format: 'AbCdEf123456789...'")
    
    print("\n4. Verify It's SAS:")
    print("   - Click on the program")
    print("   - Check program name/description")
    print("   - Look at account data for 'attestation' references")
    print("   - Check recent transactions")
    
    print("\n5. Copy Program ID:")
    print("   - It's the address shown (44 characters)")
    print("   - Format: base58 encoded public key")
    
    print("\n6. Update .env:")
    print("   ATTESTATIONS_PROGRAM_ID_DEVNET=<found_devnet_id>")
    print("   ATTESTATIONS_PROGRAM_ID_MAINNET=<found_mainnet_id>")


async def main():
    print("🔍 SAS Program ID Search - Multiple Methods")
    print("=" * 60)
    
    # Try automated methods
    await method_2_check_documentation_urls()
    await method_1_query_known_accounts("https://api.devnet.solana.com")
    await method_3_web_search_results()
    
    # Show manual instructions
    print_manual_search_instructions()
    
    print("\n" + "=" * 60)
    print("💡 RECOMMENDATION:")
    print("   Manual search on Solana Explorer is most reliable")
    print("   Program IDs may not be published in easily searchable formats")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

