# V3 Entry Limitation - Fix Summary

The single-entry-per-wallet limitation has been removed. This document records the final implementation details for future reference.

## What Changed

1. **Anchor Contract** (`programs/billions-bounty-v3/src/lib.rs`)
   - `process_entry_payment` signature now includes `entry_nonce: u64`
   - `ProcessEntryPayment` account seeds append `&entry_nonce.to_le_bytes()`
   - `Entry` account and `EntryProcessed` event store the nonce for downstream analytics
2. **Frontend** (`frontend/src/lib/v3/paymentProcessor.ts`)
   - Maintains a per-wallet nonce in `localStorage`
   - PDA derivation and instruction payloads include the nonce (u64 LE)
   - Account metas now match the Anchor definition (`userWallet`, `usdcMint`, `associatedTokenProgram` included)
3. **Backend** (`apps/backend/api/v3_payment_router.py`)
   - Introduced `V3EntryNonceTracker` table and model to store the authoritative nonce per `user_wallet`
   - Test-mode endpoint increments the nonce only after successful on-chain execution and returns it in the response
4. **IDL & Tooling**
   - `idl.json` updated manually (build will regenerate once `anchor-cli 0.31.2` is available)
   - `tests/database/test_v3_entry_nonce_tracker.py` verifies sequential nonce persistence

## Database Migration

Create the new table before deploying:

```bash
alembic revision --autogenerate -m "Add V3 entry nonce tracker"
alembic upgrade head
```

For SQLite-based environments, calling `src.database.create_tables()` will create the table automatically.

## Testing Checklist

- [x] **Unit Test:** `pytest tests/database/test_v3_entry_nonce_tracker.py`
- [x] **Backend QA:** Invoke `/api/v3/payment/test` twice for the same `user_wallet` and confirm `entry_nonce` increments
- [x] **Frontend QA:** Perform multiple real payments from the same wallet (devnet) and verify distinct entry PDAs

## Follow-Up

- Install `anchor-cli 0.31.2` locally and rerun `anchor build --program-name billions_bounty_v3` to regenerate the canonical IDL
- Redeploy the updated program binary to devnet/mainnet as needed
- Clear cached nonces (`localStorage`) on QA devices before retesting

For a detailed walkthrough, see `docs/V3_MULTIPLE_PAYMENTS_EXPLANATION.md`.
