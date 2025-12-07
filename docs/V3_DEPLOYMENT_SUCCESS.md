# V3 Deployment Success ✅

## Deployment Completed

**Program ID**: `7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh`
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
2. ✅ Initialize V3 multi-bounty accounts (see section below)
3. ✅ Verify V1, V2, V3 contracts are all initialized

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
   solana program extend 7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh 10000 --url devnet
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

---

## 2025-11-18 Multi-Bounty Initialization

- **USDC Mint**: `JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh` (mock devnet token with mint authority)
- **Jackpot Wallet**: `CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF`
- **Funding command** (sample):
  ```bash
  spl-token mint JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh 100 \
    FxZ2AywgfAzi2a6SbuFBePbNytsTqzXXSYwApXdST5NG --url devnet
  ```
- **Initializer**: `node scripts/initialize_multi_bounty_raw.js`
- **Verifier**: `npx tsx scripts/check_multi_bounty_status.ts`

| Bounty | PDA | Transaction |
| --- | --- | --- |
| 1 | `Gkh76vSp4jiBRAiZocc8njjD79NthEKnm5vXanDfFu1r` | [`4HMrmZCZ...`](https://explorer.solana.com/tx/4HMrmZCZWXR3HFrCdrnPhEfpQvFhY7ryY695m9SNvZmumMHCeycBpqb92bv56wVvuvepQxpL8r3X8nUDZpNVm7y4?cluster=devnet) |
| 2 | `7cSHV3zegVido8o6LdPHDfFQvi1rbQkK6G8GPMsM9VBG` | [`3YGVYXRY...`](https://explorer.solana.com/tx/3YGVYXRY1Ho8bvtiiiuK8mRxabVEjjxujSXmPd5oxJGccNZQ8sj7NoEXciSwZc72JYRPeqD5ptN1njK5dTTHrLNm?cluster=devnet) |
| 3 | `5Wf8srVoVjeQxaXw1y69EeU1fpWFiwLdFQ1hmPSRuq2X` | [`3vawA6jY...`](https://explorer.solana.com/tx/3vawA6jYYuRTaehMj8EkkrKFv2e8AcqhVmPL2guyso4xtFx1Cv8L5MSXF3KJ1JpJZD71oMjZx5uhdZBx5m7CKR2r?cluster=devnet) |
| 4 | `5LKqypQHyBA8LmhgLL9HbqdwR9KpqnHJkrZvwFYNQRoJ` | [`3Vy6rnns...`](https://explorer.solana.com/tx/3Vy6rnnsUT93Ed1bAfSsWp4dhW38BGosJdrmBCTe1HJGvWNu3CuYgwGXU5Q8PQEKeRFU8yjXHHKoDsjCpQQP2ZV4?cluster=devnet) |


