#!/usr/bin/env python3
"""
Multi-Bounty Initialization Script
Initializes all 4 bounties with appropriate parameters for the V3 multi-bounty contract.

Bounty Configuration:
- Bounty 1 (Expert): $10,000 floor, $10 entry
- Bounty 2 (Hard): $5,000 floor, $5 entry
- Bounty 3 (Medium): $2,500 floor, $2.50 entry
- Bounty 4 (Easy): $500 floor, $0.50 entry

Usage:
    python3 scripts/initialize_multi_bounty.py [--network devnet|mainnet] [--bounty-id 1|2|3|4]
    
    If --bounty-id is not specified, initializes all 4 bounties.
"""
import os
import sys
import asyncio
import argparse
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from anchorpy import Program, Provider, Idl
from anchorpy.provider import Wallet
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bounty configurations
BOUNTY_CONFIGS = {
    1: {
        "name": "Claude Champ",
        "difficulty": "expert",
        "research_fund_floor_usd": 10_000.0,
        "research_fee_usd": 10.0,
    },
    2: {
        "name": "GPT Gigachad",
        "difficulty": "hard",
        "research_fund_floor_usd": 5_000.0,
        "research_fee_usd": 5.0,
    },
    3: {
        "name": "Gemini Great",
        "difficulty": "medium",
        "research_fund_floor_usd": 2_500.0,
        "research_fee_usd": 2.50,
    },
    4: {
        "name": "Llama Legend",
        "difficulty": "easy",
        "research_fund_floor_usd": 500.0,
        "research_fee_usd": 0.50,
    },
}

# USDC has 6 decimals
USDC_DECIMALS = 1_000_000


async def load_idl(project_root: Path) -> Idl:
    """
    Load the V3 program IDL and patch it with size fields (like TypeScript version).
    Based on scripts/initialize_v3_from_test.ts pattern.
    """
    idl_path = project_root / "target" / "idl" / "billions_bounty_v3.json"
    if not idl_path.exists():
        # Try alternative location
        idl_path = project_root / "programs" / "billions-bounty-v3" / "target" / "idl" / "billions_bounty_v3.json"
    
    if not idl_path.exists():
        raise FileNotFoundError(f"IDL not found at {idl_path}. Please build the contract first: anchor build")
    
    with open(idl_path, "r") as f:
        idl = json.load(f)
    
    # Patch IDL with size fields (defensive, like TypeScript version)
    if "accounts" in idl:
        for account in idl["accounts"]:
            if account.get("name") == "lottery":
                if "size" not in account:
                    account["size"] = 194
                if "type" in account and "size" not in account.get("type", {}):
                    account["type"]["size"] = 194
            elif account.get("name") == "entry":
                if "size" not in account:
                    account["size"] = 73
                if "type" in account and "size" not in account.get("type", {}):
                    account["type"]["size"] = 73
    
    if "types" in idl:
        for type_def in idl["types"]:
            if "type" in type_def and "size" not in type_def.get("type", {}):
                type_info = type_def.get("type", {})
                if "fields" in type_info:
                    # Calculate size from fields (8 byte discriminator + field sizes)
                    calc_size = 8  # discriminator
                    for field in type_info["fields"]:
                        field_type = field.get("type", "")
                        if field_type == "pubkey" or field_type == "publicKey":
                            calc_size += 32
                        elif field_type in ["u64", "i64"]:
                            calc_size += 8
                        elif field_type == "bool":
                            calc_size += 1
                        elif field_type == "u8":
                            calc_size += 1
                    type_info["size"] = calc_size
    
    # Convert dict to Idl object for anchorpy
    return Idl.from_json(json.dumps(idl))


def get_program_id(network: str) -> Pubkey:
    """Get program ID for the specified network."""
    if network == "mainnet":
        program_id_str = os.getenv("LOTTERY_PROGRAM_ID_V3_MAINNET", "")
    else:
        program_id_str = os.getenv(
            "LOTTERY_PROGRAM_ID_V3",
            "7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh"  # V3 Devnet (Multi-Bounty)
        )
    
    if not program_id_str:
        raise ValueError(f"Program ID not found for {network}. Set LOTTERY_PROGRAM_ID_V3 environment variable.")
    
    return Pubkey.from_string(program_id_str)


def get_rpc_endpoint(network: str) -> str:
    """Get RPC endpoint for the specified network."""
    if network == "mainnet":
        return os.getenv("SOLANA_RPC_ENDPOINT", "https://api.mainnet-beta.solana.com")
    else:
        return os.getenv("SOLANA_RPC_ENDPOINT", "https://api.devnet.solana.com")


def get_usdc_mint(network: str) -> Pubkey:
    """Get USDC mint address for the specified network."""
    if network == "mainnet":
        usdc_mint_str = os.getenv("USDC_MINT", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
    else:
        usdc_mint_str = os.getenv("V3_USDC_MINT", os.getenv("USDC_MINT", "JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh"))
    
    return Pubkey.from_string(usdc_mint_str)


async def initialize_bounty(
    program: Program,
    bounty_id: int,
    config: dict,
    authority_keypair: Keypair,
    jackpot_wallet: Pubkey,
    backend_authority: Pubkey,
    usdc_mint: Pubkey,
) -> dict:
    """
    Initialize a single bounty.
    
    Returns:
        Dictionary with initialization result
    """
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"Initializing Bounty {bounty_id}: {config['name']} ({config['difficulty']})")
        logger.info(f"{'='*60}")
        
        # Convert USD amounts to USDC units (6 decimals)
        research_fund_floor = int(config["research_fund_floor_usd"] * USDC_DECIMALS)
        research_fee = int(config["research_fee_usd"] * USDC_DECIMALS)
        
        logger.info(f"  Research Fund Floor: ${config['research_fund_floor_usd']:,.2f} ({research_fund_floor:,} USDC units)")
        logger.info(f"  Research Fee: ${config['research_fee_usd']:.2f} ({research_fee:,} USDC units)")
        
        # Derive lottery PDA for this bounty
        lottery_pda, lottery_bump = Pubkey.find_program_address(
            [b"lottery", bytes([bounty_id])],
            program.program_id
        )
        logger.info(f"  Lottery PDA: {lottery_pda}")
        logger.info(f"  Lottery Bump: {lottery_bump}")
        
        # Derive jackpot token account (ATA for lottery PDA)
        from anchorpy.utils.token import associated_address
        jackpot_token_account = associated_address(
            usdc_mint,
            lottery_pda
        )
        logger.info(f"  Jackpot Token Account: {jackpot_token_account}")
        
        # Check if lottery is already initialized
        account_info = await program.provider.connection.get_account_info(lottery_pda)
        if account_info.value is not None:
            logger.warning(f"  ⚠️  Bounty {bounty_id} already initialized! Skipping...")
            return {
                "success": True,
                "bounty_id": bounty_id,
                "already_initialized": True,
                "lottery_pda": str(lottery_pda),
            }
        
        # Build initialization instruction
        method = program.methods.initialize_lottery(
            bounty_id,
            research_fund_floor,
            research_fee,
            jackpot_wallet,
            backend_authority,
        ).accounts({
            "lottery": lottery_pda,
            "authority": authority_keypair.pubkey(),
            "jackpot_wallet": jackpot_wallet,
            "jackpot_token_account": jackpot_token_account,
            "usdc_mint": usdc_mint,
            "token_program": Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
            "associated_token_program": Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"),
            "system_program": Pubkey.from_string("11111111111111111111111111111111"),
        })
        
        # Simulate first to check for errors
        logger.info("  📋 Simulating transaction...")
        try:
            sim_result = await method.simulate()
            if sim_result.value.err:
                logger.error(f"  ❌ Simulation failed: {sim_result.value.err}")
                return {
                    "success": False,
                    "bounty_id": bounty_id,
                    "error": f"Simulation failed: {sim_result.value.err}",
                }
            logger.info("  ✅ Simulation successful")
        except Exception as e:
            logger.error(f"  ❌ Simulation error: {e}")
            return {
                "success": False,
                "bounty_id": bounty_id,
                "error": f"Simulation error: {str(e)}",
            }
        
        # Send transaction
        logger.info("  📤 Sending initialization transaction...")
        tx_sig = await method.rpc()
        logger.info(f"  ✅ Transaction sent: {tx_sig}")
        logger.info(f"  🔗 Explorer: https://explorer.solana.com/tx/{tx_sig}?cluster={program.provider.connection._commitment}")
        
        return {
            "success": True,
            "bounty_id": bounty_id,
            "name": config["name"],
            "difficulty": config["difficulty"],
            "lottery_pda": str(lottery_pda),
            "transaction_signature": str(tx_sig),
            "research_fund_floor_usd": config["research_fund_floor_usd"],
            "research_fee_usd": config["research_fee_usd"],
        }
        
    except Exception as e:
        logger.error(f"  ❌ Error initializing bounty {bounty_id}: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "bounty_id": bounty_id,
            "error": str(e),
        }


async def main():
    parser = argparse.ArgumentParser(description="Initialize multi-bounty V3 smart contract")
    parser.add_argument(
        "--network",
        choices=["devnet", "mainnet"],
        default="devnet",
        help="Network to deploy to (default: devnet)"
    )
    parser.add_argument(
        "--bounty-id",
        type=int,
        choices=[1, 2, 3, 4],
        help="Initialize specific bounty only (1=Expert, 2=Hard, 3=Medium, 4=Easy). If not specified, initializes all."
    )
    parser.add_argument(
        "--authority-keypair",
        type=str,
        help="Path to authority keypair file (default: ~/.config/solana/id.json)"
    )
    parser.add_argument(
        "--jackpot-wallet",
        type=str,
        help="Jackpot wallet address (default: authority wallet)"
    )
    parser.add_argument(
        "--backend-authority",
        type=str,
        help="Backend authority address for AI decision signing (default: authority wallet)"
    )
    
    args = parser.parse_args()
    
    # Load IDL
    logger.info("Loading IDL...")
    idl = await load_idl(project_root)
    
    # Get program ID and RPC endpoint
    program_id = get_program_id(args.network)
    rpc_endpoint = get_rpc_endpoint(args.network)
    usdc_mint = get_usdc_mint(args.network)
    
    logger.info(f"Program ID: {program_id}")
    logger.info(f"Network: {args.network}")
    logger.info(f"RPC Endpoint: {rpc_endpoint}")
    logger.info(f"USDC Mint: {usdc_mint}")
    
    # Load authority keypair
    if args.authority_keypair:
        keypair_path = Path(args.authority_keypair).expanduser()
    else:
        keypair_path = Path.home() / ".config" / "solana" / "id.json"
    
    if not keypair_path.exists():
        raise FileNotFoundError(f"Keypair not found at {keypair_path}. Please specify --authority-keypair or set up Solana CLI.")
    
    with open(keypair_path, "r") as f:
        keypair_data = json.load(f)
        authority_keypair = Keypair.from_bytes(bytes(keypair_data))
    
    logger.info(f"Authority: {authority_keypair.pubkey()}")
    
    # Set up wallet and provider
    wallet = Wallet(authority_keypair)
    connection = AsyncClient(rpc_endpoint, commitment=Confirmed)
    provider = Provider(connection, wallet)
    program = Program(idl, program_id, provider)
    
    # Get jackpot wallet and backend authority
    if args.jackpot_wallet:
        jackpot_wallet = Pubkey.from_string(args.jackpot_wallet)
    else:
        jackpot_wallet = authority_keypair.pubkey()
    
    if args.backend_authority:
        backend_authority = Pubkey.from_string(args.backend_authority)
    else:
        backend_authority = authority_keypair.pubkey()
    
    logger.info(f"Jackpot Wallet: {jackpot_wallet}")
    logger.info(f"Backend Authority: {backend_authority}")
    
    # Determine which bounties to initialize
    if args.bounty_id:
        bounties_to_init = {args.bounty_id: BOUNTY_CONFIGS[args.bounty_id]}
    else:
        bounties_to_init = BOUNTY_CONFIGS
    
    # Initialize bounties
    results = []
    for bounty_id, config in bounties_to_init.items():
        result = await initialize_bounty(
            program,
            bounty_id,
            config,
            authority_keypair,
            jackpot_wallet,
            backend_authority,
            usdc_mint,
        )
        results.append(result)
        
        # Small delay between initializations
        if len(bounties_to_init) > 1:
            await asyncio.sleep(2)
    
    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("Initialization Summary")
    logger.info(f"{'='*60}")
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    already_init = [r for r in results if r.get("already_initialized")]
    
    for result in results:
        if result.get("success"):
            if result.get("already_initialized"):
                logger.info(f"✅ Bounty {result['bounty_id']}: Already initialized")
            else:
                logger.info(f"✅ Bounty {result['bounty_id']} ({result.get('name', 'N/A')}): Initialized")
                logger.info(f"   PDA: {result.get('lottery_pda', 'N/A')}")
                logger.info(f"   TX: {result.get('transaction_signature', 'N/A')}")
        else:
            logger.error(f"❌ Bounty {result['bounty_id']}: Failed - {result.get('error', 'Unknown error')}")
    
    logger.info(f"\nTotal: {len(successful)} successful, {len(failed)} failed, {len(already_init)} already initialized")
    
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

