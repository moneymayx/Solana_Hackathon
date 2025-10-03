#!/usr/bin/env python3
"""
Initialize Billions Bounty Lottery on Solana Devnet - CORRECTED VERSION
This script uses the correct authority that owns the deployed program
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
PROGRAM_ID = Pubkey.from_string("4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK")
RPC_URL = "https://api.devnet.solana.com"
USDC_MINT_DEVNET = Pubkey.from_string("Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr")  # Devnet USDC

# Lottery parameters
RESEARCH_FUND_FLOOR = 1_000_000_000  # 1000 USDC (with 6 decimals)
RESEARCH_FEE = 10_000_000  # 10 USDC (with 6 decimals)


def load_default_keypair() -> Keypair:
    """Load the default Solana keypair (ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC)"""
    print(f"📂 Loading default keypair from: ~/.config/solana/id.json")
    
    keypair_path = os.path.expanduser("~/.config/solana/id.json")
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


def create_initialize_instruction_v2(
    authority: Pubkey,
    lottery_pda: Pubkey,
    jackpot_wallet: Pubkey,
    research_fund_floor: int,
    research_fee: int
) -> Instruction:
    """
    Create the initialize_lottery instruction using correct Anchor format
    """
    print("\n🏗️  Creating initialize_lottery instruction (v2)...")
    
    # Calculate instruction discriminator - Anchor uses namespace:method format
    import hashlib
    discriminator_str = "global:initialize_lottery"
    discriminator = hashlib.sha256(discriminator_str.encode()).digest()[:8]
    
    # Pack instruction data: discriminator + research_fund_floor (u64) + research_fee (u64) + jackpot_wallet (32 bytes)
    instruction_data = discriminator + struct.pack('<QQ', research_fund_floor, research_fee) + bytes(jackpot_wallet)
    
    # Define accounts for initialize_lottery - CORRECT ORDER for Anchor
    # Based on the smart contract's InitializeLottery struct:
    # 1. lottery (PDA, writable, not signer)
    # 2. authority (signer, writable)
    # 3. jackpot_wallet (unchecked account, not signer, not writable)
    # 4. system_program (program, not signer, not writable)
    accounts = [
        AccountMeta(pubkey=lottery_pda, is_signer=False, is_writable=True),  # lottery
        AccountMeta(pubkey=authority, is_signer=True, is_writable=True),      # authority
        AccountMeta(pubkey=jackpot_wallet, is_signer=False, is_writable=False),  # jackpot_wallet
        AccountMeta(pubkey=Pubkey.from_string("11111111111111111111111111111111"), is_signer=False, is_writable=False),  # system_program
    ]
    
    print(f"   Discriminator: {discriminator.hex()}")
    print(f"   Research Fund Floor: {research_fund_floor / 1_000_000} USDC")
    print(f"   Research Fee: {research_fee / 1_000_000} USDC")
    print(f"   Jackpot Wallet: {jackpot_wallet}")
    print(f"   Accounts: {len(accounts)}")
    for i, acc in enumerate(accounts):
        print(f"     {i}: {acc.pubkey} (signer={acc.is_signer}, writable={acc.is_writable})")
    
    return Instruction(
        program_id=PROGRAM_ID,
        data=instruction_data,
        accounts=accounts
    )


async def initialize_lottery_correct():
    """Initialize the lottery on devnet using the correct authority"""
    print("=" * 60)
    print("Billions Bounty - Lottery Initialization (CORRECTED)")
    print("=" * 60)
    print(f"\nNetwork: Devnet")
    print(f"Program ID: {PROGRAM_ID}")
    print()
    
    # Load the correct authority (the one that owns the deployed program)
    authority = load_default_keypair()
    jackpot_wallet = derive_lottery_pda(PROGRAM_ID)[0]  # Use PDA as jackpot wallet
    
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
        initialize_ix = create_initialize_instruction_v2(
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
    # Run initialization
    asyncio.run(initialize_lottery_correct())
