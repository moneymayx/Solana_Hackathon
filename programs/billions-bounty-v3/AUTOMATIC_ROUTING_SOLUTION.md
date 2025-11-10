# Automatic Routing Solution - No File Modifications Needed!

## The Problem

You're right! The parallel system WAS supposed to work automatically with just environment variables. But there's a key difference:

- **Backend**: Can be fully automatic (routing service)
- **Frontend**: Needs component changes because it builds transactions **client-side**

## Why Frontend Needs Changes

The frontend **builds Solana transactions directly in the browser** using:
- `processV2EntryPayment()` - builds V2 contract transaction
- `processV3EntryPayment()` - builds V3 contract transaction

These are **different contract addresses** and **different instruction formats**. The browser can't automatically switch because it needs to:
1. Derive different PDAs (V2: `[global, bounty]`, V3: `[lottery, entry]`)
2. Build different instruction data
3. Use different program IDs

## The Solution: Two Approaches

### Approach 1: Backend API (Fully Automatic)

**Backend is already set up!** The backend can route automatically because:
- `smart_contract_service.py` checks `USE_CONTRACT_V2` flag (lines 48-63)
- It automatically uses V2 program ID when flag is enabled
- Existing API endpoints use this service

**To enable V3 automatically in backend:**

1. Modify `smart_contract_service.py` to check for V3 adapter first:

```python
# In smart_contract_service.py __init__ method
def __init__(self):
    # Check V3 first (highest priority)
    use_v3 = os.getenv("USE_CONTRACT_V3", "false").lower() == "true"
    use_v2 = os.getenv("USE_CONTRACT_V2", "false").lower() == "true"
    
    if use_v3:
        from .contract_adapter_v3 import get_contract_adapter_v3
        adapter = get_contract_adapter_v3()
        if adapter:
            # V3 is active - service will use V3 adapter
            self._use_adapter = True
            self._adapter = adapter
            logger.info("🔒 Using V3 contract (secure)")
            return
    elif use_v2:
        # V2 logic (existing)
        ...
    
    # Fall back to V1
    ...
```

**But this requires modifying `smart_contract_service.py`**

### Approach 2: Create Router Service (No Existing File Changes)

Create a NEW service that existing code can optionally use:

```python
# src/services/contract_router.py (NEW FILE)
from .contract_adapter_v3 import get_contract_adapter_v3
from .contract_adapter_v2 import get_contract_adapter_v2
from .smart_contract_service import smart_contract_service

class ContractRouter:
    def process_lottery_entry(...):
        if USE_CONTRACT_V3:
            adapter = get_contract_adapter_v3()
            if adapter:
                return await adapter.process_entry_payment(...)
        elif USE_CONTRACT_V2:
            adapter = get_contract_adapter_v2()
            if adapter:
                return await adapter.process_entry_payment(...)
        else:
            return await smart_contract_service.process_lottery_entry(...)
```

**Then update ONE file** (the payment API endpoint) to use the router instead of `smart_contract_service` directly.

### Approach 3: Frontend Auto-Detection (Minimal Changes)

Create a wrapper that detects which version to use:

```typescript
// frontend/src/lib/paymentProcessor.ts (NEW FILE)
import { processV2EntryPayment } from "./v2/paymentProcessor";
import { processV3EntryPayment } from "./v3/paymentProcessor";

export async function processEntryPayment(...) {
  const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";
  const USE_V2 = process.env.NEXT_PUBLIC_USE_CONTRACT_V2 === "true";
  
  if (USE_V3) {
    return await processV3EntryPayment(...);
  } else if (USE_V2) {
    return await processV2EntryPayment(...);
  } else {
    // V1 logic
  }
}
```

**Then update components** to use `processEntryPayment()` instead of `processV2EntryPayment()` directly.

## Recommended Solution

**For Backend (Fully Automatic):**
1. Update `smart_contract_service.py` to check V3 adapter first (1 file change)
2. Set `USE_CONTRACT_V3=true` → Automatic!

**For Frontend (Minimal Changes):**
1. Create `paymentProcessor.ts` wrapper (NEW file)
2. Update components to import from wrapper instead of v2/v3 directly
3. Set `NEXT_PUBLIC_USE_CONTRACT_V3=true` → Automatic!

This gives you the automatic routing you wanted with minimal code changes!

