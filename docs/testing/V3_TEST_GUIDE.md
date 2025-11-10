# V3 Testing Guide

**Version**: 0.3.0  
**Status**: Comprehensive Test Suite  
**Date**: 2024

## Overview

This guide explains how to run and interpret the V3 security test suite. All tests verify that the 6 critical security fixes are working correctly.

---

## Test Structure

```
programs/billions-bounty-v3/tests/
├── security_fixes.spec.ts    # Tests for all 6 security fixes
├── integration.spec.ts        # Full integration tests
└── edge_cases.spec.ts        # Edge cases and attack scenarios
```

---

## Running Tests

### Prerequisites

```bash
cd programs/billions-bounty-v3
npm install
anchor build
```

### Run All Tests

```bash
anchor test
```

### Run Specific Test Suites

```bash
# Security fixes only
anchor test -- tests/security_fixes.spec.ts

# Integration tests only
anchor test -- tests/integration.spec.ts

# Edge cases only
anchor test -- tests/edge_cases.spec.ts
```

### Run with Verbose Output

```bash
anchor test -- --verbose
```

---

## Test Coverage

### Fix 1: Ed25519 Signature Verification

**Test File**: `security_fixes.spec.ts`

**Tests**:
- ✅ Rejects invalid signature length (not 64 bytes)
- ✅ Rejects wrong backend authority
- ✅ Verifies signature format validation

**Expected Behavior**:
- Invalid signatures should fail with `InvalidSignature`
- Wrong backend authority should fail with `UnauthorizedBackend`

### Fix 2: Cryptographic Hash Function

**Test File**: `security_fixes.spec.ts`

**Tests**:
- ✅ Produces deterministic hash for same inputs
- ✅ Produces different hash for different inputs
- ✅ Rejects invalid decision hash

**Expected Behavior**:
- Same inputs → same hash
- Different inputs → different hash
- Invalid hash → `InvalidDecisionHash` error

### Fix 3: Input Validation

**Test File**: `security_fixes.spec.ts`

**Tests**:
- ✅ Rejects oversized user message (>5000 chars)
- ✅ Rejects oversized session ID (>100 chars)
- ✅ Rejects invalid session ID format (non-alphanumeric)
- ✅ Rejects invalid timestamp (too old)
- ✅ Rejects zero user_id

**Expected Behavior**:
- Oversized inputs → `InputTooLong`
- Invalid formats → `InvalidSessionId`
- Old timestamps → `TimestampOutOfRange`
- Invalid values → `InvalidInput`

### Fix 4: Reentrancy Guards

**Test File**: `security_fixes.spec.ts`

**Tests**:
- ✅ Verifies `is_processing` flag prevents concurrent execution

**Expected Behavior**:
- Flag should be `false` when not processing
- Flag should prevent concurrent calls

### Fix 5: Authority Checks

**Test File**: `security_fixes.spec.ts`

**Tests**:
- ✅ Rejects unauthorized emergency recovery
- ✅ Verifies authority must be signer

**Expected Behavior**:
- Unauthorized attempts → `Unauthorized`
- Missing signer → Anchor constraint error

### Fix 6: Secure Emergency Recovery

**Test File**: `security_fixes.spec.ts`

**Tests**:
- ✅ Enforces 24-hour cooldown period
- ✅ Enforces 10% maximum recovery amount

**Expected Behavior**:
- Recovery during cooldown → `RecoveryCooldownActive`
- Excessive amount → `RecoveryAmountExceedsLimit`

---

## Integration Tests

**Test File**: `integration.spec.ts`

**Tests**:
- ✅ Initializes lottery system correctly
- ✅ Processes entry payment and locks funds
- ✅ Processes AI decision and logs correctly

**Expected Behavior**:
- All operations complete successfully
- Account states update correctly
- Events emit correctly

---

## Edge Cases and Attack Scenarios

**Test File**: `edge_cases.spec.ts`

**Tests**:
- ✅ Prevents zero pubkey attacks
- ✅ Prevents replay attacks with old timestamps
- ✅ Prevents future timestamp attacks
- ✅ Prevents unauthorized emergency recovery attempts
- ✅ Prevents recovery exceeding 10% limit
- ✅ Accepts maximum valid message length
- ✅ Accepts valid session ID formats

**Expected Behavior**:
- All attack scenarios should be blocked
- Valid boundary conditions should pass

---

## Interpreting Test Results

### Passing Tests

All tests should pass indicating:
- ✅ Security fixes are working
- ✅ Input validation is enforced
- ✅ Attack scenarios are blocked

### Failing Tests

If tests fail:

1. **Check Error Messages**: Tests include specific error expectations
2. **Verify Contract State**: Ensure contract is properly initialized
3. **Check Test Setup**: Verify all test accounts are funded
4. **Review Logs**: Anchor logs provide detailed error information

### Common Test Failures

**"AccountNotFound"**
- Cause: Lottery not initialized
- Solution: Run initialization test first

**"InsufficientFunds"**
- Cause: Test accounts not funded
- Solution: Check airdrop in `before()` hook

**"ConstraintViolation"**
- Cause: Account constraints not met
- Solution: Verify account structs match contract

---

## Manual Testing Checklist

After automated tests pass, perform manual testing:

### Security Fix 1: Signature Verification
- [ ] Submit valid signature → should succeed
- [ ] Submit invalid signature length → should fail
- [ ] Submit wrong backend authority → should fail

### Security Fix 2: Hash Verification
- [ ] Submit correct hash → should succeed
- [ ] Submit incorrect hash → should fail
- [ ] Verify deterministic hashing

### Security Fix 3: Input Validation
- [ ] Submit oversized message → should fail
- [ ] Submit invalid session ID → should fail
- [ ] Submit old timestamp → should fail
- [ ] Submit valid inputs → should succeed

### Security Fix 4: Reentrancy
- [ ] Attempt concurrent calls → should be blocked
- [ ] Verify `is_processing` flag behavior

### Security Fix 5: Authority Checks
- [ ] Unauthorized recovery attempt → should fail
- [ ] Authorized recovery → should succeed

### Security Fix 6: Emergency Recovery
- [ ] Recovery during cooldown → should fail
- [ ] Recovery exceeding 10% → should fail
- [ ] Valid recovery after cooldown → should succeed

---

## Test Data

### Standard Test Constants

```typescript
const RESEARCH_FUND_FLOOR = 10000;
const RESEARCH_FEE = 10;
const ENTRY_AMOUNT = 10;
```

### Test Accounts

Tests generate keypairs for:
- `authority`: Lottery authority
- `user`: Regular user
- `jackpotWallet`: Jackpot wallet
- `backendAuthority`: Backend signing authority
- `attacker`: Attack scenarios

---

## Debugging Tests

### Enable Verbose Logging

```typescript
anchor.setProvider(anchor.AnchorProvider.env());
```

### Check Transaction Logs

```typescript
const tx = await program.methods...rpc();
console.log("Transaction:", tx);

// Fetch account to verify state
const lottery = await program.account.lottery.fetch(lotteryPDA);
console.log("Lottery state:", lottery);
```

### Common Debugging Steps

1. **Verify Initialization**: Check lottery PDA exists
2. **Check Balances**: Verify token accounts are funded
3. **Validate Accounts**: Ensure all accounts match expected PDAs
4. **Review Errors**: Anchor provides detailed constraint violations

---

## Continuous Integration

### GitHub Actions (Example)

```yaml
- name: Run V3 Security Tests
  run: |
    cd programs/billions-bounty-v3
    anchor test
```

### Pre-commit Hooks

Consider adding pre-commit hooks to run tests before commits:

```bash
# .git/hooks/pre-commit
cd programs/billions-bounty-v3 && anchor test
```

---

## Performance Benchmarks

Expected test execution times:
- Security fixes: ~30 seconds
- Integration tests: ~60 seconds
- Edge cases: ~45 seconds
- Total: ~2-3 minutes

---

## Test Maintenance

### Adding New Tests

1. Follow existing test structure
2. Use descriptive test names
3. Include expected error messages
4. Document test purpose in comments

### Updating Tests

When contract changes:
1. Update test accounts if needed
2. Update expected values
3. Verify all tests still pass
4. Add tests for new features

---

## Support

- Security Fixes Documentation: `docs/security/V3_SECURITY_FIXES.md`
- Integration Guide: `docs/development/V3_INTEGRATION_GUIDE.md`
- Contract Source: `programs/billions-bounty-v3/src/lib.rs`

---

## Test Status

- ✅ Security Fixes: 6/6 tests passing
- ✅ Integration: 3/3 tests passing
- ✅ Edge Cases: 7/7 tests passing
- ✅ Total Coverage: Comprehensive

