#!/usr/bin/env python3
"""
Test script for V3 backend test contract endpoint
Tests the /api/v3/payment/test endpoint without requiring a full server
"""
import sys
import os
import asyncio
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from solders.pubkey import Pubkey
from solders.keypair import Keypair


async def test_v3_payment_endpoint():
    """Test the V3 payment test endpoint logic"""
    print("🧪 Testing V3 Backend Payment Endpoint\n")
    
    try:
        # Import dependencies
        from apps.backend.api.v3_payment_router import V3TestPaymentRequest
        from src.services.contract_adapter_v3 import get_contract_adapter_v3, USE_CONTRACT_V3
        
        print(f"1. Contract adapter check:")
        print(f"   USE_CONTRACT_V3 = {USE_CONTRACT_V3}")
        
        if not USE_CONTRACT_V3:
            print("   ⚠️  USE_CONTRACT_V3 is False - set it to 'true' in .env")
            return False
        
        adapter = get_contract_adapter_v3()
        if not adapter:
            print("   ❌ Adapter is None")
            return False
        
        print(f"   ✅ Adapter initialized")
        print(f"   ✅ Program ID: {adapter.program_id}")
        print(f"   ✅ RPC Endpoint: {adapter.rpc_endpoint}")
        print(f"   ✅ USDC Mint: {adapter.usdc_mint}")
        print(f"   ✅ Lottery PDA: {adapter.lottery_pda}")
        
        # Check if backend wallet exists
        print(f"\n2. Backend wallet check:")
        wallet_path = os.path.expanduser("~/.config/solana/id.json")
        if os.path.exists(wallet_path):
            print(f"   ✅ Backend wallet found: {wallet_path}")
            try:
                with open(wallet_path, 'r') as f:
                    keypair_data = json.load(f)
                backend_keypair = Keypair.from_bytes(bytes(keypair_data))
                backend_wallet = backend_keypair.pubkey()
                print(f"   ✅ Backend wallet address: {backend_wallet}")
            except Exception as e:
                print(f"   ❌ Error loading wallet: {e}")
                return False
        else:
            print(f"   ⚠️  Backend wallet not found at {wallet_path}")
            print(f"   💡 Create one with: solana-keygen new --outfile {wallet_path}")
            return False
        
        # Check lottery initialization
        print(f"\n3. Lottery initialization check:")
        from solana.rpc.async_api import AsyncClient
        from solana.rpc.commitment import Confirmed
        
        client = AsyncClient(adapter.rpc_endpoint, commitment=Confirmed)
        lottery_account = await client.get_account_info(adapter.lottery_pda)
        
        if lottery_account.value:
            print(f"   ✅ Lottery account exists")
            print(f"   ✅ Account size: {len(lottery_account.value.data)} bytes")
        else:
            print(f"   ⚠️  Lottery account not initialized")
            print(f"   💡 Initialize with: node scripts/initialize_v3_final.js")
            return False
        
        # Test request creation
        print(f"\n4. Request structure check:")
        test_request = V3TestPaymentRequest(
            user_wallet="TestUserWallet11111111111111111111111111",
            entry_amount=10_000_000,  # 10 USDC
            amount_usdc=10.0
        )
        print(f"   ✅ Request model works")
        print(f"   ✅ Entry amount: {test_request.entry_amount} (smallest units)")
        print(f"   ✅ Amount USDC: {test_request.amount_usdc}")
        
        print(f"\n✅ All basic checks passed!")
        print(f"\n📝 Next steps:")
        print(f"   1. Ensure backend wallet has USDC on devnet")
        print(f"   2. Start backend server: python3 apps/backend/main.py")
        print(f"   3. Set frontend .env.local: NEXT_PUBLIC_PAYMENT_MODE=test_contract")
        print(f"   4. Test payment from frontend UI")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_v3_payment_endpoint())
    sys.exit(0 if result else 1)




