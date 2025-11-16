# V3 Frontend Integration

This directory contains the V3 smart contract frontend integration.

## Files

- `paymentProcessor.ts` - V3 payment processor for frontend (raw instruction building)
- `paymentProcessor.test.ts` - Unit tests for payment processor
- `idl.json` - Contract IDL (generated from contract)

## Usage

### Basic Payment

```typescript
import { processV3EntryPayment, usdcToSmallestUnit } from "@/lib/v3/paymentProcessor";
import { useWallet, useConnection } from "@solana/wallet-adapter-react";

function V3PaymentButton() {
  const { connection } = useConnection();
  const { publicKey, signTransaction, connected } = useWallet();
  
  const handlePayment = async () => {
    if (!connected || !publicKey || !signTransaction) {
      alert("Please connect your wallet");
      return;
    }

    const entryAmount = usdcToSmallestUnit(10); // 10 USDC

    const result = await processV3EntryPayment(
      connection,
      publicKey,
      signTransaction,
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
      Pay 10 USDC
    </button>
  );
}
```

## Testing

Run tests with:

```bash
npm test -- src/lib/v3/paymentProcessor.test.ts
```

## Configuration

Environment variables:
- `NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V3` - V3 program ID (default: 52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov)
- `NEXT_PUBLIC_V3_USDC_MINT` - USDC mint address (default: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v)
- `NEXT_PUBLIC_V3_BUYBACK_WALLET` - USDC wallet that receives 40% of each entry for 100Bs buy-and-burn (falls back to `NEXT_PUBLIC_BUYBACK_WALLET_ADDRESS`).

## Differences from V2

- Uses different program ID
- Different PDA derivation (lottery vs global/bounty)
- Simplified account structure
- Enhanced security features (Ed25519, hashing, validation)
- 60/40 economics: 60% of each entry grows the jackpot pot, 40% funds the 100Bs buy-and-burn wallet.
