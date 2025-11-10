"""
V3 Payment Router - Backend API for V3 contract payments
Allows testing V3 contract using backend's funded wallet
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from solana.rpc.commitment import Confirmed

# Import paths - main.py adds project root to sys.path
import sys
from pathlib import Path

# Ensure project root is in path (same as main.py does)
project_root = Path(__file__).parent.parent.parent.parent
project_root_str = str(project_root.resolve())
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

from src.services.contract_adapter_v3 import get_contract_adapter_v3, USE_CONTRACT_V3
from src.database import get_db
from src.models import V3EntryNonceTracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v3/payment", tags=["V3 Payment"])


class V3TestPaymentRequest(BaseModel):
    """Request to test V3 payment using backend's funded wallet"""
    user_wallet: str
    entry_amount: int  # Amount in smallest units (6 decimals)
    amount_usdc: float  # Amount in USDC (for display)
    entry_nonce: Optional[int] = None  # Optional client-provided nonce (backend will compute authoritative nonce)


@router.post("/test")
async def test_v3_payment(
    request: V3TestPaymentRequest,
    session: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Test V3 payment by calling contract using backend's funded wallet.
    
    This endpoint allows testing the V3 contract without requiring the user
    to have USDC. The backend uses its own funded wallet to pay on behalf
    of the user for testing purposes.
    
    NOTE: This is for TESTING ONLY. In production, users must sign and pay themselves.
    """
    if not USE_CONTRACT_V3:
        raise HTTPException(
            status_code=503,
            detail="V3 contract is not enabled. Set USE_CONTRACT_V3=true to enable."
        )
    
    try:
        logger.info(f"🧪 TEST V3 Payment Request: User {request.user_wallet}, Amount {request.amount_usdc} USDC")
        
        # Get V3 adapter
        adapter = get_contract_adapter_v3()
        if not adapter:
            raise HTTPException(
                status_code=500,
                detail="V3 contract adapter not available"
            )
        
        # For testing, we need to use backend's wallet to pay
        # Load backend wallet keypair
        backend_keypair_path = os.getenv(
            "BACKEND_WALLET_KEYPAIR_PATH",
            os.path.join(os.path.expanduser("~"), ".config", "solana", "id.json")
        )
        
        if not os.path.exists(backend_keypair_path):
            raise HTTPException(
                status_code=500,
                detail=f"Backend wallet keypair not found at {backend_keypair_path}. Needed for test payments."
            )
        
        # Import and load keypair
        from solders.keypair import Keypair
        import json
        
        with open(backend_keypair_path, 'r') as f:
            keypair_data = json.load(f)
        
        backend_keypair = Keypair.from_bytes(bytes(keypair_data))
        backend_wallet = backend_keypair.pubkey()
        
        logger.info(f"🔑 Using backend wallet for test payment: {backend_wallet}")
        
        # Build V3 payment transaction using raw instructions (similar to frontend)
        # This actually calls the contract on devnet using backend's funded wallet
        
        from solders.pubkey import Pubkey
        from solders.instruction import Instruction, AccountMeta
        from solders.transaction import Transaction
        from solders.rpc.responses import GetLatestBlockhashResp
        import hashlib
        import struct
        from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
        
        # Convert token program IDs to Pubkey objects
        token_program_id = Pubkey.from_string(str(TOKEN_PROGRAM_ID))
        associated_token_program_id = Pubkey.from_string(str(ASSOCIATED_TOKEN_PROGRAM_ID))
        
        # System program ID is a constant: "11111111111111111111111111111111"
        system_program_id = Pubkey.from_string("11111111111111111111111111111111")
        
        # Derive lottery PDA
        lottery_pda, lottery_bump = Pubkey.find_program_address(
            [b"lottery"],
            adapter.program_id
        )
        
        # Determine entry nonce for this user wallet (authoritative on backend)
        result = await session.execute(
            select(V3EntryNonceTracker).where(V3EntryNonceTracker.wallet_address == request.user_wallet)
        )
        nonce_record = result.scalars().first()
        
        if not nonce_record:
            nonce_record = V3EntryNonceTracker(
                wallet_address=request.user_wallet,
                current_nonce=0,
                updated_at=datetime.utcnow(),
            )
            session.add(nonce_record)
        
        expected_nonce = nonce_record.current_nonce + 1
        if request.entry_nonce is not None and request.entry_nonce != expected_nonce:
            logger.warning(
                "⚠️  Client-provided entry_nonce does not match backend expectation "
                f"(client={request.entry_nonce}, expected={expected_nonce}). Using backend value."
            )
        
        entry_nonce = expected_nonce
        nonce_record.current_nonce = entry_nonce
        nonce_record.updated_at = datetime.utcnow()
        
        # Derive entry PDA using nonce to support multiple entries per wallet
        user_wallet_pubkey = Pubkey.from_string(request.user_wallet)  # For instruction data
        entry_nonce_bytes = struct.pack("<Q", entry_nonce)
        entry_pda, entry_bump = Pubkey.find_program_address(
            [
                b"entry",
                bytes(lottery_pda),
                bytes(backend_wallet),  # Signer is backend wallet in test mode
                entry_nonce_bytes,
            ],
            adapter.program_id
        )
        
        # Check if entry already exists (contract uses 'init' which requires account to NOT exist)
        entry_account_info = await adapter.client.get_account_info(entry_pda)
        if entry_account_info.value:
            error_msg = (
                f"Entry already exists for backend wallet {backend_wallet} with nonce {entry_nonce}. "
                f"This should not happen under normal operation. Entry PDA: {entry_pda}."
            )
            logger.warning(f"⚠️  {error_msg}")
            await session.rollback()
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )
        
        # Get associated token accounts using PDA derivation
        # ATA derivation: find_program_address([owner_pubkey, TOKEN_PROGRAM_ID, mint_pubkey], ASSOCIATED_TOKEN_PROGRAM_ID)
        
        # Derive user token account ATA
        # Note: For test mode, we're using backend wallet to pay, but the entry
        # belongs to the user. However, the user_token_account constraint requires
        # associated_token::authority = user (the signer), so we need to use backend_wallet
        # for the token account since backend_wallet is the signer and payer.
        # BUT - wait, let me check the contract constraint again...
        # The contract has: associated_token::authority = user where user is the signer
        # So for testing, we use backend_wallet's token account
        user_token_account, _ = Pubkey.find_program_address(
            [
                bytes(backend_wallet),  # Backend wallet pays, so use its token account
                bytes(token_program_id),
                bytes(adapter.usdc_mint),
            ],
            associated_token_program_id
        )
        
        # IMPORTANT: The jackpot_token_account must be the ATA for the lottery PDA,
        # NOT the jackpot wallet. The contract constraint is: associated_token::authority = lottery
        # Derive jackpot token account ATA for lottery PDA
        jackpot_token_account, _ = Pubkey.find_program_address(
            [
                bytes(lottery_pda),
                bytes(token_program_id),
                bytes(adapter.usdc_mint),
            ],
            associated_token_program_id
        )
        
        # Check if the token account exists, if not we need to create it first
        # This is a one-time setup requirement
        token_account_info = await adapter.client.get_account_info(jackpot_token_account)
        if not token_account_info.value:
            logger.warning(f"⚠️  Lottery PDA token account does not exist: {jackpot_token_account}")
            logger.warning("   The token account needs to be created first.")
            logger.warning("   This should have been done during initialization.")
            logger.warning("   Creating the token account now...")
            
            # Get blockhash for create ATA transaction
            create_ata_blockhash_resp: GetLatestBlockhashResp = await adapter.client.get_latest_blockhash()
            
            # Create the associated token account for the lottery PDA
            # We need to use the Associated Token Program's create instruction
            from spl.token.instructions import create_associated_token_account
            
            create_ata_instruction = create_associated_token_account(
                payer=backend_wallet,
                owner=lottery_pda,
                mint=adapter.usdc_mint,
            )
            
            # Create transaction with create ATA instruction
            create_ata_tx = Transaction.new_signed_with_payer(
                [create_ata_instruction],
                backend_wallet,
                [backend_keypair],
                create_ata_blockhash_resp.value.blockhash
            )
            
            # Send and confirm the create ATA transaction
            create_ata_resp = await adapter.client.send_transaction(create_ata_tx)
            await adapter.client.confirm_transaction(create_ata_resp.value, commitment=Confirmed)
            logger.info(f"✅ Created lottery PDA token account: {jackpot_token_account}")
        
        # Build instruction discriminator: sha256("global:process_entry_payment")[:8]
        namespace = "global"
        instruction_name = "process_entry_payment"
        seed = f"{namespace}:{instruction_name}"
        discriminator = hashlib.sha256(seed.encode()).digest()[:8]
        
        # Serialize instruction data: discriminator + entry_amount (u64) + user_wallet (pubkey) + entry_nonce (u64)
        # The user_wallet in the instruction data should be the actual user from the request
        entry_amount_bytes = struct.pack("<Q", request.entry_amount)  # u64 little-endian
        user_wallet_bytes = bytes(user_wallet_pubkey)  # Use actual user wallet, not backend wallet
        
        instruction_data = bytes(discriminator) + entry_amount_bytes + user_wallet_bytes + entry_nonce_bytes
        
        # Build account keys (must match Rust struct ProcessEntryPayment exactly):
        # 1. lottery (PDA, mut)
        # 2. entry (PDA, init)
        # 3. user (Signer, mut) - backend_wallet
        # 4. user_wallet (UncheckedAccount, CHECK) - backend_wallet (same as user for now)
        # 5. user_token_account (Account, mut, associated_token)
        # 6. jackpot_token_account (Account, mut, associated_token)
        # 7. usdc_mint (UncheckedAccount, CHECK)
        # 8. token_program (Program)
        # 9. associated_token_program (Program)
        # 10. system_program (Program)
        account_keys = [
            AccountMeta(lottery_pda, is_signer=False, is_writable=True),  # 1. lottery
            AccountMeta(entry_pda, is_signer=False, is_writable=True),      # 2. entry
            AccountMeta(backend_wallet, is_signer=True, is_writable=True),  # 3. user (signer) - backend wallet
            AccountMeta(user_wallet_pubkey, is_signer=False, is_writable=False), # 4. user_wallet (CHECK - actual user from request)
            AccountMeta(user_token_account, is_signer=False, is_writable=True), # 5. user_token_account
            AccountMeta(jackpot_token_account, is_signer=False, is_writable=True), # 6. jackpot_token_account
            AccountMeta(adapter.usdc_mint, is_signer=False, is_writable=False), # 7. usdc_mint
            AccountMeta(token_program_id, is_signer=False, is_writable=False), # 8. token_program
            AccountMeta(associated_token_program_id, is_signer=False, is_writable=False), # 9. associated_token_program
            AccountMeta(system_program_id, is_signer=False, is_writable=False), # 10. system_program
        ]
        
        # Create instruction
        instruction = Instruction(
            program_id=adapter.program_id,
            accounts=account_keys,
            data=instruction_data,
        )
        
        # Get recent blockhash
        latest_blockhash_resp: GetLatestBlockhashResp = await adapter.client.get_latest_blockhash()
        latest_blockhash = latest_blockhash_resp.value.blockhash
        
        # Create and sign transaction
        # Note: Entry existence check is done above - if entry exists, we return error before here
        transaction = Transaction.new_signed_with_payer(
            [instruction],
            backend_wallet,  # Fee payer and signer
            [backend_keypair],
            latest_blockhash
        )
        
        # Send transaction
        send_resp = await adapter.client.send_transaction(transaction)
        signature = send_resp.value
        
        # Confirm transaction
        await adapter.client.confirm_transaction(signature, commitment=Confirmed)
        
        logger.info(f"✅ V3 test payment successful!")
        logger.info(f"   Signature: {signature}")
        logger.info(f"   Lottery PDA: {lottery_pda}")
        logger.info(f"   Entry PDA: {entry_pda}")
        logger.info(f"   Entry Nonce: {entry_nonce}")
        
        # Persist nonce update after successful on-chain execution
        await session.commit()
        
        cluster = "devnet" if "devnet" in adapter.rpc_endpoint else "mainnet-beta"
        return {
            "success": True,
            "transaction_signature": str(signature),
            "message": f"🧪 TEST: V3 contract executed using backend wallet. User {request.user_wallet} simulated.",
            "lottery_pda": str(lottery_pda),
            "entry_pda": str(entry_pda),
            "amount_usdc": request.amount_usdc,
            "is_test": True,
            "entry_nonce": entry_nonce,
            "explorer_url": f"https://explorer.solana.com/tx/{signature}?cluster={cluster}",
        }
            
    except HTTPException as http_exc:
        await session.rollback()
        raise http_exc
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"❌ Error in V3 test payment: {e}")
        logger.error(f"Full traceback:\n{error_traceback}")
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}. Check server logs for details."
        )

