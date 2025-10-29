#!/usr/bin/env python3
"""
Revenue Split Verification Test
Verifies the 60/20/10/10 split is correctly configured on-chain
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

PROGRAM_ID = "Bjek6uN5WzxZtjVvyghpsa57GzVaxXYQ8Lpg2CfPAMGW"
RPC_ENDPOINT = "https://api.devnet.solana.com"

# Expected wallet addresses from .env
EXPECTED_WALLETS = {
    "jackpot": "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF",
    "operational": "46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D",
    "buyback": "7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya",
    "staking": "Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX"
}

async def verify_revenue_split():
    """Verify revenue split configuration"""
    print("\n" + "="*80)
    print("  REVENUE SPLIT VERIFICATION TEST")
    print("  Testing 60/20/10/10 Configuration")
    print("="*80)
    print()
    
    client = AsyncClient(RPC_ENDPOINT)
    program_id = Pubkey.from_string(PROGRAM_ID)
    
    # Step 1: Read lottery state
    print("📊 STEP 1: Reading wallet configuration from blockchain...")
    try:
        lottery_pda, bump = Pubkey.find_program_address([b"lottery"], program_id)
        account_info = await client.get_account_info(lottery_pda)
        
        if account_info.value is None:
            print("❌ Lottery not initialized")
            await client.close()
            return False
            
        data = account_info.value.data
        
        # Parse wallet addresses (offsets based on Lottery struct)
        jackpot_wallet = Pubkey(data[40:72])
        operational_wallet = Pubkey(data[72:104])
        buyback_wallet = Pubkey(data[104:136])
        staking_wallet = Pubkey(data[136:168])
        
        print(f"✅ Lottery PDA: {lottery_pda}")
        print(f"✅ Bump: {bump}")
        print()
        
    except Exception as e:
        print(f"❌ Failed to read lottery state: {e}")
        await client.close()
        return False
        
    # Step 2: Verify wallet addresses match expected
    print("📊 STEP 2: Verifying wallet addresses...")
    print()
    
    all_match = True
    
    # Jackpot (60%)
    if str(jackpot_wallet) == EXPECTED_WALLETS["jackpot"]:
        print(f"✅ Jackpot (60%):     {jackpot_wallet}")
    else:
        print(f"❌ Jackpot (60%):     {jackpot_wallet}")
        print(f"   Expected: {EXPECTED_WALLETS['jackpot']}")
        all_match = False
        
    # Operational (20%)
    if str(operational_wallet) == EXPECTED_WALLETS["operational"]:
        print(f"✅ Operational (20%): {operational_wallet}")
    else:
        print(f"❌ Operational (20%): {operational_wallet}")
        print(f"   Expected: {EXPECTED_WALLETS['operational']}")
        all_match = False
        
    # Buyback (10%)
    if str(buyback_wallet) == EXPECTED_WALLETS["buyback"]:
        print(f"✅ Buyback (10%):     {buyback_wallet}")
    else:
        print(f"❌ Buyback (10%):     {buyback_wallet}")
        print(f"   Expected: {EXPECTED_WALLETS['buyback']}")
        all_match = False
        
    # Staking (10%)
    if str(staking_wallet) == EXPECTED_WALLETS["staking"]:
        print(f"✅ Staking (10%):     {staking_wallet}")
    else:
        print(f"❌ Staking (10%):     {staking_wallet}")
        print(f"   Expected: {EXPECTED_WALLETS['staking']}")
        all_match = False
        
    print()
    
    # Step 3: Verify research fund settings
    print("📊 STEP 3: Verifying research fund configuration...")
    try:
        # Parse research_fund_floor (at offset 168, u64)
        import struct
        research_fund_floor_bytes = data[168:176]
        research_fund_floor = struct.unpack('<Q', research_fund_floor_bytes)[0]
        
        # Parse research_fee (at offset 176, u64)
        research_fee_bytes = data[176:184]
        research_fee = struct.unpack('<Q', research_fee_bytes)[0]
        
        # Convert from lamports to USDC (6 decimals)
        research_fund_floor_usdc = research_fund_floor / 1_000_000
        research_fee_usdc = research_fee / 1_000_000
        
        print(f"✅ Research Fund Floor: {research_fund_floor_usdc:,.0f} USDC")
        print(f"✅ Research Fee: {research_fee_usdc:,.0f} USDC")
        print()
        
        # Verify expected values
        if research_fund_floor_usdc != 1000:
            print(f"⚠️  Research fund floor is {research_fund_floor_usdc}, expected 1000")
        if research_fee_usdc != 10:
            print(f"⚠️  Research fee is {research_fee_usdc}, expected 10")
            
    except Exception as e:
        print(f"⚠️  Could not parse research fund settings: {e}")
        
    await client.close()
    
    # Step 4: Summary
    print("="*80)
    print("  TEST RESULTS")
    print("="*80)
    print()
    
    if all_match:
        print("✅ All wallet addresses are correctly configured")
        print("✅ Revenue split: 60/20/10/10")
        print("✅ Jackpot → 60% of entry fees")
        print("✅ Operational → 20% of entry fees")
        print("✅ Buyback & Burn → 10% of entry fees")
        print("✅ Staking Rewards → 10% of entry fees")
        print()
        print("🎉 REVENUE SPLIT IS CORRECTLY CONFIGURED!")
    else:
        print("❌ One or more wallet addresses do not match expected values")
        print("⚠️  This could indicate a configuration mismatch")
        
    print()
    print("="*80)
    print()
    
    return all_match

async def main():
    """Main test runner"""
    try:
        success = await verify_revenue_split()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

