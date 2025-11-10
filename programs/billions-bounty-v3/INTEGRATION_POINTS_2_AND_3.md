# Integration Points 2 & 3 - Detailed Guide

## Point 2: Integration into BountyChatInterface

### Current Flow

**BountyChatInterface** currently handles wallet payments through:
1. `handleWalletPayment()` function (line ~488)
2. Calls backend API `/api/payment/create`
3. Backend builds transaction
4. Frontend signs and sends

### How to Integrate V3

**Option A: Replace existing wallet payment with V3 (when flag enabled)**

```typescript
// In BountyChatInterface.tsx

import V3PaymentButton from "@/components/V3PaymentButton";
import PaymentMethodSelector from "@/components/PaymentMethodSelector"; // NEW: Wrapper component

// Add state for V3 payment
const [showV3Payment, setShowV3Payment] = useState(false);

// Modify handleWalletPayment
const handleWalletPayment = async (selectedAmount: number) => {
  const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";
  
  if (USE_V3) {
    // Option 1: Show V3 payment component inline
    setShowV3Payment(true);
    return;
    
    // Option 2: Use PaymentMethodSelector (cleaner)
    // This automatically handles V2/V3 switching based on flag
  } else {
    // Existing backend API flow
    if (!connected || !publicKey || !signTransaction) {
      setError('Please connect your wallet first');
      return;
    }
    
    // ... existing code ...
  }
};

// In JSX, replace or add:
{showV3Payment && (
  <div className="modal">
    <PaymentMethodSelector
      defaultAmount={getCurrentQuestionCost(...)}
      onSuccess={(signature, explorerUrl) => {
        setShowV3Payment(false);
        // Continue chat flow
        window.open(explorerUrl, "_blank");
      }}
      onError={(error) => {
        setError(error);
      }}
    />
  </div>
)}
```

**Option B: Add V3 as separate payment option**

```typescript
// Add V3 as an additional button/option alongside existing payment methods

<div className="payment-options">
  <button onClick={() => setShowPaymentModal(true)}>
    Pay with Wallet (V2)
  </button>
  
  {process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true" && (
    <button onClick={() => setShowV3Payment(true)}>
      Pay with Wallet (V3 Secure)
    </button>
  )}
</div>
```

### Complete Code Example

```typescript
// At top of BountyChatInterface.tsx
import PaymentMethodSelector from "@/components/PaymentMethodSelector";

// Add state
const [showV3Payment, setShowV3Payment] = useState(false);

// Modify handleWalletPayment
const handleWalletPayment = async (selectedAmount: number) => {
  const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";
  
  if (USE_V3) {
    // Use V3 direct contract payment (client-side)
    setShowV3Payment(true);
    return;
  }
  
  // Existing V2 backend API flow
  // ... rest of existing code ...
};

// Add V3 payment handler
const handleV3PaymentSuccess = (signature: string, explorerUrl: string) => {
  setShowV3Payment(false);
  addSystemMessage(`✅ Payment successful: ${signature.slice(0, 8)}...`);
  // Grant questions, continue chat flow
  setIsParticipating(true);
  setError(null);
  window.open(explorerUrl, "_blank");
};

// In JSX (add near PaymentAmountModal)
{showV3Payment && (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div className="bg-white rounded-lg p-6 max-w-md w-full">
      <h2>Make Payment</h2>
      <PaymentMethodSelector
        defaultAmount={getCurrentQuestionCost(
          getStartingQuestionCost(bountyStatus?.difficulty_level || 'easy'),
          bountyStatus?.total_entries || 0
        )}
        onSuccess={handleV3PaymentSuccess}
        onError={(error) => {
          setError(error);
          setShowV3Payment(false);
        }}
      />
      <button onClick={() => setShowV3Payment(false)}>Close</button>
    </div>
  </div>
)}
```

---

## Point 3: Integration into PaymentFlow

### Current Flow

**PaymentFlow** currently has:
1. Payment method selection (fiat/wallet/free)
2. Amount input
3. MoonPay integration for fiat
4. Backend API for wallet payments

### How to Integrate V3

**Option A: Replace wallet payment method with V3**

```typescript
// In PaymentFlow.tsx

import PaymentMethodSelector from "@/components/PaymentMethodSelector";

// Modify wallet payment method
{paymentMethod === 'wallet' && (
  <PaymentMethodSelector
    defaultAmount={amount}
    onSuccess={(signature, explorerUrl) => {
      setPaymentStatus('success');
      onPaymentSuccess?.(signature);
      window.open(explorerUrl, "_blank");
    }}
    onError={(error) => {
      setPaymentStatus('failed');
      onPaymentFailure?.(error);
    }}
  />
)}
```

**Option B: Add V3 as separate payment method**

```typescript
// Add 'wallet-v3' as a new payment method option

const [paymentMethod, setPaymentMethod] = useState<'wallet' | 'fiat' | 'free' | 'wallet-v3'>('fiat');

// In payment method selector
<div className="payment-methods">
  <button onClick={() => setPaymentMethod('fiat')}>Fiat</button>
  <button onClick={() => setPaymentMethod('wallet')}>Wallet (V2)</button>
  {process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true" && (
    <button onClick={() => setPaymentMethod('wallet-v3')}>Wallet (V3 Secure)</button>
  )}
  <button onClick={() => setPaymentMethod('free')}>Free Question</button>
</div>

// In payment processing
{paymentMethod === 'wallet-v3' && (
  <PaymentMethodSelector
    defaultAmount={amount}
    onSuccess={handlePaymentSuccess}
    onError={handlePaymentFailure}
  />
)}
```

### Complete Code Example

```typescript
// At top of PaymentFlow.tsx
import PaymentMethodSelector from "@/components/PaymentMethodSelector";

// Modify createPayment function
const createPayment = async () => {
  const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";
  
  // If V3 wallet payment, use PaymentMethodSelector (handled by component)
  if (paymentMethod === 'wallet' && USE_V3) {
    // PaymentMethodSelector handles the payment directly
    // We just need to track state
    setPaymentStatus('processing');
    return;
  }
  
  // Existing payment flow for fiat/V2 wallet
  if (!connected || !publicKey) {
    onPaymentFailure?.('Please connect your wallet first');
    return;
  }
  
  // ... existing code for MoonPay/fiat payments ...
};

// Add wallet payment section
{paymentMethod === 'wallet' && (
  <div>
    {process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true" ? (
      <PaymentMethodSelector
        defaultAmount={amount}
        onSuccess={(signature, explorerUrl) => {
          setPaymentStatus('success');
          onPaymentSuccess?.(signature);
          window.open(explorerUrl, "_blank");
        }}
        onError={(error) => {
          setPaymentStatus('failed');
          onPaymentFailure?.(error);
        }}
      />
    ) : (
      // Existing wallet payment UI
      <button onClick={createPayment}>
        Pay with Wallet
      </button>
    )}
  </div>
)}
```

---

## Summary: What Code Modifications Are Needed

### For BountyChatInterface:

1. **Import**: Add `import PaymentMethodSelector from "@/components/PaymentMethodSelector"`
2. **State**: Add `const [showV3Payment, setShowV3Payment] = useState(false)`
3. **Modify `handleWalletPayment`**: Check `USE_V3` flag and conditionally show V3 payment
4. **JSX**: Add V3 payment modal/component rendering

### For PaymentFlow:

1. **Import**: Add `import PaymentMethodSelector from "@/components/PaymentMethodSelector"`
2. **Modify `createPayment`**: Check `USE_V3` flag for wallet payments
3. **JSX**: Replace or add V3 payment component in wallet payment section

### The Feature Flag Check Pattern:

```typescript
// This is the key integration code you need to add:
const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";

if (USE_V3) {
  // Use V3 components/logic
} else {
  // Use existing V2/V1 components/logic
}
```

### Files to Modify:

1. ✅ `frontend/src/components/BountyChatInterface.tsx` - Add V3 payment option
2. ✅ `frontend/src/components/PaymentFlow.tsx` - Add V3 wallet payment
3. ✅ `frontend/src/components/PaymentMethodSelector.tsx` - Already created (wrapper component)

---

## Step-by-Step Integration Checklist

### BountyChatInterface:
- [ ] Import `PaymentMethodSelector`
- [ ] Add `showV3Payment` state
- [ ] Modify `handleWalletPayment` to check flag
- [ ] Add V3 payment modal/component in JSX
- [ ] Test with flag enabled/disabled

### PaymentFlow:
- [ ] Import `PaymentMethodSelector`
- [ ] Modify wallet payment section to use `PaymentMethodSelector` when flag enabled
- [ ] Test with flag enabled/disabled

### Testing:
- [ ] Test V2 flow (flag disabled)
- [ ] Test V3 flow (flag enabled)
- [ ] Verify no regressions

---

**Remember**: The feature flag doesn't automatically do anything - you must add the conditional code to check the flag and use V3 components.
