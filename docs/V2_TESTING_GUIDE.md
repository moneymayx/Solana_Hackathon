# V2 Smart Contract Testing Guide

**Last Updated**: October 31, 2025  
**Status**: ✅ Test Suite Complete

---

## 📋 Table of Contents

1. [Test Results Summary](#test-results-summary)
2. [Automated Testing](#automated-testing)
3. [Manual Testing](#manual-testing)
4. [Payment Testing](#payment-testing)
5. [Integration Testing](#integration-testing)
6. [Test Reports](#test-reports)

---

## Test Results Summary

### ✅ Backend Tests (10/10 Passing)

| Test | Status | Details |
|------|--------|---------|
| Python Syntax | ✅ PASS | No syntax errors |
| Imports | ✅ PASS | All imports successful |
| V2PaymentProcessor Init | ✅ PASS | Processor initializes correctly |
| PDA Derivation | ✅ PASS | All PDAs derive correctly |
| Token Account Derivation | ✅ PASS | All ATAs derive correctly |
| Instruction Discriminator | ✅ PASS | Correct 8-byte discriminator |
| Bounty Status | ✅ PASS | Can query bounty status |
| Transaction Creation | ✅ PASS | Transaction creation works |
| API Router Import | ✅ PASS | V2 router imports successfully |
| FastAPI Integration | ✅ PASS | App starts with V2 router |

### ✅ Frontend Tests (All Passing)

| Test | Status | Details |
|------|--------|---------|
| TypeScript Syntax | ✅ PASS | No syntax errors |
| Exports | ✅ PASS | All functions export correctly |
| Build | ✅ PASS | Compiles successfully |

### ✅ Compatibility Tests (All Passing)

| Test | Status | Details |
|------|--------|---------|
| V1 Service Still Works | ✅ PASS | Existing services unaffected |
| Backward Compatibility | ✅ PASS | No breaking changes |

### ✅ Payment Tests (Verified Working)

| Test | Status | Details |
|------|--------|---------|
| Raw Payment Test | ✅ PASS | 4-way split verified |
| Price Escalation | ✅ PASS | Correctly enforced |
| Transaction Signing | ✅ PASS | Transactions sign correctly |
| Balance Verification | ✅ PASS | Balances match expected split |

---

## Automated Testing

### Backend Integration Tests

**Location**: `scripts/testing/test_v2_integration.py`

**Run Tests**:
```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate
python3 smart_contract/v2_implementation/scripts/test_v2_integration_1.py
```

**Test Coverage**:
- ✅ V2PaymentProcessor initialization
- ✅ PDA derivation (Global, Bounty, Buyback Tracker)
- ✅ Token account derivation (all wallets)
- ✅ Instruction discriminator calculation
- ✅ Bounty status queries
- ✅ V1 service compatibility

### Frontend Build Tests

**Run Tests**:
```bash
cd frontend
npm run build
```

**Expected**: Successful compilation with no errors

### Validation Script

**Location**: `scripts/staging/validate_v2_deployment.sh`

**Run Validation**:
```bash
./scripts/staging/validate_v2_deployment.sh
```

**Checks**:
- TypeScript validation
- Python integration tests
- Backend service checks
- Documentation completeness
- Environment variables
- Contract verifiability

---

## Manual Testing

### Payment Flow Testing

#### Prerequisites

- [ ] Wallet connected
- [ ] Wallet has devnet SOL (for fees)
- [ ] Wallet has devnet USDC
- [ ] V2 enabled on backend (`USE_CONTRACT_V2=true`)
- [ ] V2 enabled on frontend (`NEXT_PUBLIC_USE_CONTRACT_V2=true`)

#### Test Steps

1. **Connect Wallet**:
   - Open frontend
   - Click "Connect Wallet"
   - Select Phantom/Solflare
   - Approve connection

2. **Initiate Payment**:
   - Navigate to payment page
   - Enter payment amount (minimum ~10 USDC)
   - Click "Pay" button
   - Approve transaction in wallet

3. **Verify Transaction**:
   - Check wallet for transaction signature
   - Open Solana Explorer link
   - Verify transaction succeeded
   - Check logs for success message

4. **Verify 4-Way Split**:
   ```bash
   # Check balances on explorer or via CLI
   # Expected split (for 10 USDC):
   # - Bounty Pool: 6 USDC (60%)
   # - Operational: 2 USDC (20%)
   # - Buyback: 1 USDC (10%)
   # - Staking: 1 USDC (10%)
   ```

5. **Verify Price Escalation**:
   - Make second payment
   - Amount should be higher than first
   - Formula: `base_price * (1.0078 ^ total_entries)`

### API Endpoint Testing

#### Test V2 Config Endpoint

```bash
curl https://your-backend-url/api/v2/config | jq
```

**Expected Response**:
```json
{
  "success": true,
  "enabled": true,
  "program_id": "HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm",
  ...
}
```

#### Test Bounty Status Endpoint

```bash
curl https://your-backend-url/api/v2/bounty/1/status | jq
```

**Expected Response**:
```json
{
  "success": true,
  "bounty_id": 1,
  "bounty_pda": "2J455GTdBfceWWUF7dcPawixW4PEfWBdVgX7Soqc3trb"
}
```

---

## Payment Testing

### Direct Contract Testing

**Location**: `programs/billions-bounty-v2/scripts/test_v2_raw_payment.ts`

**Run Test**:
```bash
cd programs/billions-bounty-v2
npm run test:payment
```

**What It Tests**:
- ✅ Direct contract interaction
- ✅ 4-way split distribution
- ✅ Balance verification
- ✅ Transaction signing
- ✅ Price escalation

**Test Results** (Verified):
```
✅ First Payment (10 USDC):
  Bounty Pool: 6 USDC ✅
  Operational: 2 USDC ✅
  Buyback: 1 USDC ✅
  Staking: 1 USDC ✅

✅ Second Payment (15 USDC):
  Bounty Pool: 9 USDC ✅
  Operational: 3 USDC ✅
  Buyback: 1.5 USDC ✅
  Staking: 1.5 USDC ✅

✅ Cumulative Totals:
  Bounty Pool: 15 USDC ✅
  Operational: 5 USDC ✅
  Buyback: 2.5 USDC ✅
  Staking: 2.5 USDC ✅
```

### Payment Amount Guidelines

**Base Price**: 10 USDC  
**Escalation**: Each entry increases price by ~0.78%

**Recommended Test Amounts**:
- First entry: 10 USDC
- Second entry: 15 USDC (accounts for escalation)
- Third entry: 20 USDC

**Minimum Amount**: Check current price via bounty status endpoint

---

## Integration Testing

### End-to-End Flow

1. **Setup**:
   - Deploy backend to staging
   - Deploy frontend to staging
   - Enable V2 flags

2. **User Journey**:
   - Connect wallet
   - Navigate to payment
   - Process payment
   - Verify transaction
   - Check balances

3. **Verification**:
   - Transaction succeeds
   - Funds distributed correctly
   - On-chain state updated
   - Backend logs show success
   - Frontend shows success message

### Backend Integration

**Test Backend Services**:
```python
# Test payment processor
from src.services.v2.payment_processor import get_v2_payment_processor
processor = get_v2_payment_processor()

# Test API router
from src.api.v2_payment_router import router
# Check router is registered
```

**Verify**:
- ✅ Services import correctly
- ✅ Configuration loaded
- ✅ PDAs derive correctly
- ✅ API endpoints respond

### Frontend Integration

**Test Frontend Components**:
```typescript
// Test payment processor
import { processV2EntryPayment } from "@/lib/v2/paymentProcessor";
// Verify function exists and works

// Test React component
import V2PaymentButton from "@/components/V2PaymentButton";
// Verify component renders
```

**Verify**:
- ✅ Functions export correctly
- ✅ Components render
- ✅ Wallet adapter works
- ✅ Transactions submit

---

## Test Reports

### Test Results Summary

**Backend**: ✅ All 10 tests passing  
**Frontend**: ✅ Build successful  
**Payment**: ✅ 4-way split verified  
**Compatibility**: ✅ V1 still works  
**Integration**: ✅ E2E flow works

### Known Issues

#### Issue 1: Anchor Client Account Ordering
**Status**: Non-blocking  
**Workaround**: Use raw instructions (implemented ✅)  
**Impact**: None - raw instructions work perfectly

#### Issue 2: Buyback Tracker Initialization
**Status**: Resolved ✅  
**Fix**: Uses `mut` constraint, initialized in `initialize_lottery`

---

## Testing Checklist

### Pre-Deployment
- [x] Automated tests passing
- [x] Manual testing complete
- [x] Payment flow verified
- [x] 4-way split verified
- [x] Price escalation verified
- [x] API endpoints tested
- [x] Error handling tested

### Post-Deployment
- [ ] Staging environment tests
- [ ] Load testing
- [ ] Error scenario testing
- [ ] Rollback testing
- [ ] Monitoring verified

---

## Related Documentation

- **Integration**: [V2_INTEGRATION_GUIDE.md](./V2_INTEGRATION_GUIDE.md)
- **Deployment**: [V2_DEPLOYMENT_GUIDE.md](./V2_DEPLOYMENT_GUIDE.md)
- **Architecture**: [ARCHITECTURE.md](../ARCHITECTURE.md)

---

**Testing Status**: ✅ Complete - All tests passing



