#!/usr/bin/env python3
"""
Test Revenue Split - Verify 60/20/10/10 Distribution
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def main():
    print("=" * 80)
    print("  TESTING REVENUE SPLIT (60/20/10/10)")
    print("=" * 80)
    print()
    
    # Get wallet addresses
    jackpot = os.getenv('JACKPOT_WALLET_ADDRESS')
    operational = os.getenv('OPERATIONAL_WALLET_ADDRESS')
    buyback = os.getenv('BUYBACK_WALLET_ADDRESS')
    staking = os.getenv('STAKING_WALLET_ADDRESS')
    program_id = os.getenv('LOTTERY_PROGRAM_ID')
    
    print("✅ Contract Configuration:")
    print(f"   Program ID: {program_id}")
    print()
    print("   Wallet Addresses:")
    print(f"   • Jackpot (60%):     {jackpot}")
    print(f"   • Operational (20%): {operational}")
    print(f"   • Buyback (10%):     {buyback}")
    print(f"   • Staking (10%):     {staking}")
    print()
    
    print("=" * 80)
    print("  TEST SCENARIO: $10 Payment")
    print("=" * 80)
    print()
    print("Expected Split:")
    print("   Jackpot:     $6.00 (60%)")
    print("   Operational: $2.00 (20%)")
    print("   Buyback:     $1.00 (10%)")
    print("   Staking:     $1.00 (10%)")
    print("   ─────────────────────")
    print("   Total:       $10.00")
    print()
    
    print("=" * 80)
    print("  HOW TO TEST:")
    print("=" * 80)
    print()
    print("The lottery contract is LIVE on devnet. To test the revenue split:")
    print()
    print("Option A: Via Backend API")
    print("─────────────────────────")
    print("1. Start your backend:")
    print("   cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty")
    print("   source venv/bin/activate")
    print("   python3 src/main.py")
    print()
    print("2. Make a test payment via API:")
    print("   curl -X POST http://localhost:8000/api/bounty/entry \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print('       "user_id": 1,')
    print('       "bounty_id": 1,')
    print('       "amount": 10.0,')
    print('       "wallet_address": "YOUR_TEST_WALLET"')
    print("     }'")
    print()
    print("Option B: Via Frontend")
    print("─────────────────────────")
    print("1. Start your frontend:")
    print("   cd frontend && npm run dev")
    print()
    print("2. Connect wallet and make a $10 payment")
    print()
    print("Option C: Direct Smart Contract Call")
    print("─────────────────────────────────────")
    print("1. Use Solana CLI to call process_entry_payment")
    print("2. This requires crafting the transaction manually")
    print()
    
    print("=" * 80)
    print("  VERIFICATION STEPS:")
    print("=" * 80)
    print()
    print("After making a payment, check wallet balances:")
    print()
    print(f"# Jackpot (should increase by $6)")
    print(f"solana balance {jackpot} --url devnet")
    print()
    print(f"# Operational (should increase by $2)")
    print(f"solana balance {operational} --url devnet")
    print()
    print(f"# Buyback (should increase by $1)")
    print(f"solana balance {buyback} --url devnet")
    print()
    print(f"# Staking (should increase by $1)")
    print(f"solana balance {staking} --url devnet")
    print()
    
    print("=" * 80)
    print("  AUTOMATED TEST CALCULATION:")
    print("=" * 80)
    print()
    
    # Calculate splits for various amounts
    test_amounts = [10, 50, 100, 1000]
    
    for amount in test_amounts:
        jackpot_amt = amount * 0.60
        ops_amt = amount * 0.20
        buyback_amt = amount * 0.10
        staking_amt = amount * 0.10
        
        print(f"${amount} payment splits to:")
        print(f"   Jackpot:     ${jackpot_amt:>7.2f} (60%)")
        print(f"   Operational: ${ops_amt:>7.2f} (20%)")
        print(f"   Buyback:     ${buyback_amt:>7.2f} (10%)")
        print(f"   Staking:     ${staking_amt:>7.2f} (10%)")
        print(f"   Total:       ${amount:>7.2f}")
        print()
    
    print("=" * 80)
    print("  MONITORING:")
    print("=" * 80)
    print()
    print("Watch transactions in real-time:")
    print("  solana logs", program_id, "--url devnet")
    print()
    print("View in Solana Explorer:")
    print(f"  https://explorer.solana.com/address/{program_id}?cluster=devnet")
    print()
    
    print("=" * 80)
    print()
    print("✅ Revenue split test ready!")
    print("   Make a payment and verify the 60/20/10/10 distribution.")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

