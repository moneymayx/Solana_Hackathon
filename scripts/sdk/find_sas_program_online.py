#!/usr/bin/env python3
"""
Alternative script to find SAS program ID by searching online sources
"""
import sys

def search_for_sas_program_id():
    """Search for SAS program ID from various sources"""
    
    print("🔍 Searching for SAS Program ID...")
    print("=" * 60)
    
    # Common places to find program IDs:
    sources = [
        {
            "name": "Solana Explorer - Search",
            "url": "https://explorer.solana.com",
            "method": "manual",
            "note": "Search for 'attestations' or 'SAS' in program accounts"
        },
        {
            "name": "Solana Foundation GitHub",
            "url": "https://github.com/solana-foundation",
            "method": "search",
            "note": "Look for attestations repository"
        },
        {
            "name": "Official Documentation",
            "url": "https://launch.solana.com/docs/attestations",
            "method": "check",
            "note": "Check official docs for deployment information"
        }
    ]
    
    print("\n📋 Search Strategy:")
    print("\n1. Check Official Documentation:")
    print("   https://launch.solana.com/docs/attestations")
    print("   - Look for 'Program ID' or 'Deployment' section")
    print("   - Check examples for program addresses")
    
    print("\n2. Search Solana Explorer:")
    print("   https://explorer.solana.com")
    print("   - Search for 'attestations'")
    print("   - Look for program accounts")
    print("   - Check program transactions")
    
    print("\n3. Check GitHub:")
    print("   - Search: github.com/solana-foundation/attestations")
    print("   - Look in README or deployment files")
    print("   - Check example code for program ID references")
    
    print("\n4. Check sas-lib Examples:")
    print("   - JavaScript/TypeScript library examples")
    print("   - May contain program ID in example code")
    print("   - npm: @solana-foundation/sas-lib")
    
    print("\n5. Query Solana RPC:")
    print("   - Search for programs with 'attestation' in name")
    print("   - Look for recent deployments")
    print("   - Check program data for identifiers")
    
    print("\n" + "=" * 60)
    print("💡 Manual Discovery Steps:")
    print("1. Visit: https://explorer.solana.com/?cluster=devnet")
    print("2. Use search bar: search for 'attestations' or 'SAS'")
    print("3. Look for program accounts")
    print("4. Click on a program to see its address")
    print("5. Verify it's the SAS program by checking program data")
    
    print("\n⚠️  Note: Program IDs may differ for devnet vs mainnet")
    print("   Make sure to check both networks if deploying to both")


if __name__ == "__main__":
    search_for_sas_program_id()

