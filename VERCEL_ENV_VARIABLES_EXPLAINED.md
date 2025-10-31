# Vercel Environment Variables - Explained

## Key Point: Frontend vs Backend Variables

**The frontend (Vercel) does NOT need all those detailed contract variables!**

The frontend only talks to your backend API, not directly to the smart contract. So Vercel only needs minimal variables.

---

## What Goes in Vercel (Frontend)

### Required Variables:
```bash
# The backend API URL (where frontend sends requests)
NEXT_PUBLIC_API_URL=https://billions-bounty-iwnh3.ondigitalocean.app

# Optional: Feature flag to show/hide V2 UI elements (if you add them)
NEXT_PUBLIC_USE_CONTRACT_V2=false
```

### Optional (for future frontend direct contract integration):
```bash
# Only if you plan to have frontend interact directly with contract
NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V2=HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm
```

---

## What Goes in DigitalOcean (Backend)

**ALL the detailed contract variables** (from STAGING_CHECKLIST.md lines 32-41):

```bash
USE_CONTRACT_V2=false
LOTTERY_PROGRAM_ID_V2=HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm
V2_GLOBAL_PDA=BursCahsMxKjiSUgTCy11uUTWnaZ1eqcGcADUxiMzHMb
V2_BOUNTY_1_PDA=2J455GTdBfceWWUF7dcPawixW4PEfWBdVgX7Soqc3trb
V2_USDC_MINT=JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh
V2_BOUNTY_POOL_WALLET=CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF
V2_OPERATIONAL_WALLET=46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D
V2_BUYBACK_WALLET=7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya
V2_STAKING_WALLET=Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX
SOLANA_RPC_ENDPOINT=https://api.devnet.solana.com
```

**Why?** The backend needs these to:
- Connect to the smart contract
- Derive PDAs
- Send transactions
- Query contract state

---

## Why `NEXT_PUBLIC_*` Prefix?

In Next.js:
- **`NEXT_PUBLIC_*`** = Exposed to browser (client-side accessible)
- **No prefix** = Server-side only (not accessible in browser)

Since the frontend needs `NEXT_PUBLIC_API_URL` to know where to send API requests, it must have the `NEXT_PUBLIC_` prefix.

---

## Recommendation for Vercel

**Keep it simple - you only need:**

```bash
NEXT_PUBLIC_API_URL=https://billions-bounty-iwnh3.ondigitalocean.app
NEXT_PUBLIC_USE_CONTRACT_V2=false
```

**You can remove:**
- `NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V2` (unless you plan direct frontend contract integration)
- Any other `NEXT_PUBLIC_*` contract variables (frontend doesn't use them)

---

## Summary

- ✅ **Vercel (Frontend)**: Minimal variables - just API URL and feature flags
- ✅ **DigitalOcean (Backend)**: All the detailed contract variables from lines 32-41
- ✅ **Keep `NEXT_PUBLIC_*` in Vercel** - that's the correct naming convention
- ❌ **Don't put backend variables in Vercel** - they're not needed there

