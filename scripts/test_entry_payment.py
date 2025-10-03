#!/usr/bin/env python3
"""
Test Entry Payment Script
Tests the lottery entry payment flow on devnet
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
import hashlib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration
PROGRAM_ID = Pubkey.from_string("DAgzfNPpc3i2EttgxfRtSN4SXQ4CwXQYjStmgrnw3BYh")
RPC_URL = "https://api.devnet.solana.com"
USDC_MINT_DEVNET = Pubkey.from_string("Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr")

# Entry parameters
ENTRY_AMOUNT = 10_000_000  # 10 USDC (with 6 decimals)


def load_user_keypair(keypair_path: str) -> Keypair:
    """Load user keypair from JSON file"""
    print(f"📂 Loading user keypair from: {keypair_path}")
    
    with open(keypair_path, 'r') as f:
        keypair_data = json.load(f)
    
    if isinstance(keypair_data, list):
        keypair_bytes = bytes(keypair_data)
    else:
        keypair_bytes = bytes(keypair_data['secretKey'])
    
    keypair = Keypair.from_bytes(keypair_bytes)
    print(f"✅ User wallet: {keypair.pubkey()}")
    return keypair


def derive_lottery_pda(program_id: Pubkey) -> tuple[Pubkey, int]:
    """Derive the lottery PDA address"""
    seeds = [b"lottery"]
    pda, bump = Pubkey.find_program_address(seeds, program_id)
    return pda, bump


def create_entry_payment_instruction(
    user: Pubkey,
    lottery_pda: Pubkey,
    entry_amount: int,
    user_wallet: Pubkey
) -> Instruction:
    """
    Create the process_entry_payment instruction
    """
    print("\n🏗️  Creating process_entry_payment instruction...")
    
    # Calculate instruction discriminator
    discriminator_str = "global:process_entry_payment"
    discriminator = hashlib.sha256(discriminator_str.encode()).digest()[:8]
    
    # Pack instruction data: discriminator + entry_amount (u64) + user_wallet (32 bytes)
    instruction_data = discriminator + struct.pack('<Q', entry_amount) + bytes(user_wallet)
    
    # Define accounts (must match Anchor program's ProcessEntryPayment struct)
    accounts = [
        AccountMeta(pubkey=lottery_pda, is_signer=False, is_writable=True),
        AccountMeta(pubkey=user, is_signer=True, is_writable=True),
        # Add more accounts as needed (USDC token accounts, etc.)
    ]
    
    print(f"   Entry Amount: {entry_amount / 1_000_000} USDC")
    print(f"   User Wallet: {user_wallet}")
    
    return Instruction(
        program_id=PROGRAM_ID,
        data=instruction_data,
        accounts=accounts
    )


async def test_entry_payment(user_keypair_path: str):
    """Test a lottery entry payment"""
    print("=" * 60)
    print("Test Lottery Entry Payment")
    print("=" * 60)
    print(f"\nNetwork: Devnet")
    print(f"Program ID: {PROGRAM_ID}")
    print()
    
    # Load user keypair
    user = load_user_keypair(user_keypair_path)
    
    # Connect to Solana
    print(f"\n🌐 Connecting to Solana devnet...")
    client = AsyncClient(RPC_URL, commitment=Confirmed)
    
    try:
        # Check user balance
        balance_resp = await client.get_balance(user.pubkey())
        balance_sol = balance_resp.value / 1_000_000_000
        print(f"✅ User balance: {balance_sol} SOL")
        
        if balance_sol < 0.01:
            print("⚠️  Warning: Low SOL balance!")
        
        # Derive lottery PDA
        lottery_pda, bump = derive_lottery_pda(PROGRAM_ID)
        print(f"\n🎰 Lottery PDA: {lottery_pda}")
        
        # Check if lottery is initialized
        lottery_account = await client.get_account_info(lottery_pda, commitment=Confirmed)
        if lottery_account.value is None:
            print("\n❌ Lottery is not initialized yet!")
            print("Please run initialize_lottery.py first")
            return
        
        print(f"✅ Lottery account exists")
        
        # Create entry payment instruction
        entry_ix = create_entry_payment_instruction(
            user=user.pubkey(),
            lottery_pda=lottery_pda,
            entry_amount=ENTRY_AMOUNT,
            user_wallet=user.pubkey()
        )
        
        # Get recent blockhash
        print("\n📡 Fetching recent blockhash...")
        recent_blockhash_resp = await client.get_latest_blockhash()
        recent_blockhash = recent_blockhash_resp.value.blockhash
        
        # Create and sign transaction
        print("✍️  Creating and signing transaction...")
        transaction = Transaction.new_signed_with_payer(
            [entry_ix],
            user.pubkey(),
            [user],
            recent_blockhash
        )
        
        # Simulate transaction first
        print("\n🧪 Simulating transaction...")
        try:
            simulation = await client.simulate_transaction(transaction)
            if simulation.value.err:
                print(f"❌ Simulation failed: {simulation.value.err}")
                print(f"Logs: {simulation.value.logs}")
                return
            print("✅ Simulation successful!")
        except Exception as e:
            print(f"⚠️  Simulation error: {e}")
        
        # Send transaction
        print("\n🚀 Sending entry payment transaction...")
        tx_opts = TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
        signature = await client.send_transaction(transaction, opts=tx_opts)
        
        print(f"✅ Transaction sent!")
        print(f"   Signature: {signature.value}")
        print(f"\n⏳ Confirming transaction...")
        
        # Confirm transaction
        confirmation = await client.confirm_transaction(signature.value, commitment=Confirmed)
        
        if confirmation.value:
            print("\n" + "=" * 60)
            print("🎉 ENTRY PAYMENT SUCCESSFUL!")
            print("=" * 60)
            print(f"\nTransaction: {signature.value}")
            print(f"Entry Amount: {ENTRY_AMOUNT / 1_000_000} USDC")
            print(f"\n📊 View on Explorer:")
            print(f"https://explorer.solana.com/tx/{signature.value}?cluster=devnet")
            print()
        else:
            print("\n❌ Transaction failed to confirm")
    
    except Exception as e:
        print(f"\n❌ Error during entry payment: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Lottery Entry Payment")
    parser.add_argument(
        "--keypair",
        default="lottery-authority-devnet.json",
        help="Path to user keypair JSON file"
    )
    
    args = parser.parse_args()
    
    # Run test
    asyncio.run(test_entry_payment(args.keypair))

