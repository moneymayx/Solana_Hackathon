# Feature Flag Integration - How It Actually Works

## Important: Feature Flags Require Code Modifications

**Feature flags don't automatically integrate** - you need to modify your code to check the flag and conditionally use V3 components/processors.

## How Feature Flags Work

### 1. Environment Variable Setup

Set in your `.env.local` or deployment platform:

```bash
# Frontend (.env.local or Vercel)
NEXT_PUBLIC_USE_CONTRACT_V3=true  # Enable V3

# Backend (.env or DigitalOcean)
USE_CONTRACT_V3=true  # Enable V3
```

### 2. Code Modification Required

You must modify your components to check the flag and conditionally use V3:

```typescript
// ❌ WRONG: This doesn't work automatically
// Just setting the env variable doesn't do anything

// ✅ CORRECT: You must check the flag in code
const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";

if (USE_V3) {
  // Use V3 components/processors
  return <V3PaymentButton />;
} else {
  // Use existing V2/V1 components/processors
  return <V2PaymentButton />;
}
```

## Integration Examples

### Example 1: Simple Conditional Rendering

```typescript
// In any component
import V2PaymentButton from "@/components/V2PaymentButton";
import V3PaymentButton from "@/components/V3PaymentButton";

function PaymentComponent() {
  const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";
  
  // This is the code modification you need
  return USE_V3 ? <V3PaymentButton /> : <V2PaymentButton />;
}
```

### Example 2: In BountyChatInterface

**Before (existing code):**
```typescript
// Uses backend API for wallet payment
const handleWalletPayment = async (selectedAmount: number) => {
  // Calls backend API
  const response = await fetch(`${getBackendUrl()}/api/payment/create`, {...});
  // ...
}
```

**After (with V3 flag integration):**
```typescript
import V3PaymentButton from "@/components/V3PaymentButton";

const handleWalletPayment = async (selectedAmount: number) => {
  const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";
  
  if (USE_V3) {
    // Use V3 direct contract call (client-side)
    // This bypasses the backend API and calls contract directly
    // You would need to integrate V3PaymentButton into the payment flow
    setShowV3Payment(true);
    return;
  } else {
    // Existing backend API flow
    const response = await fetch(`${getBackendUrl()}/api/payment/create`, {...});
    // ...
  }
}
```

### Example 3: Complete Integration Pattern

```typescript
// Create a wrapper component that handles flag logic
"use client";

import { useState } from "react";
import V2PaymentButton from "@/components/V2PaymentButton";
import V3PaymentButton from "@/components/V3PaymentButton";

export default function SmartPaymentButton({ bountyId, defaultAmount }: Props) {
  const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";
  
  const handleSuccess = (signature: string, explorerUrl: string) => {
    console.log("Payment successful:", signature);
    window.open(explorerUrl, "_blank");
  };
  
  // This is where the magic happens - conditional rendering based on flag
  if (USE_V3) {
    return (
      <V3PaymentButton
        defaultAmount={defaultAmount}
        onSuccess={handleSuccess}
      />
    );
  } else {
    return (
      <V2PaymentButton
        bountyId={bountyId}
        defaultAmount={defaultAmount}
        onSuccess={handleSuccess}
      />
    );
  }
}
```

## What Gets Modified

### Files That Need Changes:

1. **BountyChatInterface.tsx**
   - Modify `handleWalletPayment` to check flag
   - Add V3PaymentButton as an option

2. **PaymentFlow.tsx**
   - Add V3 as a payment method option
   - Conditionally render V3PaymentButton

3. **Any page using payment components**
   - Replace direct component usage with flag-checking wrapper

## Step-by-Step Integration

### Step 1: Check Current Payment Flow

```bash
# Find where payments are handled
grep -r "handleWalletPayment\|PaymentFlow\|V2PaymentButton" frontend/src
```

### Step 2: Add Flag Check

```typescript
// At the top of component
const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";
```

### Step 3: Conditionally Use V3

```typescript
// Replace existing payment logic with:
{USE_V3 ? (
  <V3PaymentButton onSuccess={...} />
) : (
  <ExistingPaymentComponent ... />
)}
```

### Step 4: Test Both Paths

1. Set `NEXT_PUBLIC_USE_CONTRACT_V3=false` → Test V2 flow
2. Set `NEXT_PUBLIC_USE_CONTRACT_V3=true` → Test V3 flow

## Backend Integration

Backend also needs flag checks:

```python
# In contract_adapter_v3.py
USE_CONTRACT_V3 = os.getenv("USE_CONTRACT_V3", "false").lower() == "true"

# In payment endpoints
if USE_CONTRACT_V3:
    # Use V3 adapter
    adapter = get_contract_adapter_v3()
    result = await adapter.process_entry_payment(...)
else:
    # Use existing V1/V2 service
    result = await smart_contract_service.process_payment(...)
```

## Summary

**Feature flags require code changes:**
- ✅ Set environment variable
- ✅ Import V3 components
- ✅ Add conditional logic (if/else or ternary)
- ✅ Test both paths

**Feature flags do NOT:**
- ❌ Automatically switch components
- ❌ Work without code modifications
- ❌ Replace existing code automatically
