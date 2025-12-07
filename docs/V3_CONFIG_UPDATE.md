# V3 Configuration Update Guide

## Updated Values (2024)

**New V3 Program ID**: `7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh`  
**Old V3 Program ID**: `52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov` (superseded)

**Multi-Bounty PDAs** (derived with `[b"lottery", bounty_id]` seeds):
- Bounty 1: `Gkh76vSp4jiBRAiZocc8njjD79NthEKnm5vXanDfFu1r`
- Bounty 2: `7cSHV3zegVido8o6LdPHDfFQvi1rbQkK6G8GPMsM9VBG`
- Bounty 3: `5Wf8srVoVjeQxaXw1y69EeU1fpWFiwLdFQ1hmPSRuq2X`
- Bounty 4: `5LKqypQHyBA8LmhgLL9HbqdwR9KpqnHJkrZvwFYNQRoJ`

## Files Updated

### Frontend
- ✅ `frontend/src/lib/v3/paymentProcessor.ts` - Updated default PROGRAM_ID
- ✅ `frontend/src/lib/v3/idl.json` - Updated address field

### Backend
- ✅ `src/services/contract_adapter_v3.py` - Updated default program ID

### Documentation
- ✅ `docs/development/STAGING_ENV_FLAGS.md` - Updated environment variable examples

## Environment Variables

### Backend (.env)
```bash
LOTTERY_PROGRAM_ID_V3=7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh
V3_BACKEND_AUTHORITY=CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF
V3_USDC_MINT_DEVNET=JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh
```

### Frontend (.env.local or Vercel)
```bash
NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V3=7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh
NEXT_PUBLIC_V3_USDC_MINT=JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh
NEXT_PUBLIC_USE_CONTRACT_V3=true
```

## Verification

The PDA is automatically derived from the program ID, but you can verify:

```javascript
const { PublicKey } = require('@solana/web3.js');
const PROGRAM_ID = new PublicKey('7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh');
const [bounty1] = PublicKey.findProgramAddressSync(
  [Buffer.from('lottery'), Buffer.from([1])],
  PROGRAM_ID
);
console.log('Bounty 1 PDA:', bounty1.toBase58());
```

## Deployment Status

✅ Program deployed to devnet  
✅ All four bounty PDAs initialized via `scripts/initialize_multi_bounty_raw.js`  
✅ Ready for multi-bounty payments  

## Next Steps

1. Update environment variables in deployment platforms (DigitalOcean, Vercel)
2. Restart services to pick up new configs
3. Test V3 payment processing
4. Monitor for any issues

