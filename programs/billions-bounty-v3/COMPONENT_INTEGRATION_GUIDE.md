# V3 Component Integration Guide

## What is Component Integration?

Component integration means creating **React UI components** that use the V3 payment processor to allow users to interact with the smart contract through a graphical interface. Instead of calling the payment processor directly in code, users interact with buttons, forms, and modals.

## Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  V3PaymentButton / V3PaymentModal              │  │
│  │  - Amount input                                  │  │
│  │  - Payment button                                │  │
│  │  - Loading states                                │  │
│  │  - Error handling                                │  │
│  └──────────────┬───────────────────────────────────┘  │
│                 │                                          │
│                 ▼                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Wallet Adapter (useWallet, useConnection)       │  │
│  │  - Connection to Solana network                  │  │
│  │  - User's wallet (publicKey, signTransaction)    │  │
│  │  - Wallet connection state                       │  │
│  └──────────────┬───────────────────────────────────┘  │
│                 │                                          │
│                 ▼                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  V3 Payment Processor (paymentProcessor.ts)     │  │
│  │  - processV3EntryPayment()                       │  │
│  │  - Transaction building                         │  │
│  │  - PDA derivation                               │  │
│  └──────────────┬───────────────────────────────────┘  │
│                 │                                          │
│                 ▼                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Solana Blockchain                                │  │
│  │  - Transaction execution                         │  │
│  │  - Smart contract                                │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Component Structure

### 1. **V3PaymentButton Component**

A simple button component for quick payments:

```typescript
// frontend/src/components/V3PaymentButton.tsx
"use client";

import { useState } from "react";
import { useConnection, useWallet } from "@solana/wallet-adapter-react";
import {
  processV3EntryPayment,
  usdcToSmallestUnit,
} from "@/lib/v3/paymentProcessor";

interface V3PaymentButtonProps {
  defaultAmount?: number; // Default amount in USDC
  onSuccess?: (signature: string, explorerUrl: string) => void;
  onError?: (error: string) => void;
}

export default function V3PaymentButton({
  defaultAmount = 10,
  onSuccess,
  onError,
}: V3PaymentButtonProps) {
  const { connection } = useConnection();
  const { publicKey, signTransaction, connected } = useWallet();
  const [amount, setAmount] = useState(defaultAmount);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePayment = async () => {
    if (!connected || !publicKey || !signTransaction) {
      setError("Please connect your wallet");
      onError?.("Wallet not connected");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const entryAmount = usdcToSmallestUnit(amount);

      const result = await processV3EntryPayment(
        connection,
        publicKey,
        signTransaction,
        entryAmount
      );

      if (result.success && result.transactionSignature) {
        onSuccess?.(result.transactionSignature, result.explorerUrl || "");
      } else {
        const errorMsg = result.error || "Payment failed";
        setError(errorMsg);
        onError?.(errorMsg);
      }
    } catch (err: any) {
      const errorMsg = err.message || String(err);
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="v3-payment-button space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2">
          Payment Amount (USDC)
        </label>
        <input
          type="number"
          min="1"
          step="0.1"
          value={amount}
          onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
          disabled={loading || !connected}
          className="w-full px-4 py-2 border rounded-lg disabled:bg-gray-100"
        />
      </div>

      {error && (
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <button
        onClick={handlePayment}
        disabled={loading || !connected || amount <= 0}
        className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium disabled:bg-gray-400 disabled:cursor-not-allowed hover:bg-blue-700"
      >
        {loading
          ? "Processing..."
          : !connected
          ? "Connect Wallet"
          : `Pay ${amount} USDC`}
      </button>
    </div>
  );
}
```

### 2. **V3PaymentModal Component**

A modal dialog for more complex payment flows:

```typescript
// frontend/src/components/V3PaymentModal.tsx
"use client";

import { useState } from "react";
import { useConnection, useWallet } from "@solana/wallet-adapter-react";
import { X, ExternalLink, Loader2 } from "lucide-react";
import {
  processV3EntryPayment,
  usdcToSmallestUnit,
  getV3LotteryStatus,
} from "@/lib/v3/paymentProcessor";

interface V3PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (signature: string) => void;
  defaultAmount?: number;
}

export default function V3PaymentModal({
  isOpen,
  onClose,
  onSuccess,
  defaultAmount = 10,
}: V3PaymentModalProps) {
  const { connection } = useConnection();
  const { publicKey, signTransaction, connected } = useWallet();
  const [amount, setAmount] = useState(defaultAmount);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{
    signature: string;
    explorerUrl: string;
  } | null>(null);

  const handlePayment = async () => {
    // ... same payment logic as V3PaymentButton
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Make Payment</h2>
          <button onClick={onClose}>
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Payment form */}
        {/* Success state */}
        {/* Error state */}
      </div>
    </div>
  );
}
```

### 3. **Integration with Existing Components**

Example: Integrating V3 into `BountyChatInterface`:

```typescript
// frontend/src/components/BountyChatInterface.tsx
import { useState } from "react";
import V3PaymentButton from "@/components/V3PaymentButton";
import { useWallet } from "@solana/wallet-adapter-react";

export default function BountyChatInterface() {
  const { connected } = useWallet();
  const [showPayment, setShowPayment] = useState(false);

  const handlePaymentSuccess = (signature: string, explorerUrl: string) => {
    console.log("Payment successful!", signature);
    // Open explorer in new tab
    window.open(explorerUrl, "_blank");
    // Continue chat flow
    setShowPayment(false);
  };

  return (
    <div>
      {/* Chat interface */}
      
      {showPayment && (
        <V3PaymentButton
          defaultAmount={10}
          onSuccess={handlePaymentSuccess}
          onError={(error) => console.error("Payment failed:", error)}
        />
      )}
    </div>
  );
}
```

## Key Integration Points

### 1. **Wallet Adapter Hooks**

```typescript
import { useConnection, useWallet } from "@solana/wallet-adapter-react";

// Get Solana connection
const { connection } = useConnection();

// Get wallet state and functions
const { 
  publicKey,           // User's wallet address
  signTransaction,     // Function to sign transactions
  connected,           // Whether wallet is connected
  connect,             // Function to connect wallet
  disconnect           // Function to disconnect
} = useWallet();
```

### 2. **Payment Processor Integration**

```typescript
import {
  processV3EntryPayment,
  usdcToSmallestUnit,
  getV3LotteryStatus,
} from "@/lib/v3/paymentProcessor";

// Process payment
const result = await processV3EntryPayment(
  connection,
  publicKey,
  signTransaction,
  usdcToSmallestUnit(10) // 10 USDC
);

// Handle result
if (result.success) {
  // Payment successful
  console.log("Signature:", result.transactionSignature);
  window.open(result.explorerUrl, "_blank");
} else {
  // Payment failed
  console.error("Error:", result.error);
}
```

### 3. **State Management**

Components need to manage:
- **Loading state** - When transaction is processing
- **Error state** - When payment fails
- **Success state** - When payment succeeds
- **Amount state** - User-entered payment amount
- **Wallet state** - Connection status

### 4. **User Experience Flow**

```
1. User sees payment button/modal
   ↓
2. User enters amount (or uses default)
   ↓
3. User clicks "Pay X USDC"
   ↓
4. Component checks wallet connection
   ├─ Not connected → Prompt to connect
   └─ Connected → Continue
   ↓
5. Component calls processV3EntryPayment()
   ↓
6. Payment processor builds transaction
   ├─ Derives PDAs (lottery, entry)
   ├─ Fetches lottery account state
   ├─ Builds instruction
   └─ Creates transaction
   ↓
7. Wallet adapter signs transaction
   ↓
8. Transaction sent to Solana network
   ↓
9. Component waits for confirmation
   ↓
10. Success: Show success message + explorer link
    Error: Show error message
```

## Component Testing

Component tests would validate:

```typescript
// frontend/src/__tests__/components/V3PaymentButton.test.tsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { WalletProvider } from "@solana/wallet-adapter-react";
import V3PaymentButton from "@/components/V3PaymentButton";

describe("V3PaymentButton", () => {
  it("should render payment button", () => {
    render(<V3PaymentButton />);
    expect(screen.getByText(/Pay/i)).toBeInTheDocument();
  });

  it("should handle wallet connection", async () => {
    // Mock wallet adapter
    // Test connection flow
  });

  it("should process payment on click", async () => {
    // Mock payment processor
    // Test payment flow
  });

  it("should display error on failure", async () => {
    // Mock payment failure
    // Test error display
  });
});
```

## Comparison: V2 vs V3 Components

| Aspect | V2 | V3 |
|--------|----|----|
| **Payment Function** | `processV2EntryPayment(..., bountyId, ...)` | `processV3EntryPayment(..., entryAmount)` |
| **PDA Structure** | `[global, bounty]` | `[lottery, entry]` |
| **Account Fetching** | Static PDAs | Dynamic (fetches lottery account for jackpotWallet) |
| **Error Handling** | Similar | Similar |
| **Wallet Integration** | Identical | Identical |

## Production Integration

### Feature Flag Integration

```typescript
// Use environment variable to toggle V3
const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";

function PaymentComponent() {
  if (USE_V3) {
    return <V3PaymentButton />;
  } else {
    return <V2PaymentButton />;
  }
}
```

### Gradual Rollout

1. **Phase 1**: V3 components hidden behind feature flag
2. **Phase 2**: V3 available to beta users
3. **Phase 3**: V3 default, V2 fallback
4. **Phase 4**: V3 only

## What Gets Created

### Components (React)
- ✅ `V3PaymentButton.tsx` - Simple payment button
- ✅ `V3PaymentModal.tsx` - Modal dialog for payments
- ✅ `V3LotteryStatus.tsx` - Display lottery status
- ✅ Component tests (`.test.tsx` files)

### Integration Points
- ✅ `BountyChatInterface.tsx` - Add V3 payment option
- ✅ `PaymentFlow.tsx` - Add V3 wallet payment method
- ✅ Feature flag logic for V2/V3 switching

### Styling
- ✅ Tailwind CSS classes (consistent with V2)
- ✅ Loading states, error states, success states
- ✅ Mobile-responsive design

## Next Steps for Component Integration

1. **Create V3PaymentButton** - Simple button component
2. **Create V3PaymentModal** - Modal dialog component
3. **Add to BountyChatInterface** - Integrate payment flow
4. **Add feature flag** - Toggle V2/V3
5. **Component tests** - React Testing Library
6. **E2E tests** - Playwright integration tests

---

**Current Status**: Payment processor ready ✅  
**Next**: Create React components using the same pattern as V2
