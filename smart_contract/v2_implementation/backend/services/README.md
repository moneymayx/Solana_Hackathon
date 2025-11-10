# V2 Contract Integration Guide

This directory contains the V2 smart contract integration code using raw Solana instructions.

## Files

- `payment_processor.py` - Backend payment processor using solana-py
- `contract_service.py` - Higher-level contract service wrapper (placeholder)

## Backend Integration

### Basic Usage

```python
from src.services.v2.payment_processor import V2PaymentProcessor, get_v2_payment_processor
from solders.keypair import Keypair
import asyncio

# Get processor instance
processor = get_v2_payment_processor()

# Process payment
# Note: In production, you'd get the user's keypair from their wallet connection
user_keypair = Keypair()  # This would come from user's wallet

result = await processor.process_entry_payment(
    user_keypair=user_keypair,
    bounty_id=1,
    entry_amount=15_000_000,  # 15 USDC (6 decimals)
)

if result["success"]:
    print(f"Transaction: {result['transaction_signature']}")
    print(f"Explorer: {result['explorer_url']}")
else:
    print(f"Error: {result['error']}")
```

### API Endpoint Example

```python
from fastapi import APIRouter, Depends
from src.services.v2.payment_processor import get_v2_payment_processor

router = APIRouter()

@router.post("/api/v2/payment/process")
async def process_v2_payment(
    user_wallet: str,
    bounty_id: int,
    entry_amount: int,
):
    """Process V2 entry payment."""
    processor = get_v2_payment_processor()
    
    # Get user's keypair from wallet (implementation depends on your auth system)
    # user_keypair = get_user_keypair(user_wallet)
    
    result = await processor.process_entry_payment(
        user_keypair=user_keypair,
        bounty_id=bounty_id,
        entry_amount=entry_amount,
    )
    
    return result
```

## Configuration

All configuration comes from environment variables:

- `LOTTERY_PROGRAM_ID_V2` - V2 program ID
- `V2_USDC_MINT` - USDC mint address
- `V2_BOUNTY_POOL_WALLET` - Bounty pool wallet
- `V2_OPERATIONAL_WALLET` - Operational wallet
- `V2_BUYBACK_WALLET` - Buyback wallet
- `V2_STAKING_WALLET` - Staking wallet
- `SOLANA_RPC_ENDPOINT` - Solana RPC URL

## Testing

See `programs/billions-bounty-v2/scripts/test_v2_raw_payment.ts` for reference implementation in TypeScript.



