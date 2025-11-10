# Testing V3 on the Frontend

This guide shows you how to test V3 contract functionality on the frontend.

## Quick Start

### 1. Enable V3 Feature Flag

**Frontend** (`.env.local` or environment variables):
```bash
NEXT_PUBLIC_USE_CONTRACT_V3=true
NEXT_PUBLIC_USE_CONTRACT_V2=false
```

**Backend** (`.env`):
```bash
USE_CONTRACT_V3=true
USE_CONTRACT_V2=false
```

### 2. Restart Your Frontend

```bash
# Stop your dev server (Ctrl+C)
# Then restart
npm run dev
# or
yarn dev
```

**Important**: Next.js caches environment variables, so you must restart for changes to take effect.

---

## Testing Methods

### Method 1: Using PaymentMethodSelector (Automatic)

The `PaymentMethodSelector` component automatically uses V3 when the flag is enabled.

**Where to find it:**
- Look for components that import `PaymentMethodSelector`
- Check pages that use payment buttons

**What to look for:**
- You should see a badge: **"🔒 Using V3 (Secure)"** above the payment button
- Console will log: `"V3 payment successful:"` or `"V3 payment error:"`

---

### Method 2: Direct V3PaymentButton Component

You can test the V3PaymentButton directly:

```typescript
import V3PaymentButton from "@/components/V3PaymentButton";

function TestPage() {
  return (
    <div>
      <h1>V3 Payment Test</h1>
      <V3PaymentButton
        defaultAmount={10}
        onSuccess={(sig, url) => console.log("Success!", sig, url)}
        onError={(err) => console.error("Error:", err)}
      />
    </div>
  );
}
```

**What happens:**
- Component renders a payment form
- User enters amount (defaults to 10 USDC)
- Clicks "Pay" button
- Wallet prompts to sign transaction
- Transaction processed via V3 contract

---

### Method 3: Using Unified Payment Processor

The `processEntryPayment` function automatically routes to V3:

```typescript
import { processEntryPayment } from "@/lib/paymentProcessor";

// This automatically uses V3 if NEXT_PUBLIC_USE_CONTRACT_V3=true
const result = await processEntryPayment(
  connection,
  publicKey,
  signTransaction,
  10 // 10 USDC
);
```

**What to look for in console:**
```
🔒 Using V3 payment processor (secure) - AUTOMATIC ROUTING
🔄 Processing V3 payment: 10 USDC (10000000 smallest units)
✅ Payment successful! <transaction-signature>
```

---

## Verification Checklist

### ✅ Step 1: Check Environment Variables

**In browser console**, check if flag is set:

```javascript
// Open browser console (F12) and run:
console.log('V3 Enabled:', process.env.NEXT_PUBLIC_USE_CONTRACT_V3);
// Should show: "true" (as string)
```

**Note**: Next.js environment variables are replaced at build time, so you might see `undefined` in browser. This is normal - check if the component actually uses V3 instead.

---

### ✅ Step 2: Look for V3 Indicators

**Visual Indicators:**
1. **Badge**: Look for "🔒 Using V3 (Secure)" text above payment button
2. **Console Logs**: Check browser console for V3-specific messages

**Console Messages to Look For:**

**When component renders:**
- ✅ `"🔒 Using V3 payment processor (secure) - AUTOMATIC ROUTING"`
- ✅ `"🔒 Using V3 (Secure)"` (from PaymentMethodSelector)

**During payment:**
- ✅ `"🔄 Processing V3 payment: 10 USDC (10000000 smallest units)"`
- ✅ `"✅ Payment successful!"` followed by transaction signature
- ✅ `"V3 payment successful: <signature>"` (from PaymentMethodSelector)

**Error indicators:**
- ❌ `"❌ Payment failed:"` - Check error message
- ❌ `"V3 payment error: <error>"` - Check what went wrong

---

### ✅ Step 3: Verify Transaction

After a successful payment:

1. **Transaction Signature**: Console will show the signature
2. **Explorer Link**: Click the explorer URL in the success message
3. **Verify on Solana Explorer**:
   - Go to the transaction page
   - Check "Program ID" - should be V3 program: `ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb` (devnet)
   - Look for "Instruction: Process Entry Payment V3" or similar

---

## Testing Checklist

### Before Testing
- [ ] Set `NEXT_PUBLIC_USE_CONTRACT_V3=true` in frontend `.env.local`
- [ ] Set `USE_CONTRACT_V3=true` in backend `.env`
- [ ] Restart frontend dev server
- [ ] Restart backend server
- [ ] Connect Solana wallet (Phantom, etc.)
- [ ] Ensure wallet has USDC on devnet

### During Testing
- [ ] See "🔒 Using V3 (Secure)" badge
- [ ] Console shows "Using V3 payment processor"
- [ ] Enter payment amount
- [ ] Click "Pay" button
- [ ] Wallet prompts for transaction signature
- [ ] Approve transaction
- [ ] See success message with transaction signature
- [ ] Verify transaction on Solana Explorer

### After Testing
- [ ] Transaction appears on Solana Explorer
- [ ] Program ID matches V3 program ID
- [ ] USDC deducted from wallet
- [ ] No errors in console

---

## Troubleshooting

### ❌ Not Seeing V3 Indicator

**Problem**: Still seeing V2 or no version indicator

**Solutions:**
1. **Clear Next.js cache:**
   ```bash
   rm -rf .next
   npm run dev
   ```

2. **Check environment variable spelling:**
   - Must be exactly: `NEXT_PUBLIC_USE_CONTRACT_V3=true`
   - No spaces, no typos

3. **Verify in code:**
   ```typescript
   // Add this temporarily to see what the flag is
   console.log('V3 Flag:', process.env.NEXT_PUBLIC_USE_CONTRACT_V3);
   ```

4. **Check if component uses PaymentMethodSelector:**
   - If using `V2PaymentButton` directly, it won't switch to V3
   - Use `PaymentMethodSelector` instead, or import `V3PaymentButton` directly

---

### ❌ Payment Fails

**Check console errors:**

1. **"Please connect your wallet"**
   - Connect your Solana wallet first

2. **"Insufficient funds"**
   - Ensure wallet has USDC on devnet
   - Get devnet USDC from a faucet

3. **"Program ID mismatch"**
   - Verify V3 program is deployed
   - Check `NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V3` matches deployed program

4. **Transaction simulation failed**
   - Check RPC endpoint is working
   - Verify contract is deployed on correct network

---

### ❌ Console Shows V2 Instead of V3

**Problem**: Console logs show "Using V2 payment processor"

**Solutions:**
1. **Double-check environment variable:**
   ```bash
   # In .env.local
   NEXT_PUBLIC_USE_CONTRACT_V3=true
   NEXT_PUBLIC_USE_CONTRACT_V2=false  # Explicitly set to false
   ```

2. **Restart dev server:**
   ```bash
   # Kill the server and restart
   npm run dev
   ```

3. **Hard refresh browser:**
   - Press `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
   - Or clear browser cache

---

## Test Pages

### Option 1: Create a Test Page

Create `frontend/src/app/test-v3/page.tsx`:

```typescript
'use client';

import V3PaymentButton from "@/components/V3PaymentButton";
import PaymentMethodSelector from "@/components/PaymentMethodSelector";

export default function TestV3Page() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">V3 Testing Page</h1>
      
      <div className="space-y-8">
        <section>
          <h2 className="text-xl font-semibold mb-2">Direct V3PaymentButton</h2>
          <V3PaymentButton defaultAmount={10} />
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-2">PaymentMethodSelector (Auto)</h2>
          <PaymentMethodSelector defaultAmount={10} />
        </section>
      </div>
    </div>
  );
}
```

Visit: `http://localhost:3000/test-v3`

---

### Option 2: Use Existing Pages

Check where `PaymentMethodSelector` or payment components are used:

```bash
# Search for usage
grep -r "PaymentMethodSelector" frontend/src/app/
grep -r "V3PaymentButton" frontend/src/app/
grep -r "processEntryPayment" frontend/src/
```

---

## Expected Console Output

### ✅ Successful V3 Payment Flow

```
🔒 Using V3 payment processor (secure) - AUTOMATIC ROUTING
🔄 Processing V3 payment: 10 USDC (10000000 smallest units)
✅ Payment successful! 5xK7...abc123
V3 payment successful: 5xK7...abc123
```

### ✅ Successful Transaction Object

```javascript
{
  success: true,
  transactionSignature: "5xK7...abc123",
  explorerUrl: "https://explorer.solana.com/tx/5xK7...abc123?cluster=devnet"
}
```

---

## Summary

**Quick Test Steps:**

1. ✅ Set `NEXT_PUBLIC_USE_CONTRACT_V3=true`
2. ✅ Restart frontend dev server
3. ✅ Look for "🔒 Using V3 (Secure)" badge
4. ✅ Check console for "Using V3 payment processor"
5. ✅ Make a test payment
6. ✅ Verify transaction on Solana Explorer

**Success Indicators:**
- ✅ "🔒 Using V3 (Secure)" badge visible
- ✅ Console shows V3 messages
- ✅ Transaction succeeds with V3 program ID
- ✅ Explorer confirms V3 contract was used

If you see these, V3 is working! 🎉

