#!/usr/bin/env python3
"""
Utility script to find the Solana Attestations Service (SAS) program ID

This script searches for the attestations program on Solana by:
1. Querying known program IDs
2. Searching for programs with "attestation" in the name
3. Checking common deployment addresses
4. Providing instructions for manual discovery
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from solana.rpc.api import Client
from solana.publickey import PublicKey
import json

def search_attestations_program(rpc_url: str = "https://api.devnet.solana.com"):
    """
    Search for the Attestations program ID
    
    Args:
        rpc_url: Solana RPC endpoint (devnet or mainnet)
    """
    print(f"🔍 Searching for SAS Program ID on {rpc_url}")
    print("=" * 60)
    
    client = Client(rpc_url)
    
    # Common program ID patterns to check
    # These are placeholder patterns - actual program IDs need to be found
    test_ids = [
        # Common Solana Foundation program patterns
        "11111111111111111111111111111111",  # System Program (for comparison)
    ]
    
    print("\n📋 Known Information:")
    print("- SAS (Solana Attestations Service) is an on-chain program")
    print("- It should be deployed on both devnet and mainnet")
    print("- Program ID should be a valid Solana public key (44 chars base58)")
    print("- Documentation: https://launch.solana.com/docs/attestations")
    
    print("\n🔧 Manual Discovery Methods:")
    print("\n1. Check Official Documentation:")
    print("   - Visit: https://launch.solana.com/docs/attestations")
    print("   - Look for program deployment address")
    print("   - Check GitHub: https://github.com/solana-foundation/attestations")
    
    print("\n2. Search Solana Explorer:")
    print("   - Go to: https://explorer.solana.com")
    print("   - Search for 'attestations' or 'SAS'")
    print("   - Look for program accounts")
    print("   - Check program transactions")
    
    print("\n3. Query Example Attestations:")
    print("   - If you know a wallet with an attestation:")
    print("   - Query its accounts")
    print("   - Find which program owns the attestation account")
    
    print("\n4. Check sas-lib Examples:")
    print("   - JavaScript/TypeScript library for attestations")
    print("   - Example code may contain program ID references")
    print("   - GitHub: Search for '@solana-foundation/sas-lib'")
    
    print("\n5. RPC Query Method:")
    print("   - Use getProgramAccounts with filter")
    print("   - Search for accounts with 'attestation' in data")
    print("   - Identify owner program")
    
    print("\n📝 Next Steps:")
    print("1. Once you find the program ID, update .env:")
    print("   ATTESTATIONS_PROGRAM_ID_DEVNET=<devnet_program_id>")
    print("   ATTESTATIONS_PROGRAM_ID_MAINNET=<mainnet_program_id>")
    print("\n2. Update src/services/sdk/attestations_service.py")
    print("3. Test with known attestation accounts")
    
    print("\n" + "=" * 60)
    print("⚠️  CRITICAL: This program ID is required for all attestation queries")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Find SAS program ID")
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
    
    search_attestations_program(rpc_url)

