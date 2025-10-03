#!/usr/bin/env python3
"""
Initialize Billions Bounty Lottery on Solana Devnet
This script initializes the lottery PDA with initial configuration
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
from solders.system_program import create_account, CreateAccountParams
from solders.transaction import Transaction
from solders.instruction import Instruction, AccountMeta
from solana.rpc.types import TxOpts
import struct

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration
PROGRAM_ID = Pubkey.from_string("DAgzfNPpc3i2EttgxfRtSN4SXQ4CwXQYjStmgrnw3BYh")
RPC_URL = "https://api.devnet.solana.com"
USDC_MINT_DEVNET = Pubkey.from_string("Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr")  # Devnet USDC

# Lottery parameters
RESEARCH_FUND_FLOOR = 1_000_000_000  # 1000 USDC (with 6 decimals)
RESEARCH_FEE = 10_000_000  # 10 USDC (with 6 decimals)


def load_authority_keypair(keypair_path: str) -> Keypair:
    """Load authority keypair from JSON file"""
    print(f"📂 Loading authority keypair from: {keypair_path}")
    
    with open(keypair_path, 'r') as f:
        keypair_data = json.load(f)
    
    # Handle both array and object format
    if isinstance(keypair_data, list):
        keypair_bytes = bytes(keypair_data)
    else:
        keypair_bytes = bytes(keypair_data['secretKey'])
    
    keypair = Keypair.from_bytes(keypair_bytes)
    print(f"✅ Authority loaded: {keypair.pubkey()}")
    return keypair


def derive_lottery_pda(program_id: Pubkey) -> tuple[Pubkey, int]:
    """Derive the lottery PDA address"""
    print("\n🔍 Deriving lottery PDA...")
    
    seeds = [b"lottery"]
    pda, bump = Pubkey.find_program_address(seeds, program_id)
    
    print(f"✅ Lottery PDA: {pda}")
    print(f"   Bump: {bump}")
    return pda, bump


async def check_lottery_exists(client: AsyncClient, lottery_pda: Pubkey) -> bool:
    """Check if lottery is already initialized"""
    print("\n🔍 Checking if lottery is already initialized...")
    
    try:
        account_info = await client.get_account_info(lottery_pda, commitment=Confirmed)
        
        if account_info.value is not None:
            print("⚠️  Lottery PDA already exists!")
            print(f"   Owner: {account_info.value.owner}")
            print(f"   Data length: {len(account_info.value.data)} bytes")
            return True
        else:
            print("✅ Lottery PDA does not exist - ready to initialize")
            return False
    except Exception as e:
        print(f"✅ Lottery not found (will be created): {e}")
        return False


def create_initialize_instruction(
    authority: Pubkey,
    lottery_pda: Pubkey,
    jackpot_wallet: Pubkey,
    research_fund_floor: int,
    research_fee: int
) -> Instruction:
    """
    Create the initialize_lottery instruction
    
    Instruction format for Anchor programs:
    - First 8 bytes: Instruction discriminator (hash of "global:initialize_lottery")
    - Followed by: instruction parameters
    """
    print("\n🏗️  Creating initialize_lottery instruction...")
    
    # Calculate instruction discriminator
    # For Anchor, this is the first 8 bytes of sha256("global:initialize_lottery")
    import hashlib
    discriminator_str = "global:initialize_lottery"
    discriminator = hashlib.sha256(discriminator_str.encode()).digest()[:8]
    
    # Pack instruction data: discriminator + research_fund_floor (u64) + research_fee (u64) + jackpot_wallet (32 bytes)
    instruction_data = discriminator + struct.pack('<QQ', research_fund_floor, research_fee) + bytes(jackpot_wallet)
    
    # Define accounts for initialize_lottery
    # Order must match the Anchor program's InitializeLottery struct
    accounts = [
        AccountMeta(pubkey=lottery_pda, is_signer=False, is_writable=True),
        AccountMeta(pubkey=authority, is_signer=True, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # System Program
    ]
    
    print(f"   Discriminator: {discriminator.hex()}")
    print(f"   Research Fund Floor: {research_fund_floor / 1_000_000} USDC")
    print(f"   Research Fee: {research_fee / 1_000_000} USDC")
    print(f"   Jackpot Wallet: {jackpot_wallet}")
    print(f"   Accounts: {len(accounts)}")
    
    return Instruction(
        program_id=PROGRAM_ID,
        data=instruction_data,
        accounts=accounts
    )


async def initialize_lottery(keypair_path: str, jackpot_wallet_address: str):
    """Initialize the lottery on devnet"""
    print("=" * 60)
    print("Billions Bounty - Lottery Initialization")
    print("=" * 60)
    print(f"\nNetwork: Devnet")
    print(f"Program ID: {PROGRAM_ID}")
    print()
    
    # Load authority keypair
    authority = load_authority_keypair(keypair_path)
    jackpot_wallet = Pubkey.from_string(jackpot_wallet_address)
    
    # Connect to Solana
    print(f"\n🌐 Connecting to Solana devnet...")
    client = AsyncClient(RPC_URL, commitment=Confirmed)
    
    try:
        # Check authority balance
        balance_resp = await client.get_balance(authority.pubkey())
        balance_sol = balance_resp.value / 1_000_000_000
        print(f"✅ Authority balance: {balance_sol} SOL")
        
        if balance_sol < 0.1:
            print("⚠️  Warning: Low balance! May need more SOL for initialization.")
        
        # Derive lottery PDA
        lottery_pda, bump = derive_lottery_pda(PROGRAM_ID)
        
        # Check if already initialized
        exists = await check_lottery_exists(client, lottery_pda)
        if exists:
            print("\n❌ Lottery is already initialized!")
            print(f"\nYou can view it at:")
            print(f"https://explorer.solana.com/address/{lottery_pda}?cluster=devnet")
            return
        
        # Create initialize instruction
        initialize_ix = create_initialize_instruction(
            authority=authority.pubkey(),
            lottery_pda=lottery_pda,
            jackpot_wallet=jackpot_wallet,
            research_fund_floor=RESEARCH_FUND_FLOOR,
            research_fee=RESEARCH_FEE
        )
        
        # Get recent blockhash
        print("\n📡 Fetching recent blockhash...")
        recent_blockhash_resp = await client.get_latest_blockhash()
        recent_blockhash = recent_blockhash_resp.value.blockhash
        
        # Create and sign transaction
        print("✍️  Creating and signing transaction...")
        transaction = Transaction.new_signed_with_payer(
            [initialize_ix],
            authority.pubkey(),
            [authority],
            recent_blockhash
        )
        
        # Send transaction
        print("\n🚀 Sending initialization transaction...")
        tx_opts = TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
        signature = await client.send_transaction(transaction, opts=tx_opts)
        
        print(f"✅ Transaction sent!")
        print(f"   Signature: {signature.value}")
        print(f"\n⏳ Confirming transaction...")
        
        # Confirm transaction
        confirmation = await client.confirm_transaction(signature.value, commitment=Confirmed)
        
        if confirmation.value:
            print("\n" + "=" * 60)
            print("🎉 LOTTERY INITIALIZED SUCCESSFULLY!")
            print("=" * 60)
            print(f"\nLottery PDA: {lottery_pda}")
            print(f"Authority: {authority.pubkey()}")
            print(f"Jackpot Wallet: {jackpot_wallet}")
            print(f"Research Fund Floor: {RESEARCH_FUND_FLOOR / 1_000_000} USDC")
            print(f"Entry Fee: {RESEARCH_FEE / 1_000_000} USDC")
            print(f"\n📊 View on Explorer:")
            print(f"https://explorer.solana.com/tx/{signature.value}?cluster=devnet")
            print(f"\n💾 Save this information:")
            print(f"LOTTERY_PDA={lottery_pda}")
            print(f"LOTTERY_BUMP={bump}")
            print()
        else:
            print("\n❌ Transaction failed to confirm")
    
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize Billions Bounty Lottery")
    parser.add_argument(
        "--keypair",
        default="lottery-authority-devnet.json",
        help="Path to authority keypair JSON file"
    )
    parser.add_argument(
        "--jackpot-wallet",
        required=True,
        help="Jackpot wallet public key (where initial funds go)"
    )
    
    args = parser.parse_args()
    
    # Run initialization
    asyncio.run(initialize_lottery(args.keypair, args.jackpot_wallet))

