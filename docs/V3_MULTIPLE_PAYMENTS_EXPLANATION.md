# V3 Multiple Payments - Fix Implemented

## Summary

✅ **Status:** Multiple entries per wallet are now supported in both testing and production.  
✅ **Contract:** `process_entry_payment` accepts an `entry_nonce` and derives the entry PDA using `[b"entry", lottery, signer, entry_nonce]`.  
✅ **Frontend:** Keeps a per-wallet nonce in `localStorage` and passes it to every payment.  
✅ **Backend (test mode):** Tracks nonces in the new `v3_entry_nonce_tracker` table so backend-funded payments remain unique.  
✅ **Events & Accounts:** The `Entry` account and `EntryProcessed` event now expose the nonce for analytics and debugging.

## Contract Changes

```rust
pub fn process_entry_payment(
    ctx: Context<ProcessEntryPayment>,
    entry_amount: u64,
    user_wallet: Pubkey,
    entry_nonce: u64,
) -> Result<()> {
    // ... existing validation ...
    entry.entry_nonce = entry_nonce;
    // Seeds now include entry_nonce for uniqueness
}

#[derive(Accounts)]
#[instruction(entry_amount: u64, user_wallet: Pubkey, entry_nonce: u64)]
pub struct ProcessEntryPayment<'info> {
    #[account(
        init,
        payer = user,
        space = 8 + Entry::LEN,
        seeds = [
            b"entry",
            lottery.key().as_ref(),
            user.key().as_ref(),
            &entry_nonce.to_le_bytes()
        ],
        bump
    )]
    pub entry: Account<'info, Entry>,
    // ... remaining accounts ...
}

#[account]
pub struct Entry {
    pub user_wallet: Pubkey,
    pub amount_paid: u64,
    pub research_contribution: u64,
    pub operational_fee: u64,
    pub timestamp: i64,
    pub is_processed: bool,
    pub entry_nonce: u64,
}
```

## Frontend Updates

File: `frontend/src/lib/v3/paymentProcessor.ts`

- `computeNextEntryNonce()` reads + increments the last nonce from `localStorage`
- `findEntryPDA()` appends `serializeU64(entryNonce)` when deriving the PDA
- `instructionData` appends the nonce (u64 LE) so Anchor decodes it
- Account metas now include `userWallet` (unchecked) and `ASSOCIATED_TOKEN_PROGRAM_ID`
- After successful transactions we persist the nonce so subsequent payments continue sequentially

The backend test mode path sends the nonce along with the request so server and client stay in sync:

```ts
const nextEntryNonce = computeNextEntryNonce(userWallet);
const response = await fetch("/api/v3/payment/test", {
  body: JSON.stringify({
    user_wallet: userWallet.toBase58(),
    entry_amount: entryAmount,
    amount_usdc: entryAmount / 1_000_000,
    entry_nonce: nextEntryNonce,
  }),
});
```

On success the frontend persists either the server-confirmed nonce or the client guess:

```ts
if (typeof result.entry_nonce === "number") {
  persistEntryNonce(userWallet, result.entry_nonce);
} else {
  persistEntryNonce(userWallet, nextEntryNonce);
}
```

## Backend Updates

File: `apps/backend/api/v3_payment_router.py`

- Introduced `V3EntryNonceTracker` model imported from `src.models`
- Backend computes the authoritative nonce (`current_nonce + 1`) per `user_wallet`
- Nonces are written to the database *after* a successful `send_transaction`
- Responses now include the nonce so the frontend can commit it locally

```python
result = await session.execute(
    select(V3EntryNonceTracker).where(V3EntryNonceTracker.wallet_address == request.user_wallet)
)
nonce_record = result.scalars().first()
if not nonce_record:
    nonce_record = V3EntryNonceTracker(wallet_address=request.user_wallet, current_nonce=0)
    session.add(nonce_record)

entry_nonce = nonce_record.current_nonce + 1
nonce_record.current_nonce = entry_nonce
...
await session.commit()
return { "entry_nonce": entry_nonce, ... }
```

## Database Schema

New model: `V3EntryNonceTracker`

```python
class V3EntryNonceTracker(Base):
    __tablename__ = "v3_entry_nonce_tracker"
    id = mapped_column(Integer, primary_key=True, index=True)
    wallet_address = mapped_column(String(255), unique=True, index=True)
    current_nonce = mapped_column(Integer, default=0)
    updated_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

Run a migration (or recreate tables for SQLite) so this table exists.  The automated test `tests/database/test_v3_entry_nonce_tracker.py` verifies sequential increments for a wallet.

## Testing Checklist

1. **Unit Test:** `pytest tests/database/test_v3_entry_nonce_tracker.py`
2. **Backend:** Call `/api/v3/payment/test` twice for the same `user_wallet` and confirm:
   - `entry_nonce` increments (1, 2, ...)
   - Transaction signatures differ
   - `entry_pda` changes with each nonce
3. **Frontend (Wallet Adapter):** Run two real payments from the same wallet and verify the second transaction succeeds and creates a distinct entry account

## Rollout Notes

- Regenerate the Anchor IDL (requires `anchor-cli 0.31.2`) and redeploy the contract to staging/devnet
- Update ENV files:
  - `NEXT_PUBLIC_PAYMENT_MODE` can stay `test_contract` for QA
  - No additional flags are required; nonce management is automatic
- Clear local storage for testers to avoid stale nonce values from the previous implementation

With these changes, wallets can confidently submit multiple entries without clashing PDAs, unlocking real repeated participation in both test and production environments.
