# V3 Deployment Success ✅

## Deployment Completed

**Program ID**: `52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov`
**Network**: Devnet
**Date**: $(date)

## Deployment Method

Used the **two-step buffer method** to reduce upfront costs:
1. Created buffer account: `GeUS5zmdD26yjwbkwpC3qcTKkWFPbKGTj9RdJ9QeWSUp`
2. Deployed program from buffer using `--buffer` flag

## Cost Breakdown

- **Starting balance**: 3.92 SOL
- **Buffer creation**: ~3.42 SOL
- **Deployment from buffer**: ~0.002 SOL
- **Final balance**: ~0.495 SOL

## Key Insight

The full deployment (`solana program deploy` directly) requires ~4.18 SOL upfront. However, using `solana program write-buffer` first costs ~3.42 SOL, then deploying from the buffer only costs ~0.002 SOL, allowing deployment with less than 4.2 SOL total.

## Next Steps

1. ✅ Program deployed
2. ⏭️ Initialize V3 lottery account
3. ⏭️ Verify V1, V2, V3 contracts are all initialized

---

## 2025-11-10 Redeployment (Entry Nonce Update)

### Why
- Added `entry_nonce` support to `process_entry_payment`
- New binary grew from **490,968 bytes → 492,520 bytes**
- Existing program data account needed more space

### Actions
1. **Rebuilt with Anchor 0.28.0 / `cargo-build-sbf`**
2. **Extended program data account** to avoid `account data too small`:
   ```bash
   solana program extend 52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov 10000 --url devnet
   ```
3. **Uploaded new binary via buffer method:**
   ```bash
   solana program write-buffer target/deploy/billions_bounty_v3.so --url devnet
   solana program deploy --buffer <buffer_pubkey> \
     --program-id target/deploy/billions_bounty_v3-keypair.json \
     --url devnet
   ```
4. **Synced IDL changes manually** (`frontend/src/lib/v3/idl.json` → `target/idl/billions_bounty_v3.json`)

### Result
- Program redeployed at slot `420512958`
- Program data account now sized at **500,968 bytes** (extra headroom for future upgrades)

## Commands Used

```bash
# Step 1: Write buffer (costs ~3.42 SOL)
solana program write-buffer target/deploy/billions_bounty_v3.so --url devnet

# Step 2: Deploy from buffer (costs ~0.002 SOL)
solana program deploy --buffer GeUS5zmdD26yjwbkwpC3qcTKkWFPbKGTj9RdJ9QeWSUp \
  --program-id target/deploy/billions_bounty_v3-keypair.json \
  --url devnet
```

