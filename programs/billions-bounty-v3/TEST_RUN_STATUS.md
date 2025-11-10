# V3 Test Run Status

## ✅ Successfully Completed

1. **SOL Transfer from Kora Wallet**: 
   - ✅ Transferred 2 SOL from Kora wallet (`D4f9ArwgTuChKdgonTV8WFs3q1YtY9tHArF5zs4D5Vc5`)
   - ✅ Transferred 2.8 SOL more (total 4.8 SOL transferred)
   - ✅ Provider wallet now has **2.9 SOL** (sufficient for testing)

2. **Test Configuration Improvements**:
   - ✅ Reduced per-account funding from 0.5 SOL → 0.15 SOL
   - ✅ Reduced buffer from 1 SOL → 0.05 SOL  
   - ✅ Increased timeout from 2s → 60s
   - ✅ Added balance logging for debugging

## 🔍 Current Issue: "Unknown Signer" Error

### Error Details
```
Error: unknown signer: kkZUAjpTNysvU37aMb92p6pnhMcTRxT9mkDftqrAZ7L
at Transaction._addSignature
at Context.<anonymous> (tests/security_fixes.spec.ts:145:5)
```

This error occurs when calling `initializeLottery` at line 145 in `security_fixes.spec.ts`.

### Likely Cause

The error suggests Anchor is trying to sign a transaction with a keypair that wasn't provided in `.signers()`. The public key `kkZUAjpTNysvU37aMb92p6pnhMcTRxT9mkDftqrAZ7L` is likely the `jackpotWallet.publicKey`.

**Possible reasons:**
1. **Associated Token Account Creation**: The `associated_token::authority = jackpot_wallet` constraint in the Rust code might cause Anchor to try to create/verify the associated token account automatically, requiring the `jackpotWallet` keypair even though it's marked as `UncheckedAccount`.

2. **Account Already Exists**: We're manually creating the `jackpotTokenAccount` before calling `initializeLottery` (lines 113-118), but Anchor might be trying to recreate it or verify ownership.

3. **Account Name Mismatch**: The Rust struct uses `jackpot_wallet` (snake_case) but the test uses `jackpotWallet` (camelCase). Anchor should handle this automatically, but worth verifying.

### Next Steps to Debug

1. **Check if jackpotTokenAccount needs to be removed from accounts if it already exists**
2. **Verify the associated_token constraint isn't trying to create the account automatically**
3. **Add jackpotWallet keypair to signers temporarily to test** (even though it shouldn't be needed)
4. **Check if there's a mismatch between the PDA derivation and what Anchor expects**

### Test Code Location

```typescript
// Line 113-118: Manual creation of jackpot token account
jackpotTokenAccount = await createAccount(
  provider.connection,
  authority,
  usdcMint,
  jackpotWallet.publicKey  // <-- This is the owner
);

// Line 145-163: initializeLottery call (fails here)
await program.methods
  .initializeLottery(...)
  .accounts({
    ...
    jackpotWallet: jackpotWallet.publicKey,  // <-- Might need keypair?
    jackpotTokenAccount: jackpotTokenAccount,
    ...
  })
  .signers([authority])  // <-- Only authority, but maybe needs jackpotWallet?
  .rpc();
```

### Rust Code (lib.rs lines 491-495)

```rust
#[account(
    mut,
    associated_token::mint = usdc_mint,
    associated_token::authority = jackpot_wallet  // <-- This might auto-create
)]
pub jackpot_token_account: Account<'info, TokenAccount>,
```

The `associated_token::authority` constraint tells Anchor to derive the associated token account PDA. Since we're creating it manually first, Anchor might be confused or trying to verify it needs the authority.

---

## Summary

✅ **Funding issue resolved** - Provider wallet has sufficient SOL  
🔍 **New issue discovered** - "Unknown signer" error in `initializeLottery`  
📝 **Likely fix needed** - May need to adjust how the associated token account is handled or ensure Anchor recognizes the manually created account

The tests are very close to working - we just need to resolve this signing issue!

