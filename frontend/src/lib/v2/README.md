# V2 Frontend Integration Guide

This directory contains the V2 smart contract frontend integration using `@solana/web3.js`.

## Files

- `paymentProcessor.ts` - V2 payment processor for frontend

## Frontend Integration

### React Component Example

```typescript
import { useWallet } from "@solana/wallet-adapter-react";
import { Connection } from "@solana/web3.js";
import { processV2EntryPayment, usdcToSmallestUnit } from "@/lib/v2/paymentProcessor";

function PaymentButton() {
  const { publicKey, signTransaction } = useWallet();
  const connection = new Connection("https://api.devnet.solana.com");

  const handlePayment = async () => {
    if (!publicKey || !signTransaction) {
      alert("Please connect your wallet");
      return;
    }

    const entryAmount = usdcToSmallestUnit(15); // 15 USDC

    const result = await processV2EntryPayment(
      connection,
      publicKey,
      signTransaction,
      1, // bounty_id
      entryAmount
    );

    if (result.success) {
      console.log("Payment successful!", result.transactionSignature);
      window.open(result.explorerUrl, "_blank");
    } else {
      alert(`Payment failed: ${result.error}`);
    }
  };

  return (
    <button onClick={handlePayment}>
      Pay 15 USDC
    </button>
  );
}
```

### With Wallet Adapter

```typescript
import { useConnection, useWallet } from "@solana/wallet-adapter-react";
import { processV2EntryPayment, usdcToSmallestUnit } from "@/lib/v2/paymentProcessor";

function V2PaymentForm() {
  const { connection } = useConnection();
  const { publicKey, signTransaction } = useWallet();

  const handleSubmit = async (amount: number) => {
    if (!publicKey || !signTransaction) return;

    const result = await processV2EntryPayment(
      connection,
      publicKey,
      async (tx) => {
        // Wallet adapter's signTransaction
        return await signTransaction(tx);
      },
      1, // bounty_id
      usdcToSmallestUnit(amount)
    );

    return result;
  };

  // ... rest of component
}
```

## Environment Variables

Set these in your `.env.local` or Vercel:

```bash
NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V2=HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm
NEXT_PUBLIC_V2_USDC_MINT=JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh
NEXT_PUBLIC_V2_BOUNTY_POOL_WALLET=CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF
NEXT_PUBLIC_V2_OPERATIONAL_WALLET=46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D
NEXT_PUBLIC_V2_BUYBACK_WALLET=7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya
NEXT_PUBLIC_V2_STAKING_WALLET=Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX
```

## Helper Functions

- `usdcToSmallestUnit(amount: number)` - Convert USDC to smallest unit (6 decimals)
- `smallestUnitToUsdc(amount: number)` - Convert smallest unit to USDC
- `getV2BountyStatus(connection, bountyId)` - Get bounty status

## Testing

See `programs/billions-bounty-v2/scripts/test_v2_raw_payment.ts` for reference implementation.



