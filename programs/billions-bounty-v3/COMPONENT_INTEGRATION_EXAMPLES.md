# V3 Component Integration - Examples

## Quick Overview

Component integration means wrapping the V3 payment processor in React components that users can interact with. Here are concrete examples:

## Example 1: Simple Payment Button

```typescript
// Usage in any page/component
import V3PaymentButton from "@/components/V3PaymentButton";

function MyPage() {
  return (
    <div>
      <h1>Make a Payment</h1>
      <V3PaymentButton
        defaultAmount={10}
        onSuccess={(signature, explorerUrl) => {
          console.log("Payment successful!", signature);
          window.open(explorerUrl, "_blank");
        }}
        onError={(error) => {
          alert(`Payment failed: ${error}`);
        }}
      />
    </div>
  );
}
```

**What happens**:
1. User sees input field and button
2. User enters amount (or uses default 10 USDC)
3. User clicks "Pay X USDC"
4. Component checks wallet connection
5. Calls `processV3EntryPayment()` from payment processor
6. Shows loading state while processing
7. Shows success (with explorer link) or error

## Example 2: Integration in Chat Interface

```typescript
// In BountyChatInterface.tsx
import { useState } from "react";
import V3PaymentButton from "@/components/V3PaymentButton";
import { useConnection, useWallet } from "@solana/wallet-adapter-react";

function BountyChatInterface() {
  const [showPayment, setShowPayment] = useState(false);
  const [hasPaid, setHasPaid] = useState(false);

  const handlePaymentSuccess = (signature: string, explorerUrl: string) => {
    setHasPaid(true);
    setShowPayment(false);
    // Continue chat flow - user can now interact
    window.open(explorerUrl, "_blank");
  };

  return (
    <div>
      {!hasPaid && (
        <div>
          <p>Payment required to continue</p>
          <button onClick={() => setShowPayment(true)}>
            Pay Now
          </button>
          
          {showPayment && (
            <div className="modal">
              <V3PaymentButton
                defaultAmount={10}
                onSuccess={handlePaymentSuccess}
                onError={(error) => alert(error)}
              />
            </div>
          )}
        </div>
      )}

      {hasPaid && (
        <div>
          {/* Chat interface */}
        </div>
      )}
    </div>
  );
}
```

## Example 3: With Feature Flag (V2/V3 Toggle)

```typescript
// In a shared payment component
import { useMemo } from "react";
import V2PaymentButton from "@/components/V2PaymentButton";
import V3PaymentButton from "@/components/V3PaymentButton";

function PaymentComponent({ bountyId }: { bountyId?: number }) {
  const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";

  const PaymentButton = useMemo(() => {
    if (USE_V3) {
      return (
        <V3PaymentButton
          defaultAmount={10}
          onSuccess={(sig, url) => console.log("V3 success", sig)}
        />
      );
    } else {
      return (
        <V2PaymentButton
          bountyId={bountyId || 1}
          defaultAmount={10}
          onSuccess={(sig, url) => console.log("V2 success", sig)}
        />
      );
    }
  }, [USE_V3, bountyId]);

  return (
    <div>
      {USE_V3 && <span className="badge">Using V3 (Secure)</span>}
      {PaymentButton}
    </div>
  );
}
```

## Example 4: Custom Payment Modal

```typescript
// V3PaymentModal.tsx (full implementation)
"use client";

import { useState, useEffect } from "react";
import { useConnection, useWallet } from "@solana/wallet-adapter-react";
import { X, ExternalLink, Loader2, CheckCircle } from "lucide-react";
import {
  processV3EntryPayment,
  usdcToSmallestUnit,
  getV3LotteryStatus,
} from "@/lib/v3/paymentProcessor";
import V3PaymentButton from "@/components/V3PaymentButton";

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
  const [lotteryStatus, setLotteryStatus] = useState<{
    success: boolean;
    lotteryPDA?: string;
  } | null>(null);

  useEffect(() => {
    if (isOpen) {
      // Fetch lottery status when modal opens
      getV3LotteryStatus(connection).then(setLotteryStatus);
    }
  }, [isOpen, connection]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
        >
          <X className="w-6 h-6" />
        </button>

        <h2 className="text-2xl font-bold mb-4">Make Payment</h2>

        {lotteryStatus?.success && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded">
            <p className="text-sm text-green-700">
              ✅ Lottery active and ready
            </p>
          </div>
        )}

        <V3PaymentButton
          defaultAmount={defaultAmount}
          onSuccess={(signature, explorerUrl) => {
            onSuccess?.(signature);
            onClose();
          }}
          onError={(error) => {
            console.error("Payment error:", error);
          }}
        />
      </div>
    </div>
  );
}
```

## Key Differences: V2 vs V3 Components

### V2 Payment Button
```typescript
processV2EntryPayment(
  connection,
  publicKey,
  signTransaction,
  bountyId,        // ← Requires bounty ID
  entryAmount
)
```

### V3 Payment Button
```typescript
processV3EntryPayment(
  connection,
  publicKey,
  signTransaction,
  entryAmount      // ← No bounty ID needed (simpler!)
)
```

**V3 Advantages**:
- ✅ Simpler API (no bounty ID)
- ✅ Enhanced security (Ed25519, hashing, validation)
- ✅ Better error handling
- ✅ Fetches lottery state dynamically

## Testing Components

### Component Unit Test

```typescript
// V3PaymentButton.test.tsx
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { WalletProvider } from "@solana/wallet-adapter-react";
import V3PaymentButton from "@/components/V3PaymentButton";

// Mock the payment processor
jest.mock("@/lib/v3/paymentProcessor", () => ({
  processV3EntryPayment: jest.fn(),
  usdcToSmallestUnit: (n: number) => n * 1_000_000,
}));

describe("V3PaymentButton", () => {
  it("should render payment button", () => {
    render(
      <WalletProvider>
        <V3PaymentButton />
      </WalletProvider>
    );
    expect(screen.getByText(/Pay/i)).toBeInTheDocument();
  });

  it("should process payment when clicked", async () => {
    const mockProcess = require("@/lib/v3/paymentProcessor").processV3EntryPayment;
    mockProcess.mockResolvedValue({
      success: true,
      transactionSignature: "test-sig",
      explorerUrl: "https://explorer.solana.com/tx/test-sig",
    });

    render(
      <WalletProvider>
        <V3PaymentButton />
      </WalletProvider>
    );

    const button = screen.getByText(/Pay/i);
    fireEvent.click(button);

    await waitFor(() => {
      expect(mockProcess).toHaveBeenCalled();
    });
  });
});
```

## Integration Checklist

When integrating V3 components:

- [ ] **Wallet Provider** - Ensure `WalletProvider` wraps your app
- [ ] **Connection** - Use `useConnection()` hook
- [ ] **Wallet State** - Use `useWallet()` hook
- [ ] **Error Handling** - Display errors to users
- [ ] **Loading States** - Show loading indicators
- [ ] **Success States** - Show success with explorer link
- [ ] **Mobile Responsive** - Test on mobile devices
- [ ] **Accessibility** - Proper labels and ARIA attributes

## Real-World Usage Flow

```
1. User visits page with payment option
   ↓
2. User clicks "Pay" button
   ↓
3. Component checks:
   ├─ Wallet connected? → Yes
   ├─ Amount valid? → Yes
   └─ Ready to pay? → Yes
   ↓
4. Component shows loading state ("Processing...")
   ↓
5. Payment processor:
   ├─ Derives lottery PDA
   ├─ Fetches lottery account (gets jackpotWallet)
   ├─ Derives entry PDA
   ├─ Builds transaction
   └─ Signs transaction
   ↓
6. Transaction sent to Solana network
   ↓
7. Waiting for confirmation...
   ↓
8. Success:
   ├─ Shows success message
   ├─ Displays explorer link
   └─ Calls onSuccess callback
   ↓
9. User can:
   ├─ Click explorer link (view transaction)
   ├─ Continue to next step
   └─ Make another payment
```

## Next Steps

1. **Create V3PaymentButton** ✅ (Created in this file)
2. **Create V3PaymentModal** - Modal version
3. **Add to BountyChatInterface** - Integrate into chat flow
4. **Component Tests** - React Testing Library tests
5. **Feature Flag** - Toggle V2/V3
6. **Documentation** - Update user-facing docs

---

**Component Integration = React UI + Wallet Adapter + Payment Processor**
