# Contract Version Priority & Flag Configuration

## How Version Flags Work

The system uses a **priority order** to determine which contract version to use:

### Priority Order: **V3 > V2 > V1**

```
If USE_CONTRACT_V3=true  → Uses V3 (highest priority)
Else if USE_CONTRACT_V2=true  → Uses V2
Else  → Uses V1 (fallback)
```

## What Happens When Both Are Set to `true`

### ✅ **Safe (But Redundant)**

If you set both:
```bash
USE_CONTRACT_V3=true
USE_CONTRACT_V2=true
```

**Result**: 
- ✅ V3 will be used (it has priority)
- ⚠️ V2 will be **completely ignored**
- ✅ No errors, but unnecessary flag is redundant

### ✅ **Recommended Configuration**

You should only enable **one** at a time:

**For V3 (Recommended - Most Secure):**
```bash
# Backend .env
USE_CONTRACT_V3=true
USE_CONTRACT_V2=false

# Frontend .env.local
NEXT_PUBLIC_USE_CONTRACT_V3=true
NEXT_PUBLIC_USE_CONTRACT_V2=false
```

**For V2:**
```bash
# Backend .env
USE_CONTRACT_V3=false
USE_CONTRACT_V2=true

# Frontend .env.local
NEXT_PUBLIC_USE_CONTRACT_V3=false
NEXT_PUBLIC_USE_CONTRACT_V2=true
```

---

## Code Implementation

### Backend Priority Logic

**File**: `src/services/smart_contract_service.py` (lines 48-72)

```python
# Check feature flags in priority order: V3 > V2 > V1
use_v3 = os.getenv("USE_CONTRACT_V3", "false").lower() == "true"
use_v2 = os.getenv("USE_CONTRACT_V2", "false").lower() == "true"

# Try V3 adapter first (highest priority)
if use_v3:
    # Uses V3 and returns early
    logger.info("🔒 Using V3 smart contract (secure)")
    return  # ← Stops here, V2 never checked

# Try V2 if V3 not available (only reached if V3 is false)
if use_v2:
    logger.info("🆕 Using V2 smart contract")
else:
    # Fallback to V1
    logger.info("📌 Using V1 smart contract (legacy)")
```

**Key Point**: The `return` statement on line 60 means if V3 is enabled, V2 is never checked.

---

### Frontend Priority Logic

**File**: `frontend/src/lib/paymentProcessor.ts` (lines 40-67)

```typescript
// Check feature flags in priority order: V3 > V2 > V1
const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";
const USE_V2 = process.env.NEXT_PUBLIC_USE_CONTRACT_V2 === "true";

// Route to V3 if enabled
if (USE_V3) {
  console.log("🔒 Using V3 payment processor (secure)");
  return await processV3EntryPayment(...);  // ← Returns early
}

// Route to V2 if enabled (only reached if V3 is false)
if (USE_V2) {
  console.log("🆕 Using V2 payment processor");
  return await processV2EntryPayment(...);
}

// Fallback to V1
console.warn("📌 V1 contract requires backend API");
```

**Key Point**: The early `return` means if V3 is enabled, V2 code never executes.

---

## Recommendations

### ✅ **Best Practice**

**Only enable the version you want to use:**

```bash
# Production (Using V3)
USE_CONTRACT_V3=true
USE_CONTRACT_V2=false

# Staging (Testing V2)
USE_CONTRACT_V3=false
USE_CONTRACT_V2=true
```

### ⚠️ **Why Not Both?**

1. **Confusion**: Logs might show both flags, making debugging harder
2. **Unnecessary**: V2 will never be used if V3 is true
3. **Clarity**: Clearer intent when only one flag is enabled

### ✅ **When Both Might Be Okay**

- **Testing migration**: Temporarily have both enabled while migrating from V2 to V3
- **Gradual rollout**: Enabling V3 while keeping V2 as fallback (though V3 will still be used)

---

## Quick Check Commands

**Check which version backend is using:**

Look for these log messages when backend starts:
- `🔒 Using V3 smart contract (secure)` → V3 active
- `🆕 Using V2 smart contract` → V2 active
- `📌 Using V1 smart contract (legacy)` → V1 active

**Check frontend console:**

Look for these messages:
- `🔒 Using V3 payment processor (secure)` → V3 active
- `🆕 Using V2 payment processor (parallel)` → V2 active

---

## Summary

| Configuration | Result |
|--------------|--------|
| `V3=true, V2=false` | ✅ Uses V3 |
| `V3=false, V2=true` | ✅ Uses V2 |
| `V3=true, V2=true` | ✅ Uses V3 (V2 ignored) |
| `V3=false, V2=false` | ✅ Uses V1 (fallback) |

**Recommendation**: Set only one to `true` for clarity, but having both won't cause errors - V3 will take precedence.

