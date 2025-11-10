# V2 Contract Integration - Complete Guide

**Date**: October 31, 2025  
**Status**: ✅ **READY FOR INTEGRATION**

---

## 🎉 Integration Files Created

### Backend (Python)
- ✅ `src/services/v2/payment_processor.py` - Raw instruction-based payment processor
- ✅ `src/services/v2/README.md` - Backend integration documentation

### Frontend (TypeScript/React)
- ✅ `frontend/src/lib/v2/paymentProcessor.ts` - Raw instruction-based payment processor
- ✅ `frontend/src/lib/v2/README.md` - Frontend integration documentation

---

## 📋 Backend Integration

### Quick Start

The backend integration is ready to use. Here's how to integrate it:

#### 1. Import the Payment Processor

```python
from src.services.v2.payment_processor import get_v2_payment_processor
```

#### 2. Process a Payment

```python
processor = get_v2_payment_processor()

result = await processor.process_entry_payment(
    user_keypair=user_keypair,  # From user's wallet
    bounty_id=1,
    entry_amount=15_000_000,  # 15 USDC (6 decimals)
)

if result["success"]:
    print(f"Transaction: {result['transaction_signature']}")
else:
    print(f"Error: {result['error']}")
```

### API Endpoint Integration

Add this to your FastAPI router:

```python
from fastapi import APIRouter, Depends
from src.services.v2.payment_processor import get_v2_payment_processor
from solders.keypair import Keypair
from solders.pubkey import Pubkey

router = APIRouter()

@router.post("/api/v2/payment/process")
async def process_v2_payment(
    user_wallet_address: str,
    bounty_id: int = 1,
    entry_amount_usdc: float = 15.0,
):
    """
    Process V2 entry payment.
    
    Args:
        user_wallet_address: User's wallet address
        bounty_id: Bounty ID (default: 1)
        entry_amount_usdc: Payment amount in USDC (default: 15.0)
    """
    processor = get_v2_payment_processor()
    
    # Convert USDC to smallest unit (6 decimals)
    entry_amount = int(entry_amount_usdc * 1_000_000)
    
    # Note: In production, you'd need to get the user's keypair
    # This depends on your authentication system
    # For now, this is a placeholder
    # user_keypair = await get_user_keypair(user_wallet_address)
    
    # result = await processor.process_entry_payment(
    #     user_keypair=user_keypair,
    #     bounty_id=bounty_id,
    #     entry_amount=entry_amount,
    # )
    
    return {
        "message": "Integration ready - implement user keypair retrieval",
        "processor_initialized": True,
    }
```

### Configuration

The processor automatically reads from environment variables:
- `LOTTERY_PROGRAM_ID_V2`
- `V2_USDC_MINT`
- `V2_BOUNTY_POOL_WALLET`
- `V2_OPERATIONAL_WALLET`
- `V2_BUYBACK_WALLET`
- `V2_STAKING_WALLET`
- `SOLANA_RPC_ENDPOINT`

All set in your `.env` file! ✅

---

## 🎨 Frontend Integration

### Quick Start

The frontend integration is ready to use with wallet adapters:

#### 1. Import the Payment Processor

```typescript
import { processV2EntryPayment, usdcToSmallestUnit } from "@/lib/v2/paymentProcessor";
```

#### 2. Use with Wallet Adapter

```typescript
import { useConnection, useWallet } from "@solana/wallet-adapter-react";
import { processV2EntryPayment, usdcToSmallestUnit } from "@/lib/v2/paymentProcessor";

function PaymentButton() {
  const { connection } = useConnection();
  const { publicKey, signTransaction } = useWallet();

  const handlePayment = async () => {
    if (!publicKey || !signTransaction) {
      alert("Please connect your wallet");
      return;
    }

    const result = await processV2EntryPayment(
      connection,
      publicKey,
      signTransaction, // Wallet adapter's sign function
      1, // bounty_id
      usdcToSmallestUnit(15) // 15 USDC
    );

    if (result.success) {
      console.log("✅ Payment successful!", result.transactionSignature);
      // Open explorer
      window.open(result.explorerUrl, "_blank");
    } else {
      alert(`❌ Payment failed: ${result.error}`);
    }
  };

  return <button onClick={handlePayment}>Pay 15 USDC</button>;
}
```

### Environment Variables

Add to `.env.local` or Vercel:

```bash
NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V2=HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm
NEXT_PUBLIC_V2_USDC_MINT=JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh
NEXT_PUBLIC_V2_BOUNTY_POOL_WALLET=CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF
NEXT_PUBLIC_V2_OPERATIONAL_WALLET=46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D
NEXT_PUBLIC_V2_BUYBACK_WALLET=7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya
NEXT_PUBLIC_V2_STAKING_WALLET=Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX
```

### Helper Functions

```typescript
// Convert USDC to smallest unit (6 decimals)
const amount = usdcToSmallestUnit(15); // 15_000_000

// Convert smallest unit to USDC
const usdc = smallestUnitToUsdc(15_000_000); // 15.0

// Get bounty status
const status = await getV2BountyStatus(connection, 1);
```

---

## 🔧 Key Implementation Details

### Raw Instructions Approach

Both backend and frontend use **raw Solana instructions** instead of Anchor's client library. This is because:

1. ✅ **Reliability**: Anchor client has account ordering issues
2. ✅ **Control**: Direct control over instruction building
3. ✅ **Compatibility**: Works consistently across environments

### Instruction Discriminator

The discriminator is derived using:
```python
# Python
sha256("global:process_entry_payment_v2")[:8]

# TypeScript
sha256("global:process_entry_payment_v2").slice(0, 8)
```

### Account Order

The account order **must match** the contract exactly:
1. Global PDA
2. Bounty PDA
3. Buyback Tracker PDA
4. User (signer)
5. User Token Account
6. Destination Token Accounts (4x)
7. Wallet Addresses (4x, read-only)
8. Program IDs (mint, token program, etc.)

See `test_v2_raw_payment.ts` for the exact order.

---

## 📝 Next Steps

### Backend

1. **Create API Endpoint**
   - Add endpoint for V2 payments
   - Integrate with your authentication system
   - Handle user keypair retrieval

2. **Update Existing Endpoints**
   - Modify existing payment endpoints to use V2 when enabled
   - Check `USE_CONTRACT_V2` environment variable

3. **Testing**
   - Test with devnet
   - Verify 4-way split (60/20/10/10)
   - Check price escalation

### Frontend

1. **Create Payment Component**
   - Build React component using `processV2EntryPayment`
   - Integrate with wallet adapter
   - Add error handling and loading states

2. **Update Existing Payment Flow**
   - Modify existing payment UI to use V2
   - Check `NEXT_PUBLIC_USE_CONTRACT_V2` flag

3. **Testing**
   - Test with devnet
   - Verify transaction on explorer
   - Check wallet balances

---

## 🔍 Reference Implementation

The TypeScript test script serves as the reference:
- `programs/billions-bounty-v2/scripts/test_v2_raw_payment.ts`

This script has been tested and verified to work correctly. Both backend and frontend implementations follow this pattern.

---

## ✅ Status

- ✅ Backend payment processor implemented
- ✅ Frontend payment processor implemented
- ✅ Documentation created
- ✅ Ready for API endpoint integration
- ✅ Ready for React component integration

**The integration code is complete and ready to use!** 🎉

---

## 🚀 Quick Test

### Backend Test

```python
from src.services.v2.payment_processor import get_v2_payment_processor

processor = get_v2_payment_processor()
# processor is ready to use!
print(f"Program ID: {processor.program_id}")
```

### Frontend Test

```typescript
import { getV2BountyStatus } from "@/lib/v2/paymentProcessor";
import { Connection } from "@solana/web3.js";

const connection = new Connection("https://api.devnet.solana.com");
const status = await getV2BountyStatus(connection, 1);
console.log(status);
```

---

**Integration files are ready for use!** 🎉



