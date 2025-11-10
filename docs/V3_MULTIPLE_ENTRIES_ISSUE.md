# V3 Multiple Entries Issue - Historical Notes

> ✅ **Status:** Resolved by introducing per-wallet `entry_nonce` support (see `docs/V3_MULTIPLE_PAYMENTS_EXPLANATION.md` for the implemented solution).  
> This document is kept for historical context and outlines the original problem analysis prior to the fix.

## The Problem

The V3 contract currently allows **only ONE entry per user wallet per lottery**. This is a critical limitation that affects both testing and production.

### Current Contract Design

```rust
#[account(
    init,  // ← This requires the account to NOT exist
    payer = user,
    space = 8 + Entry::LEN,
    seeds = [b"entry", lottery.key().as_ref(), user.key().as_ref()],
    bump
)]
pub entry: Account<'info, Entry>,
```

**The entry PDA seeds:** `[b"entry", lottery, user]` where `user` is the signer.

### Why This Is a Problem

1. **Production Impact**: Users can only make **ONE payment ever** per lottery
2. **Testing Impact**: Backend wallet can only be used for **ONE test payment**
3. **Business Impact**: Users cannot contribute multiple times, limiting revenue

### Current Behavior

- ✅ First payment from a wallet: **SUCCESS** (entry created)
- ❌ Second payment from same wallet: **FAILS** (entry already exists)

## Solutions

### Option 1: Add Nonce to Entry Seeds (RECOMMENDED)

Modify the entry PDA to include a nonce/sequence number, allowing multiple unique entries per user:

```rust
#[account(
    init,
    payer = user,
    space = 8 + Entry::LEN,
    seeds = [b"entry", lottery.key().as_ref(), user.key().as_ref(), &entry_nonce.to_le_bytes()],
    bump
)]
pub entry: Account<'info, Entry>,
```

**Pros:**
- Allows unlimited entries per user
- Each entry is unique and trackable
- Backwards compatible (just adds a field)

**Cons:**
- Requires contract update and redeployment
- Frontend/backend need to track entry nonce

### Option 2: Use Timestamp in Seeds

Use current timestamp in seeds to make each entry unique:

```rust
seeds = [b"entry", lottery.key().as_ref(), user.key().as_ref(), &Clock::get()?.unix_timestamp.to_le_bytes()],
```

**Pros:**
- No need to track nonce
- Naturally unique per payment

**Cons:**
- Timestamps can collide (unlikely but possible)
- Less deterministic for testing

### Option 3: Change to `init_if_needed` and Aggregate

Allow updating the entry to accumulate multiple payments:

```rust
#[account(
    init_if_needed,
    payer = user,
    space = 8 + Entry::LEN,
    seeds = [b"entry", lottery.key().as_ref(), user.key().as_ref()],
    bump
)]
pub entry: Account<'info, Entry>,
```

Then modify the function to aggregate amounts:

```rust
entry.amount_paid += entry_amount;  // Accumulate instead of replace
entry.timestamp = Clock::get()?.unix_timestamp;  // Update timestamp
```

**Pros:**
- Simple change
- One entry per user aggregates all payments

**Cons:**
- Loses individual payment history
- Can't track separate entries for analytics
- `total_entries` count would be wrong

### Option 4: Use a Sequence Number from Lottery

Add a sequence counter to Lottery and increment for each entry:

```rust
pub struct Lottery {
    // ... existing fields ...
    pub entry_sequence: u64,  // New field
}
```

Then use in seeds:
```rust
seeds = [b"entry", lottery.key().as_ref(), user.key().as_ref(), &lottery.entry_sequence.to_le_bytes()],
```

And increment:
```rust
lottery.entry_sequence += 1;
```

**Pros:**
- Guaranteed unique
- Incremental sequence
- Tracks total entries properly

**Cons:**
- Requires Lottery struct change
- All entries share one sequence (not per-user)

## Recommended Solution: Option 1 (Nonce in Seeds)

This is the most flexible and allows proper tracking of individual entries while enabling multiple payments per user.

### Implementation Steps

1. **Update Rust Contract:**
   - Add `entry_nonce: u64` parameter to `process_entry_payment`
   - Update seeds to include nonce
   - Update Entry struct if needed (or use nonce just for uniqueness)

2. **Update Frontend:**
   - Track entry nonce per user (localStorage or backend)
   - Increment nonce for each payment
   - Pass nonce to payment function

3. **Update Backend:**
   - Track entry nonce per user (database)
   - Return nonce with payment requests
   - Pass nonce in instruction data

4. **Redeploy Contract:**
   - Rebuild V3 contract
   - Redeploy to devnet/mainnet
   - Update all integrations

## Temporary Testing Workaround

For testing purposes until the contract is fixed:

1. **Generate Unique Test Wallets:**
   - Create a new keypair for each test
   - Use that keypair as the backend wallet

2. **Use Entry Account Cleanup:**
   - Close existing entry accounts before reuse
   - Requires additional Solana instructions

3. **Test with Different User Wallets:**
   - Each test uses a different user wallet address
   - Entry PDA will be different per user

## Impact Assessment

**Current Status:**
- ❌ Production: Users can only pay once per lottery
- ❌ Testing: Backend wallet can only be used once
- ⚠️  Business: Severe limitation on user participation

**After Fix:**
- ✅ Production: Users can make unlimited payments
- ✅ Testing: Can test multiple times with same wallet
- ✅ Business: No artificial limits on participation

## Recommendation

**Immediate Action:** Implement Option 1 (Nonce in Seeds)
**Timeline:** Contract update, test, and redeploy
**Testing:** Verify multiple entries work per user wallet
**Production:** Deploy update before launch

This is a **critical bug** that must be fixed before production use.




