# V3 Lottery Initialization Status

**Date**: Current  
**Status**: ✅ **ALL FOUR BOUNTIES INITIALIZED ON DEVNET**

## Summary

- **Program ID**: `7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh`
- **USDC Mint (Mock Devnet Token)**: `JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh`
- **Initialization Method**: `node scripts/initialize_multi_bounty_raw.js`
- **Verification Script**: `npx tsx scripts/check_multi_bounty_status.ts`

## Jackpot Funding (Mock USDC)

The jackpot wallet (`CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF`) holds the mock USDC used for all bounties.

```
# Fund jackpot ATA with the mock mint (per docs/development/USDC_MINT_UPDATE.md)
spl-token mint JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh 100 \
  FxZ2AywgfAzi2a6SbuFBePbNytsTqzXXSYwApXdST5NG --url devnet
```

Current balance (after initialization): **115 USDC**.

## Initialization Details

| Bounty | Difficulty | PDA | Transaction |
| --- | --- | --- | --- |
| 1 – Claude Champ | Expert | `Gkh76vSp4jiBRAiZocc8njjD79NthEKnm5vXanDfFu1r` | [`4HMrmZCZ...`](https://explorer.solana.com/tx/4HMrmZCZWXR3HFrCdrnPhEfpQvFhY7ryY695m9SNvZmumMHCeycBpqb92bv56wVvuvepQxpL8r3X8nUDZpNVm7y4?cluster=devnet) |
| 2 – GPT Gigachad | Hard | `7cSHV3zegVido8o6LdPHDfFQvi1rbQkK6G8GPMsM9VBG` | [`3YGVYXRY...`](https://explorer.solana.com/tx/3YGVYXRY1Ho8bvtiiiuK8mRxabVEjjxujSXmPd5oxJGccNZQ8sj7NoEXciSwZc72JYRPeqD5ptN1njK5dTTHrLNm?cluster=devnet) |
| 3 – Gemini Great | Medium | `5Wf8srVoVjeQxaXw1y69EeU1fpWFiwLdFQ1hmPSRuq2X` | [`3vawA6jY...`](https://explorer.solana.com/tx/3vawA6jYYuRTaehMj8EkkrKFv2e8AcqhVmPL2guyso4xtFx1Cv8L5MSXF3KJ1JpJZD71oMjZx5uhdZBx5m7CKR2r?cluster=devnet) |
| 4 – Llama Legend | Easy | `5LKqypQHyBA8LmhgLL9HbqdwR9KpqnHJkrZvwFYNQRoJ` | [`3Vy6rnns...`](https://explorer.solana.com/tx/3Vy6rnnsUT93Ed1bAfSsWp4dhW38BGosJdrmBCTe1HJGvWNu3CuYgwGXU5Q8PQEKeRFU8yjXHHKoDsjCpQQP2ZV4?cluster=devnet) |

Each PDA derives from `[b"lottery", bounty_id]`, matching the multi-bounty contract changes.

## Scripts & Commands

| Purpose | Command |
| --- | --- |
| Initialize all four bounties (raw instruction flow) | `node scripts/initialize_multi_bounty_raw.js` |
| Check jackpot ATA balance | `spl-token account-info FxZ2AywgfAzi2a6SbuFBePbNytsTqzXXSYwApXdST5NG --url devnet` |
| Verify bounty PDAs + jackpot balance | `npx tsx scripts/check_multi_bounty_status.ts` |

## Verification Output (Sample)

```
npx tsx scripts/check_multi_bounty_status.ts

Program ID: 7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh
USDC Mint: JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh
Jackpot Wallet: CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF
Jackpot Balance: 115 USDC

Bounty 1 ... ✅ Lottery account exists (data length 179 bytes)
...
```

## Environment Variables

```
LOTTERY_PROGRAM_ID_V3=7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh
V3_USDC_MINT_DEVNET=JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh
V3_JACKPOT_WALLET=CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF
```

## Resources

- `scripts/initialize_multi_bounty_raw.js` – Devnet initializer (raw instructions)
- `scripts/check_multi_bounty_status.ts` – Status/reporting utility
- `docs/development/USDC_MINT_UPDATE.md` – Test-token background
- `docs/V3_CONFIG_UPDATE.md` – Environment variable reference

