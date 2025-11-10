# V3 Integration Guide

**Version**: 0.3.0  
**Status**: Parallel Build (Feature Flag Controlled)  
**Date**: 2024

## Overview

This guide explains how to integrate and use the V3 secure smart contract. V3 is implemented as a parallel build following the same pattern as V2, allowing gradual rollout with feature flags.

---

## Architecture

V3 follows the same parallel integration pattern as V2:

- **Feature Flag**: `USE_CONTRACT_V3=false` (default, disabled)
- **Adapter Pattern**: Non-invasive wrapper that routes calls when enabled
- **Same Interface**: Drop-in replacement for existing contract service
- **No Breaking Changes**: Existing code continues to work when flag is disabled

---

## Environment Variables

### Backend Configuration

```bash
# Feature flag (default: false)
USE_CONTRACT_V3=false

# V3 Program Configuration
LOTTERY_PROGRAM_ID_V3=<deployed_program_id>
V3_LOTTERY_PDA=<pda_address>
V3_USDC_MINT=<usdc_mint_address>
V3_BACKEND_AUTHORITY=<backend_authority_pubkey>
```

### Frontend Configuration (if needed)

```bash
NEXT_PUBLIC_USE_CONTRACT_V3=false
NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V3=<deployed_program_id>
```

---

## Integration Steps

### Step 1: Deploy V3 Contract

1. Build the contract:
   ```bash
   cd programs/billions-bounty-v3
   anchor build
   ```

2. Deploy to devnet:
   ```bash
   anchor deploy --provider.cluster devnet
   ```

3. Update environment variables with deployed program ID

### Step 2: Initialize V3 Lottery

The V3 contract requires `backend_authority` to be set during initialization:

```rust
initialize_lottery(
    research_fund_floor: u64,
    research_fee: u64,
    jackpot_wallet: Pubkey,
    backend_authority: Pubkey,  // NEW: Required for signature verification
)
```

### Step 3: Enable Feature Flag (Gradual Rollout)

**Phase 1: Testing (Flag Disabled)**
- Set `USE_CONTRACT_V3=false`
- Verify existing functionality works
- Ensure no regressions

**Phase 2: Backend Testing (Backend Only)**
- Set `USE_CONTRACT_V3=true` on backend
- Keep frontend flag disabled
- Test backend integration

**Phase 3: Full Integration**
- Enable both backend and frontend flags
- Monitor for issues
- Keep rollback plan ready

---

## Backend Integration

### Using the Adapter

```python
from src.services.contract_adapter_v3 import get_contract_adapter_v3

# Get adapter (returns None if flag is disabled)
adapter = get_contract_adapter_v3()

if adapter:
    # Use V3 secure contract
    result = await adapter.process_ai_decision(
        user_message="...",
        ai_response="...",
        decision_hash=hash_bytes,
        signature=signature_bytes,
        is_successful_jailbreak=True,
        user_id=1,
        session_id="session-123",
        timestamp=int(time.time()),
        winner_wallet=winner_pubkey,
    )
else:
    # Use existing contract service
    from src.services.smart_contract_service import smart_contract_service
    result = await smart_contract_service.process_lottery_entry(...)
```

### Adapter Methods

The V3 adapter provides the same interface as the existing contract service:

- `process_entry_payment(entry_amount, user_wallet, user_keypair)`
- `process_ai_decision(user_message, ai_response, decision_hash, signature, ...)`
- `emergency_recovery(amount, authority_keypair)`
- `get_lottery_status()`

### Key Differences from V1/V2

1. **Backend Authority Required**: Must be set during initialization
2. **Input Validation**: Pre-validation in adapter + on-chain validation
3. **Signature Format**: Must be exactly 64 bytes (Ed25519)
4. **Session ID Format**: Must be alphanumeric + hyphens/underscores
5. **Emergency Recovery**: Has cooldown and amount limits

---

## Frontend Integration (Optional)

If frontend needs to call contract directly:

```typescript
import { PublicKey } from "@solana/web3.js";

const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";
const PROGRAM_ID = USE_V3 
  ? new PublicKey(process.env.NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V3!)
  : new PublicKey(process.env.LOTTERY_PROGRAM_ID!);

// Use appropriate program ID based on flag
```

**Recommendation**: Prefer backend mediation initially, then add direct frontend calls if needed.

---

## Testing Strategy

### Phase 1: Local Validator Tests

```bash
cd programs/billions-bounty-v3
anchor test
```

Verify all security tests pass:
- `tests/security_fixes.spec.ts`
- `tests/integration.spec.ts`
- `tests/edge_cases.spec.ts`

### Phase 2: Devnet Deployment

1. Deploy contract to devnet
2. Initialize lottery
3. Run integration tests against devnet
4. Test all security fixes in real environment

### Phase 3: Backend Adapter Tests

1. Set `USE_CONTRACT_V3=false` - verify no regression
2. Set `USE_CONTRACT_V3=true` - verify V3 works
3. Test parallel operation (both contracts can coexist)

### Phase 4: Production Rollout

1. Enable flag in staging environment first
2. Monitor logs and metrics
3. Gradual rollout to production
4. Keep rollback plan ready

---

## Rollback Plan

If issues are detected:

1. **Immediate Rollback**: Set `USE_CONTRACT_V3=false`
2. **Redeploy/Restart**: Restart backend services
3. **Verify**: Confirm existing contract functionality restored
4. **Investigate**: Review logs and fix issues
5. **Re-test**: Fix issues and re-test before re-enabling

---

## Key Security Features

When using V3, these security features are automatically enabled:

1. ✅ Ed25519 signature verification
2. ✅ SHA-256 cryptographic hashing
3. ✅ Comprehensive input validation
4. ✅ Reentrancy guards
5. ✅ Strengthened authority checks
6. ✅ Secure emergency recovery (cooldown + limits)

---

## Migration Notes

### From V1 to V3

- Add `backend_authority` parameter to initialization
- Update lottery account size (larger due to new fields)
- Update error handling for new error codes
- Test input validation (string lengths, formats)

### From V2 to V3

- V3 uses different account structure (lottery PDA vs global/bounty PDAs)
- V3 requires backend_authority (V2 uses different auth model)
- V3 has stricter input validation
- Emergency recovery has cooldown/limits (V2 doesn't have this)

---

## Common Issues

### Issue: "UnauthorizedBackend" Error

**Cause**: Backend authority doesn't match stored authority  
**Solution**: Verify `V3_BACKEND_AUTHORITY` matches the authority set during initialization

### Issue: "InputTooLong" Error

**Cause**: Message or session ID exceeds length limits  
**Solution**: Trim inputs to max 5000 chars (messages) or 100 chars (session ID)

### Issue: "TimestampOutOfRange" Error

**Cause**: Timestamp is too old (>1 hour) or in future  
**Solution**: Ensure timestamp is current (within 1 hour)

### Issue: "RecoveryCooldownActive" Error

**Cause**: Attempting emergency recovery within 24 hours of previous recovery  
**Solution**: Wait for cooldown period to expire

---

## Support

- Security Fixes Documentation: `docs/security/V3_SECURITY_FIXES.md`
- Testing Guide: `docs/testing/V3_TEST_GUIDE.md`
- Contract Source: `programs/billions-bounty-v3/src/lib.rs`
- Backend Adapter: `src/services/contract_adapter_v3.py`

---

## Status

- ✅ Contract Implementation: Complete
- ✅ Test Suite: Complete
- ✅ Backend Adapter: Complete
- ⏳ Deployment: Pending
- ⏳ Production Testing: Pending

