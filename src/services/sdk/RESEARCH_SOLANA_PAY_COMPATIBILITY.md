# Solana Pay Compatibility Research - V2 Contract Analysis

## V2 Contract Requirements Analysis

### Current V2 Payment Instruction

**Location**: `programs/billions-bounty-v2/src/lib.rs` - `process_entry_payment_v2`

**Instruction Requirements**:
1. **Custom Instruction Format**:
   - Discriminator: `process_entry_payment_v2`
   - Data: `bounty_id (u64)` + `entry_amount (u64)`
   
2. **Account Requirements** (17 accounts):
   - PDAs: global, bounty, buybackTracker
   - User: wallet + token account
   - 4 Destination token accounts (bounty pool, operational, buyback, staking)
   - 4 Destination wallets (read-only)
   - Program IDs: mint, token program, associated token program, system program, rent sysvar

3. **Multi-Recipient Split**:
   - 60% → Bounty pool
   - 20% → Operational
   - 10% → Buyback
   - 10% → Staking
   - All in single instruction with 4 CPI transfers

## Solana Pay Compatibility Research

### Transfer Requests (Simple Payments)
**Status**: ❌ Not Compatible
- **Why**: Transfer requests only support simple SOL/SPL token transfers
- **V2 Need**: Custom instruction with PDAs and multi-recipient split
- **Conclusion**: Cannot use transfer requests for V2 contract

### Transaction Requests (Interactive Payments)
**Status**: ⏳ Needs Research

**What to Research**:
1. **Can Transaction Requests Include Custom Instructions?**
   - Solana Pay Transaction Request spec
   - Support for arbitrary instruction data
   - Support for multiple instructions

2. **Account Support**:
   - Can Transaction Requests include PDA accounts?
   - Can they specify all 17 accounts needed?
   - Account ordering requirements?

3. **Multi-Recipient Support**:
   - Can Transaction Request include multiple transfers in one transaction?
   - Or would need multiple instructions?

**Research Sources**:
- Solana Pay Transaction Request spec: https://docs.solanapay.com/core/transaction-request
- Example implementations with custom instructions

### Hybrid Approach

**Concept**: Use Solana Pay URL format but build custom instruction client-side

**Flow**:
1. Generate Solana Pay transaction request URL
2. Wallet opens URL
3. Backend handler receives request
4. Backend builds V2 custom instruction
5. Returns transaction to wallet
6. User signs and sends

**Research Needed**:
- Does Solana Pay Transaction Request support this pattern?
- How do wallets handle custom instruction building?
- Can we specify custom program in transaction request?

## Compatibility Assessment

### Current Assessment

| Feature | V2 Contract Needs | Solana Pay Supports | Compatible? |
|---------|-------------------|---------------------|-------------|
| Custom Instructions | ✅ Required | ⏳ Transaction Requests? | ⏳ Unknown |
| PDAs | ✅ Required (3 PDAs) | ⏳ Need to verify | ⏳ Unknown |
| Multi-Recipient | ✅ Required (4-way split) | ❌ Not in transfer requests | ❌ No |
| Account Ordering | ✅ Critical (17 accounts) | ⏳ Need to verify | ⏳ Unknown |
| Instruction Discriminator | ✅ Required | ⏳ Need to verify | ⏳ Unknown |

## Research Action Items

1. **Review Transaction Request Spec**:
   - Read full Transaction Request specification
   - Check support for custom program instructions
   - Verify account and instruction format flexibility

2. **Test Transaction Request**:
   - Create test transaction request with custom instruction
   - Test with Phantom/Solflare wallet
   - Verify if it works

3. **Hybrid Approach Test**:
   - Test backend handler pattern
   - See if wallets support custom instruction building

## Recommendations

### Based on Current Analysis:
- **Transfer Requests**: ❌ Not compatible - too simple
- **Transaction Requests**: ⏳ Unknown - needs research
- **Hybrid Approach**: ⏳ Possibly feasible - needs testing

### Likely Outcome:
- Solana Pay will NOT work directly for V2 contract
- May be able to use Transaction Request with custom instruction handler
- Current custom implementation is probably the right approach

---

**Status**: Transfer requests confirmed incompatible, Transaction Requests need research

