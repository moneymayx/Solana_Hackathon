#!/usr/bin/env python3
"""
Test Escape Plan Timer - Live Devnet Test
Verifies the on-chain 24-hour timer functionality
"""

import asyncio
import os
import sys
import time
import httpx
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
import struct

PROGRAM_ID = "Bjek6uN5WzxZtjVvyghpsa57GzVaxXYQ8Lpg2CfPAMGW"
RPC_ENDPOINT = "https://api.devnet.solana.com"
API_BASE = "http://localhost:8000"

async def read_timer_from_chain():
    """Read timer directly from blockchain"""
    client = AsyncClient(RPC_ENDPOINT)
    program_id = Pubkey.from_string(PROGRAM_ID)
    
    lottery_pda, _ = Pubkey.find_program_address([b"lottery"], program_id)
    account_info = await client.get_account_info(lottery_pda)
    
    if account_info.value is None:
        await client.close()
        raise Exception("Lottery not initialized")
        
    data = account_info.value.data
    
    # Parse next_rollover (at offset 249)
    next_rollover_bytes = data[249:257]
    next_rollover = struct.unpack('<q', next_rollover_bytes)[0]
    
    # Parse last_participant (at offset 257)
    last_participant_bytes = data[257:289]
    last_participant = Pubkey(last_participant_bytes)
    
    await client.close()
    
    return next_rollover, last_participant

async def test_escape_timer():
    """Test the escape plan timer functionality"""
    print("\n" + "="*80)
    print("  ESCAPE PLAN TIMER TEST")
    print("  Testing On-Chain 24-Hour Countdown")
    print("="*80)
    print()
    
    # Step 1: Read initial timer state
    print("📊 STEP 1: Reading initial timer state from blockchain...")
    try:
        initial_rollover, initial_participant = await read_timer_from_chain()
        current_time = int(time.time())
        initial_remaining = initial_rollover - current_time
        
        print(f"✅ Current Time: {datetime.fromtimestamp(current_time)}")
        print(f"✅ Next Rollover: {datetime.fromtimestamp(initial_rollover)}")
        print(f"✅ Time Remaining: {initial_remaining/3600:.2f} hours")
        print(f"✅ Last Participant: {initial_participant}")
        print()
        
    except Exception as e:
        print(f"❌ Failed to read timer: {e}")
        return False
        
    # Step 2: Check if API is accessible
    print("📊 STEP 2: Checking API accessibility...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE}/")
            if response.status_code == 200:
                print(f"✅ API is accessible")
            else:
                print(f"⚠️  API returned status {response.status_code}")
            print()
    except Exception as e:
        print(f"⚠️  API check failed: {e}")
        print("   (This is OK if backend is not running)")
        print()
        
    # Step 3: Verify timer is working
    print("📊 STEP 3: Verifying timer logic...")
    
    if initial_rollover == 0:
        print("❌ Timer not initialized (zero value)")
        return False
        
    # Check if timer is reasonable (within 48 hours from now)
    max_future = current_time + (48 * 3600)
    if initial_rollover > max_future:
        print(f"❌ Timer is too far in future: {initial_rollover}")
        return False
        
    print("✅ Timer value is valid")
    print()
    
    # Step 4: Summary
    print("="*80)
    print("  TEST RESULTS")
    print("="*80)
    print()
    print("✅ Escape timer is stored on-chain")
    print("✅ Timer data is accessible")
    print("✅ Timer value is valid")
    print()
    
    if initial_remaining < 0:
        print("⚠️  NOTICE: Timer has expired (negative remaining time)")
        print("   This means 24 hours have passed since last activity")
        print("   The escape plan can now be executed")
    elif initial_remaining > 0:
        hours_remaining = initial_remaining / 3600
        print(f"✅ Timer is active: {hours_remaining:.2f} hours remaining")
        print(f"   Expires at: {datetime.fromtimestamp(initial_rollover)}")
        
    print()
    print("="*80)
    print()
    
    return True

async def main():
    """Main test runner"""
    try:
        success = await test_escape_timer()
        if success:
            print("🎉 ESCAPE TIMER TEST PASSED!")
            sys.exit(0)
        else:
            print("❌ ESCAPE TIMER TEST FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

