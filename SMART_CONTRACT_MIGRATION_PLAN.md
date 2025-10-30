# Smart Contract Migration Plan

**Date Created**: January 2025  
**Status**: Roadmap for Future Migration  
**Current State**: Backend handles most functionality; Contracts handle core payments & winner payouts

---

## Executive Summary

This document outlines discrepancies between backend implementations and smart contract capabilities. Currently, the backend handles most business logic while the smart contract manages core fund transfers. This document serves as a roadmap for migrating functionality to smart contracts before mainnet launch.

**Current Philosophy**: For now, all functionality is handled by the backend. This document outlines what needs to be migrated to smart contracts for full decentralization.

---

## Current State Analysis

### What the Smart Contract Currently Handles ✅

1. **Entry Payments** (`process_entry_payment`)
   - Accepts payment from users
   - Locks funds in jackpot wallet
   - Currently uses **80/20 split** (80% to jackpot, 20% operational fee)
   - Single transfer to jackpot wallet
   - **File**: `programs/billions-bounty/src/lib.rs` (lines 53-105)

2. **Winner Payouts** (`process_ai_decision`)
   - Transfers full jackpot to winner
   - Resets jackpot to floor amount
   - **File**: `programs/billions-bounty/src/lib.rs` (lines 107-199)

3. **Escape Plan Timer** (`execute_time_escape_plan`)
   - Tracks 24-hour timer on-chain
   - Distributes 20% to last participant
   - Emits event for backend to distribute remaining 80%
   - **File**: `programs/billions-bounty/src/lib.rs` (lines 244-294)

4. **NFT Verification** (`verify_nft_ownership`)
   - Verifies NFT ownership on-chain
   - Prevents duplicate verifications
   - **File**: `programs/billions-bounty/src/lib.rs` (NFT verification account exists)

### What the Backend Currently Handles ⚠️

1. **60/20/10/10 Revenue Split**
   - Backend calculates: 60% bounty, 20% operational, 10% buyback, 10% staking
   - Contract only does: 80% jackpot, 20% operational
   - **Location**: `src/services/smart_contract_service.py` (lines 238-242)

2. **Per-Bounty Tracking**
   - Backend maintains separate `Bounty` records with `current_pool` and `total_entries`
   - Contract uses single global lottery account
   - **Location**: `src/models.py` (`Bounty` model), `apps/backend/main.py` (bounty endpoints)

3. **Price Escalation**
   - Frontend calculates: `startingCost * 1.0078^totalEntries`
   - Backend tracks `total_entries` per bounty
   - Contract doesn't track or enforce pricing
   - **Location**: `frontend/src/app/bounty/[id]/page.tsx` (line 66)

4. **Referral System**
   - Complete backend service with database tracking
   - Zero contract integration
   - **Location**: `src/services/referral_service.py`, `src/models.py` (`Referral`, `ReferralCode`)

5. **Buyback Automation**
   - Backend monitoring service exists
   - No on-chain automation
   - **Location**: `src/services/buyback_service.py` (if exists)

6. **Team Bounties**
   - Full backend system with 8 database tables
   - No contract support for team prize distribution
   - **Location**: `src/services/team_service.py`, `src/models.py` (Team models)

7. **Staking Rewards**
   - Backend models exist (`StakingPosition` - now removed)
   - Compiled staking contract exists but **NO SOURCE CODE** in repository
   - **Location**: `programs/staking/` (binary only, no `.rs` files)

8. **AI Decision Verification**
   - Backend creates Ed25519 signatures
   - Contract verifies hash but has `TODO` for full Ed25519 verification
   - **Location**: `programs/billions-bounty/src/lib.rs` (line 134)

---

## Detailed Discrepancies

### 1. Revenue Split (60/20/10/10)

**Current Backend Implementation**:
```python
# src/services/smart_contract_service.py
bounty_pool_contribution_rate = 0.60
operational_fee_rate = 0.20
buyback_rate = 0.10
staking_rate = 0.10
```

**Current Contract Implementation**:
```rust
// programs/billions-bounty/src/lib.rs (lines 67-68)
let research_contribution = (entry_amount * 80) / 100;
let operational_fee = (entry_amount * 20) / 100;
// Single transfer to jackpot wallet (line 94)
```

**What Needs to Happen**:
- Contract needs 4 separate wallet transfers
- 60% to bounty pool wallet
- 20% to operational wallet
- 10% to buyback wallet
- 10% to staking rewards wallet

**Migration Complexity**: Medium  
**Priority**: High (before mainnet)

---

### 2. Per-Bounty Tracking

**Current Backend Implementation**:
```python
# src/models.py - Bounty model
class Bounty(Base):
    id: int
    current_pool: float
    total_entries: int
    # ... per-bounty state
```

**Current Contract Implementation**:
```rust
// programs/billions-bounty/src/lib.rs
// Single Lottery account, no per-bounty separation
pub struct Lottery {
    pub current_jackpot: u64,
    pub total_entries: u64,
    // ... global state
}
```

**What Needs to Happen**:
- Create separate `Bounty` PDA accounts per bounty ID
- Track `current_pool` and `total_entries` on-chain per bounty
- Update `process_entry_payment` to accept `bounty_id` parameter

**Migration Complexity**: High  
**Priority**: High (before mainnet)

---

### 3. Price Escalation

**Current Backend Implementation**:
```typescript
// frontend/src/app/bounty/[id]/page.tsx
const getCurrentQuestionCost = (): number => {
  return startingCost * Math.pow(1.0078, totalEntries)
}
```

**Current Contract Implementation**:
- No price tracking or enforcement
- Contract accepts any amount >= `research_fee`

**What Needs to Happen**:
- Contract needs to calculate price based on `total_entries` per bounty
- Enforce minimum payment amount on-chain
- Formula: `base_price * (1.0078 ^ total_entries)`

**Migration Complexity**: Medium  
**Priority**: Medium (post-launch enhancement)

---

### 4. Referral System

**Current Backend Implementation**:
- Complete referral service with database models
- Tracks referral codes, usage, free question grants
- **Files**: `src/services/referral_service.py`, `src/models.py`

**Current Contract Implementation**:
- No referral functionality

**What Needs to Happen**:
- Create `Referral` PDA account
- Track referral code usage on-chain
- Grant free questions via contract instruction
- Link referral rewards to on-chain state

**Migration Complexity**: High  
**Priority**: Low (future feature)

---

### 5. Buyback Automation

**Current Backend Implementation**:
- Backend monitoring service checks revenue periodically
- Executes buyback transactions manually
- **Location**: Buyback service (if exists)

**Current Contract Implementation**:
- No on-chain automation

**What Needs to Happen**:
- Create `Buyback` PDA account
- Implement automated buyback instruction
- Or use off-chain cron job that calls contract

**Migration Complexity**: Medium  
**Priority**: Medium (post-launch enhancement)

---

### 6. Team Bounties

**Current Backend Implementation**:
- Full team system with 8 database tables
- Team prize distribution logic
- **Files**: `src/services/team_service.py`, `src/models.py` (Team models)

**Current Contract Implementation**:
- No team functionality

**What Needs to Happen**:
- Create `Team` PDA account
- Track team members and contributions on-chain
- Implement team prize distribution contract method
- Split payments among team members

**Migration Complexity**: Very High  
**Priority**: Low (future feature)

---

### 7. Staking Rewards

**Current Backend Implementation**:
- `StakingPosition` model (removed)
- Revenue distribution service
- **Files**: `src/services/revenue_distribution_service.py`

**Current Contract Implementation**:
- Compiled binary exists: `programs/staking/target/deploy/staking.so`
- **NO SOURCE CODE** in repository

**What Needs to Happen**:
- Locate or recreate staking contract source code
- Implement staking, unstaking, and reward distribution
- Link to revenue distribution (10% of revenue)

**Migration Complexity**: High  
**Priority**: Medium (if staking is still desired)

---

### 8. NFT Verification Source Code

**Current State**:
- Contract binary exists: `programs/nft-verification/`
- NFT verification functionality exists in main contract
- **File**: `programs/billions-bounty/src/lib.rs` (NFT verification)

**What Needs to Happen**:
- Verify NFT verification source code is complete
- Document NFT verification flow
- Ensure source code matches deployed binary

**Migration Complexity**: Low  
**Priority**: Low (verification)

---

### 9. AI Signature Verification

**Current Backend Implementation**:
```python
# src/services/ai_decision_service.py
# Creates Ed25519 signatures
signature = self.private_key.sign(decision_hash)
```

**Current Contract Implementation**:
```rust
// programs/billions-bounty/src/lib.rs (line 134)
// TODO: Add proper Ed25519 signature verification
```

**What Needs to Happen**:
- Implement full Ed25519 signature verification in contract
- Verify signature against backend authority public key
- Prevent replay attacks

**Migration Complexity**: Medium  
**Priority**: High (security critical)

---

## Migration Priorities

### High Priority (Before Mainnet) 🔴

1. **Revenue Split (60/20/10/10)**
   - Critical for correct fund distribution
   - Must match documented split
   - **Estimated Effort**: 2-3 days

2. **Per-Bounty Tracking**
   - Required for multi-bounty support
   - Current global lottery won't scale
   - **Estimated Effort**: 3-5 days

3. **AI Signature Verification**
   - Security critical
   - Prevents unauthorized decision submissions
   - **Estimated Effort**: 1-2 days

### Medium Priority (Post-Launch Enhancements) 🟡

4. **Price Escalation**
   - Nice to have for fairness
   - Can be enforced off-chain initially
   - **Estimated Effort**: 2-3 days

5. **Buyback Automation**
   - Can use backend cron job initially
   - On-chain automation reduces trust
   - **Estimated Effort**: 2-3 days

6. **Staking Rewards**
   - Only if staking functionality is still desired
   - Requires source code recovery
   - **Estimated Effort**: 5-7 days

### Low Priority (Future Features) 🟢

7. **Referral System**
   - Backend implementation works fine
   - Migration adds complexity
   - **Estimated Effort**: 3-5 days

8. **Team Bounties**
   - Complex feature
   - Backend implementation sufficient
   - **Estimated Effort**: 7-10 days

---

## Migration Roadmap

### Phase 1: Critical Fixes (Week 1-2)

1. ✅ Update revenue split to 60/20/10/10
2. ✅ Implement per-bounty tracking
3. ✅ Add AI signature verification

**Files to Modify**:
- `programs/billions-bounty/src/lib.rs`
- `src/services/smart_contract_service.py`
- `apps/backend/main.py` (update contract calls)

### Phase 2: Post-Launch Enhancements (Month 2-3)

1. ✅ Implement on-chain price escalation
2. ✅ Add buyback automation (or verify backend cron)
3. ✅ Recover/implement staking contract

**Files to Modify**:
- `programs/billions-bounty/src/lib.rs`
- `programs/staking/src/lib.rs` (create if missing)

### Phase 3: Future Features (Month 4+)

1. ✅ Migrate referral system (if needed)
2. ✅ Add team bounty support (if needed)

---

## Implementation Guidelines

### When Migrating to Contract

1. **Always Start with Tests**
   - Write Anchor tests before implementation
   - Test edge cases (empty pools, overflow, etc.)

2. **Update Backend Integration**
   - Modify `smart_contract_service.py` to call new contract methods
   - Keep backend as fallback during migration

3. **Database Migration**
   - Plan data migration from backend to on-chain
   - Some data may remain in database for indexing

4. **Gradual Rollout**
   - Deploy to devnet first
   - Test thoroughly before mainnet
   - Can run backend + contract in parallel initially

### Testing Checklist

- [ ] Unit tests for contract logic
- [ ] Integration tests with backend
- [ ] Edge case testing (empty pools, max values, etc.)
- [ ] Security audit (signature verification, access control)
- [ ] Gas cost analysis
- [ ] End-to-end flow testing

---

## Current Backend Processes (Documented but Not Contract-Enforced)

### Revenue Distribution

**Backend Calculates**:
- 60% bounty pool contribution
- 20% operational fee
- 10% buyback allocation
- 10% staking rewards

**Contract Currently Does**:
- 80% to jackpot (single wallet)
- 20% operational fee
- No buyback/staking separation

**Status**: ⚠️ Discrepancy - Backend calculates 4-way split but contract only does 2-way

---

### Buyback Process

**Backend**: Monitors revenue, executes buyback transactions periodically  
**Contract**: No automation  
**Status**: ✅ Backend handles this (acceptable for now)

---

### Price Calculation

**Backend**: Tracks `total_entries` per bounty, calculates price  
**Contract**: No price enforcement  
**Status**: ⚠️ Backend calculates but contract doesn't verify

---

### Staking Rewards

**Backend**: `RevenueDistributionService` calculates distributions  
**Contract**: Binary exists but source code missing  
**Status**: ⚠️ Cannot verify or update staking contract

---

## Migration Todo List

### High Priority Todos

- [ ] **Update lottery contract for 4-wallet revenue split**
  - Modify `process_entry_payment` to make 4 transfers
  - Add buyback_wallet and staking_wallet accounts
  - Update initialization to accept all 4 wallets
  - **File**: `programs/billions-bounty/src/lib.rs`
  - **Estimated**: 2-3 days

- [ ] **Add per-bounty state tracking to contract**
  - Create `Bounty` PDA account structure
  - Add `bounty_id` parameter to `process_entry_payment`
  - Track `current_pool` and `total_entries` per bounty
  - Update all contract methods to accept `bounty_id`
  - **File**: `programs/billions-bounty/src/lib.rs`
  - **Estimated**: 3-5 days

- [ ] **Implement full Ed25519 signature verification**
  - Add proper signature verification in `process_ai_decision`
  - Verify against backend authority public key
  - Add replay attack prevention
  - **File**: `programs/billions-bounty/src/lib.rs` (line 134 TODO)
  - **Estimated**: 1-2 days

### Medium Priority Todos

- [ ] **Implement on-chain price escalation**
  - Add price calculation to contract
  - Formula: `base_price * (1.0078 ^ total_entries)`
  - Enforce minimum payment in `process_entry_payment`
  - **File**: `programs/billions-bounty/src/lib.rs`
  - **Estimated**: 2-3 days

- [ ] **Create or recover staking contract source**
  - Locate staking contract source code
  - Or recreate from requirements
  - Implement staking, unstaking, rewards
  - **File**: `programs/staking/src/lib.rs` (create if missing)
  - **Estimated**: 5-7 days

- [ ] **Add buyback automation to contract**
  - Create `Buyback` PDA account
  - Implement automated buyback instruction
  - Or document backend cron job process
  - **File**: `programs/billions-bounty/src/lib.rs` or documentation
  - **Estimated**: 2-3 days

### Low Priority Todos

- [ ] **Migrate referral system to contract**
  - Create `Referral` PDA account
  - Track referral code usage on-chain
  - Grant free questions via contract
  - **File**: `programs/billions-bounty/src/lib.rs` or new contract
  - **Estimated**: 3-5 days

- [ ] **Add team bounty support to contract**
  - Create `Team` PDA account structure
  - Implement team prize distribution
  - Track team members and contributions
  - **File**: `programs/billions-bounty/src/lib.rs` or new contract
  - **Estimated**: 7-10 days

- [ ] **Verify NFT verification source code**
  - Ensure source matches deployed binary
  - Document NFT verification flow
  - **File**: `programs/billions-bounty/src/lib.rs`
  - **Estimated**: 1 day

---

## Notes

- **Current State**: Backend handles most functionality correctly. This is acceptable for development and testing.
- **Migration Goal**: Move critical functions to smart contracts before mainnet launch for full decentralization.
- **Risk Assessment**: Gradual migration reduces risk. Backend can remain as fallback.
- **Testing**: All migrations must be tested on devnet before mainnet deployment.

---

## Related Files

- Contract: `programs/billions-bounty/src/lib.rs`
- Backend Service: `src/services/smart_contract_service.py`
- Backend Models: `src/models.py`
- Frontend: `frontend/src/app/bounty/[id]/page.tsx`
- API: `apps/backend/main.py`

---

**Last Updated**: January 2025  
**Next Review**: Before mainnet launch

