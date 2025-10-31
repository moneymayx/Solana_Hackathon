# Billions Bounty - V2 Devnet Deployment Summary

**Last Updated**: October 31, 2025  
**Status**: ✅ **DEPLOYED & VERIFIED**

---

## Program Details

- **Program ID (devnet)**: `HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`
- **Network**: Solana Devnet
- **USDC Mint**: `JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh` (test token)

---

## Initialized PDAs

- **Global PDA**: `BursCahsMxKjiSUgTCy11uUTWnaZ1eqcGcADUxiMzHMb`
- **Bounty 1 PDA**: `2J455GTdBfceWWUF7dcPawixW4PEfWBdVgX7Soqc3trb`
- **Buyback Tracker PDA**: `9ceXx23oRrdAzdzUTzgj224y4KYhXN5eSug2CkJHpZpr`

---

## Wallet Configuration

- **Bounty Pool**: `CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF`
- **Operational**: `46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D`
- **Buyback**: `7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya`
- **Staking**: `Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX`

---

## Token Accounts (ATAs)

- **Bounty Pool ATA**: `FxZ2AywgfAzi2a6SbuFBePbNytsTqzXXSYwApXdST5NG`
- **Operational ATA**: `HTnqbKxh7aRgqUcej6UhRuagHgCkuQ81XeJus6LGpBrh`
- **Buyback ATA**: `AmaBFDcbHqFVQ2i2FTEpNivPNcvFd3fCK2FaCkrjecra`
- **Staking ATA**: `HFxDF6ud3kcS5kWNH9faxjRqfst5srZh8zkAcc4XzpxK`

---

## Initialization Transactions

- **initialize_lottery**: `wuBg9FscP71pHSzNE5jBGsdRVJtASE35WoBETAx8X6H43JSatHKdjzJvaa3psA3qv4KWL5WdRcvkXoBrJRoeKhF`
- **initialize_bounty (id=1)**: `4MNgLTDuJ49ZGrqGA9nctKF2MisGuNkQfq7Nu6jcnaLBW4deo8auUqjW55k9GhuBf38CZLm8zrKzrhuEWcwgxbUY`

---

## Test Transactions

- **Payment 1 (10 USDC)**: `mBitChScx3U35s1Kws3WoT2o3rtzT4Yf24H2ZXk5tjtQsJ1is4j5epC38aYW4EukDeBUGogqMMc8CZW6imR347v`
  - Distribution: 6/2/1/1 USDC ✅
- **Payment 2 (15 USDC)**: `33EPQo48gciNeZeJYDSnK21gyfMBD5DgUU9QqijLqdnBwFiSiBmtsmwZ2RCa5s44YXhSzujU3uDfwLeSWVddr67B`
  - Distribution: 9/3/1.5/1.5 USDC ✅

---

## IDL Status

- **Local IDL**: `programs/billions-bounty-v2/target/idl/billions_bounty_v2.json`
- **Status**: ✅ Generated and validated
- **Note**: Use raw Web3.js instructions for client integration (see `test_v2_raw_payment.ts`)

---

## Verification

- ✅ Program deployed and verified on devnet
- ✅ All PDAs initialized
- ✅ 4-way revenue split tested and verified (60/20/10/10)
- ✅ Price escalation working correctly
- ✅ Buyback tracker operational
- ✅ Raw payment test fully functional

---

## Integration Notes

**Recommended Approach**: Use raw Web3.js instructions via:
- Backend: `solana-py` or raw instruction building
- Frontend: `@solana/web3.js` directly
- Reference: `programs/billions-bounty-v2/scripts/test_v2_raw_payment.ts`

**Anchor Client**: Has account ordering issues - use raw instructions instead.

---

## Explorer Links

- **Program**: https://explorer.solana.com/address/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm?cluster=devnet
- **Global PDA**: https://explorer.solana.com/address/BursCahsMxKjiSUgTCy11uUTWnaZ1eqcGcADUxiMzHMb?cluster=devnet
- **Bounty PDA**: https://explorer.solana.com/address/2J455GTdBfceWWUF7dcPawixW4PEfWBdVgX7Soqc3trb?cluster=devnet
