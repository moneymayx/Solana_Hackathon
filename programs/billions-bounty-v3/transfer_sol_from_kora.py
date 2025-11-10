#!/usr/bin/env python3
"""
Transfer SOL from Kora wallet to provider wallet on devnet.
This script uses the KORA_PRIVATE_KEY from environment variables.
"""
import os
import sys
from pathlib import Path

# Add project root to path to import from src
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.transaction import Transaction
    from solders.system_program import TransferParams, transfer
    try:
        from solana.rpc.async_api import AsyncClient
        from solana.rpc.api import Client
    except ImportError:
        from solana.rpc.api import Client
    from solana.rpc.commitment import Confirmed
    import base58
except ImportError as e:
    print(f"❌ Missing dependencies. Error: {e}")
    print(f"   Please install: pip3 install solana solders")
    sys.exit(1)

def load_kora_keypair():
    """Load Kora keypair from environment variable."""
    # Try to load from .env file first
    env_path = project_root / ".env"
    if env_path.exists():
        print(f"📖 Loading .env from {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('KORA_PRIVATE_KEY='):
                    private_key_base58 = line.split('=', 1)[1].strip()
                    # Remove quotes if present
                    private_key_base58 = private_key_base58.strip('"\'')
                    try:
                        keypair = Keypair.from_base58_string(private_key_base58)
                        return keypair
                    except Exception as e:
                        print(f"❌ Failed to parse KORA_PRIVATE_KEY: {e}")
                        sys.exit(1)
    
    # Fallback to environment variable
    private_key_base58 = os.getenv('KORA_PRIVATE_KEY')
    if not private_key_base58:
        print("❌ KORA_PRIVATE_KEY not found in .env file or environment")
        print("   Please add KORA_PRIVATE_KEY to your .env file")
        sys.exit(1)
    
    try:
        keypair = Keypair.from_base58_string(private_key_base58)
        return keypair
    except Exception as e:
        print(f"❌ Failed to parse KORA_PRIVATE_KEY: {e}")
        sys.exit(1)

def main():
    """Transfer SOL from Kora wallet to provider wallet."""
    # Wallet addresses
    kora_wallet = Pubkey.from_string("D4f9ArwgTuChKdgonTV8WFs3q1YtY9tHArF5zs4D5Vc5")
    provider_wallet = Pubkey.from_string("ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC")
    transfer_amount = 2.0  # SOL to transfer
    lamports = int(transfer_amount * 1_000_000_000)  # Convert to lamports
    
    # Load Kora keypair
    print("🔐 Loading Kora keypair...")
    kora_keypair = load_kora_keypair()
    kora_pubkey = kora_keypair.pubkey()
    
    # Verify the public key matches
    if str(kora_pubkey) != str(kora_wallet):
        print(f"⚠️  Warning: Loaded keypair public key ({kora_pubkey}) doesn't match expected ({kora_wallet})")
        print("   Continuing anyway...")
    
    # Connect to devnet
    print("🌐 Connecting to Solana devnet...")
    client = Client("https://api.devnet.solana.com")
    
    # Check balances
    print(f"💰 Checking balances...")
    kora_balance = client.get_balance(kora_pubkey, commitment=Confirmed).value
    provider_balance = client.get_balance(provider_wallet, commitment=Confirmed).value
    
    print(f"   Kora wallet ({kora_pubkey}): {kora_balance / 1_000_000_000:.9f} SOL")
    print(f"   Provider wallet ({provider_wallet}): {provider_balance / 1_000_000_000:.9f} SOL")
    
    # Adjust transfer amount if Kora wallet doesn't have enough (leave some for fees)
    fee_reserve = 0.01 * 1_000_000_000  # Reserve 0.01 SOL for fees
    max_transfer = max(0, kora_balance - fee_reserve)
    
    if max_transfer < lamports:
        print(f"⚠️  Kora wallet has insufficient balance for {transfer_amount} SOL transfer")
        print(f"   Have: {kora_balance / 1_000_000_000:.9f} SOL")
        print(f"   Can transfer: {max_transfer / 1_000_000_000:.9f} SOL (reserving {fee_reserve / 1_000_000_000:.9f} SOL for fees)")
        lamports = int(max_transfer)
        transfer_amount = max_transfer / 1_000_000_000
        
        if lamports <= 0:
            print(f"❌ Cannot transfer - insufficient balance")
            sys.exit(1)
        
        print(f"   Adjusting transfer to {transfer_amount:.9f} SOL")
    
    # Create transfer transaction
    print(f"\n📤 Transferring {transfer_amount} SOL from Kora wallet to provider wallet...")
    
    # Build transfer instruction
    transfer_ix = transfer(
        TransferParams(
            from_pubkey=kora_pubkey,
            to_pubkey=provider_wallet,
            lamports=lamports
        )
    )
    
    # Get recent blockhash and create transaction
    print("   Getting recent blockhash...")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.get_latest_blockhash(commitment=Confirmed)
            if response.value is None:
                raise Exception("Failed to get latest blockhash")
            
            # Create and sign transaction using new_signed_with_payer
            transaction = Transaction.new_signed_with_payer(
                [transfer_ix],
                kora_pubkey,
                [kora_keypair],
                response.value.blockhash
            )
            
            print("   Sending transaction...")
            # Use skip_preflight to avoid blockhash simulation issues
            from solana.rpc.types import TxOpts
            signature = client.send_transaction(
                transaction,
                opts=TxOpts(skip_preflight=True, preflight_commitment=Confirmed)
            ).value
            break  # Success, exit retry loop
        except Exception as e:
            if "Blockhash" in str(e) and attempt < max_retries - 1:
                print(f"   Blockhash issue (attempt {attempt + 1}/{max_retries}), retrying...")
                import time
                time.sleep(1)
                continue
            else:
                raise
    
    if signature:
        print(f"✅ Transaction sent! Signature: {signature}")
        print(f"   Waiting for confirmation...")
        
        # Wait for confirmation
        import time
        print("   Confirming transaction...")
        max_retries = 15
        for i in range(max_retries):
            time.sleep(2)
            # Use get_signature_statuses (plural) which takes an array
            statuses = client.get_signature_statuses([signature], search_transaction_history=True)
            if statuses.value and len(statuses.value) > 0:
                status = statuses.value[0]
                if status and status.err is None:
                    if hasattr(status, 'confirmation_status') and status.confirmation_status:
                        if status.confirmation_status.confirmed or status.confirmation_status.finalized:
                            print(f"✅ Transaction confirmed!")
                            
                            # Check new balances
                            new_kora_balance = client.get_balance(kora_pubkey, commitment=Confirmed).value
                            new_provider_balance = client.get_balance(provider_wallet, commitment=Confirmed).value
                            
                            print(f"\n💰 New balances:")
                            print(f"   Kora wallet: {new_kora_balance / 1_000_000_000:.9f} SOL")
                            print(f"   Provider wallet: {new_provider_balance / 1_000_000_000:.9f} SOL")
                            print(f"\n🔗 Explorer: https://explorer.solana.com/tx/{signature}?cluster=devnet")
                            return
                    elif status.err is None:
                        # Transaction succeeded (no error) but confirmation status not available
                        print(f"✅ Transaction processed!")
                        
                        # Check new balances
                        new_kora_balance = client.get_balance(kora_pubkey, commitment=Confirmed).value
                        new_provider_balance = client.get_balance(provider_wallet, commitment=Confirmed).value
                        
                        print(f"\n💰 New balances:")
                        print(f"   Kora wallet: {new_kora_balance / 1_000_000_000:.9f} SOL")
                        print(f"   Provider wallet: {new_provider_balance / 1_000_000_000:.9f} SOL")
                        print(f"\n🔗 Explorer: https://explorer.solana.com/tx/{signature}?cluster=devnet")
                        return
                elif status and status.err:
                    print(f"❌ Transaction failed: {status.err}")
                    sys.exit(1)
        
        print(f"⚠️  Transaction sent but confirmation timeout. Check manually:")
        print(f"   https://explorer.solana.com/tx/{signature}?cluster=devnet")
    else:
        print("❌ Failed to send transaction")
        sys.exit(1)

if __name__ == "__main__":
    main()

