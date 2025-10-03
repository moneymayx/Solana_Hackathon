#!/usr/bin/env python3
"""
Comprehensive Test Suite for Billions Bounty Lottery
Tests all major functions of the deployed smart contract
"""
import os
import sys
import asyncio
import json
from pathlib import Path
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.instruction import Instruction, AccountMeta
from solana.rpc.types import TxOpts
import struct
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration
PROGRAM_ID = Pubkey.from_string("4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK")
LOTTERY_PDA = Pubkey.from_string("9nrqftRQVcZUvrRpFJaVgqv49D8ffAEWw3ggUqfomNiJ")
RPC_URL = "https://api.devnet.solana.com"
USDC_MINT_DEVNET = Pubkey.from_string("Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr")

# Test parameters
ENTRY_AMOUNT = 10_000_000  # 10 USDC


def load_keypair(keypair_path: str) -> Keypair:
    """Load keypair from JSON file"""
    with open(keypair_path, 'r') as f:
        keypair_data = json.load(f)
    
    if isinstance(keypair_data, list):
        keypair_bytes = bytes(keypair_data)
    else:
        keypair_bytes = bytes(keypair_data['secretKey'])
    
    return Keypair.from_bytes(keypair_bytes)


def derive_entry_pda(user_pubkey: Pubkey, lottery_pda: Pubkey, program_id: Pubkey) -> tuple[Pubkey, int]:
    """Derive entry PDA for a user"""
    seeds = [b"entry", bytes(lottery_pda), bytes(user_pubkey)]
    return Pubkey.find_program_address(seeds, program_id)


def create_process_entry_instruction(
    user: Pubkey,
    lottery_pda: Pubkey,
    entry_pda: Pubkey,
    entry_amount: int,
    program_id: Pubkey
) -> Instruction:
    """Create process_entry_payment instruction"""
    import hashlib
    discriminator_str = "global:process_entry_payment"
    discriminator = hashlib.sha256(discriminator_str.encode()).digest()[:8]
    
    # Pack: discriminator + entry_amount (u64) + user_wallet (32 bytes)
    instruction_data = discriminator + struct.pack('<Q', entry_amount) + bytes(user)
    
    # Accounts for ProcessEntryPayment
    accounts = [
        AccountMeta(pubkey=lottery_pda, is_signer=False, is_writable=True),  # lottery
        AccountMeta(pubkey=entry_pda, is_signer=False, is_writable=True),    # entry
        AccountMeta(pubkey=user, is_signer=True, is_writable=True),          # user
        AccountMeta(pubkey=USDC_MINT_DEVNET, is_signer=False, is_writable=False),  # usdc_mint
        AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # system_program
        AccountMeta(pubkey=Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"), is_signer=False, is_writable=False),  # associated_token_program
        AccountMeta(pubkey=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"), is_signer=False, is_writable=False),  # token_program
    ]
    
    return Instruction(
        program_id=program_id,
        data=instruction_data,
        accounts=accounts
    )


def create_select_winner_instruction(
    lottery_pda: Pubkey,
    program_id: Pubkey
) -> Instruction:
    """Create select_winner instruction"""
    import hashlib
    discriminator_str = "global:select_winner"
    discriminator = hashlib.sha256(discriminator_str.encode()).digest()[:8]
    
    # No additional data needed for select_winner
    instruction_data = discriminator
    
    # Accounts for SelectWinner
    accounts = [
        AccountMeta(pubkey=lottery_pda, is_signer=False, is_writable=True),  # lottery
        AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # system_program
    ]
    
    return Instruction(
        program_id=program_id,
        data=instruction_data,
        accounts=accounts
    )


async def test_lottery_state(client: AsyncClient, lottery_pda: Pubkey):
    """Test 1: Check lottery state"""
    print("🧪 TEST 1: Checking Lottery State")
    print("=" * 40)
    
    try:
        account_info = await client.get_account_info(lottery_pda, commitment=Confirmed)
        
        if account_info.value is None:
            print("❌ Lottery PDA not found!")
            return False
        
        print(f"✅ Lottery PDA found: {lottery_pda}")
        print(f"   Owner: {account_info.value.owner}")
        print(f"   Data length: {len(account_info.value.data)} bytes")
        print(f"   Balance: {account_info.value.lamports / 1_000_000_000} SOL")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking lottery state: {e}")
        return False


async def test_entry_payment(client: AsyncClient, user_keypair: Keypair):
    """Test 2: Process entry payment"""
    print("\n🧪 TEST 2: Processing Entry Payment")
    print("=" * 40)
    
    try:
        # Derive entry PDA
        entry_pda, entry_bump = derive_entry_pda(user_keypair.pubkey(), LOTTERY_PDA, PROGRAM_ID)
        print(f"Entry PDA: {entry_pda}")
        
        # Check if entry already exists
        entry_info = await client.get_account_info(entry_pda, commitment=Confirmed)
        if entry_info.value is not None:
            print("⚠️  Entry already exists - skipping test")
            return True
        
        # Create instruction
        instruction = create_process_entry_instruction(
            user=user_keypair.pubkey(),
            lottery_pda=LOTTERY_PDA,
            entry_pda=entry_pda,
            entry_amount=ENTRY_AMOUNT,
            program_id=PROGRAM_ID
        )
        
        # Get recent blockhash
        recent_blockhash_resp = await client.get_latest_blockhash()
        recent_blockhash = recent_blockhash_resp.value.blockhash
        
        # Create transaction
        transaction = Transaction.new_signed_with_payer(
            [instruction],
            user_keypair.pubkey(),
            [user_keypair],
            recent_blockhash
        )
        
        # Send transaction
        print("🚀 Sending entry payment transaction...")
        tx_opts = TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
        signature = await client.send_transaction(transaction, opts=tx_opts)
        
        print(f"✅ Transaction sent: {signature.value}")
        print("⏳ Confirming...")
        
        # Confirm transaction
        confirmation = await client.confirm_transaction(signature.value, commitment=Confirmed)
        
        if confirmation.value:
            print("✅ Entry payment successful!")
            print(f"📊 View: https://explorer.solana.com/tx/{signature.value}?cluster=devnet")
            return True
        else:
            print("❌ Transaction failed to confirm")
            return False
            
    except Exception as e:
        print(f"❌ Error processing entry payment: {e}")
        return False


async def test_winner_selection(client: AsyncClient, authority_keypair: Keypair):
    """Test 3: Select winner"""
    print("\n🧪 TEST 3: Selecting Winner")
    print("=" * 40)
    
    try:
        # Create instruction
        instruction = create_select_winner_instruction(LOTTERY_PDA, PROGRAM_ID)
        
        # Get recent blockhash
        recent_blockhash_resp = await client.get_latest_blockhash()
        recent_blockhash = recent_blockhash_resp.value.blockhash
        
        # Create transaction
        transaction = Transaction.new_signed_with_payer(
            [instruction],
            authority_keypair.pubkey(),
            [authority_keypair],
            recent_blockhash
        )
        
        # Send transaction
        print("🚀 Sending winner selection transaction...")
        tx_opts = TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
        signature = await client.send_transaction(transaction, opts=tx_opts)
        
        print(f"✅ Transaction sent: {signature.value}")
        print("⏳ Confirming...")
        
        # Confirm transaction
        confirmation = await client.confirm_transaction(signature.value, commitment=Confirmed)
        
        if confirmation.value:
            print("✅ Winner selection successful!")
            print(f"📊 View: https://explorer.solana.com/tx/{signature.value}?cluster=devnet")
            return True
        else:
            print("❌ Transaction failed to confirm")
            return False
            
    except Exception as e:
        print(f"❌ Error selecting winner: {e}")
        return False


async def run_comprehensive_tests():
    """Run all tests"""
    print("🚀 BILLIONS BOUNTY - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"Program ID: {PROGRAM_ID}")
    print(f"Lottery PDA: {LOTTERY_PDA}")
    print(f"Network: Devnet")
    print()
    
    # Load keypairs
    print("📂 Loading keypairs...")
    authority = load_keypair("/Users/jaybrantley/.config/solana/id.json")
    print(f"✅ Authority: {authority.pubkey()}")
    
    # Create test user
    user = Keypair()
    print(f"✅ Test User: {user.pubkey()}")
    
    # Fund test user
    print("\n💰 Funding test user...")
    client = AsyncClient(RPC_URL, commitment=Confirmed)
    
    try:
        # Request airdrop for test user
        print("🪂 Requesting airdrop for test user...")
        airdrop_sig = await client.request_airdrop(user.pubkey(), 2_000_000_000)  # 2 SOL
        
        # Confirm airdrop
        await client.confirm_transaction(airdrop_sig.value, commitment=Confirmed)
        print("✅ Test user funded!")
        
        # Run tests
        results = []
        
        # Test 1: Lottery State
        results.append(await test_lottery_state(client, LOTTERY_PDA))
        
        # Test 2: Entry Payment
        results.append(await test_entry_payment(client, user))
        
        # Test 3: Winner Selection (only if we have entries)
        results.append(await test_winner_selection(client, authority))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        test_names = ["Lottery State", "Entry Payment", "Winner Selection"]
        for i, (name, result) in enumerate(zip(test_names, results)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{i+1}. {name}: {status}")
        
        passed = sum(results)
        total = len(results)
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️  Some tests failed - check logs above")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())
