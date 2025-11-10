# V3 Configuration Update Guide

## Updated Values (2024)

**New V3 Program ID**: `52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov`  
**Old V3 Program ID**: `ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb` (replaced)

**V3 Lottery PDA**: `HsZZAW2hPyeewapZEGrNJWgnHKc1mQU34oLuBXJUSV2x`

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
LOTTERY_PROGRAM_ID_V3=52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov
V3_BACKEND_AUTHORITY=CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF
V3_USDC_MINT_DEVNET=JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh
```

### Frontend (.env.local or Vercel)
```bash
NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V3=52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov
NEXT_PUBLIC_V3_USDC_MINT=JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh
NEXT_PUBLIC_USE_CONTRACT_V3=true
```

## Verification

The PDA is automatically derived from the program ID, but you can verify:

```javascript
const { PublicKey } = require('@solana/web3.js');
const PROGRAM_ID = new PublicKey('52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov');
const [lotteryPDA] = PublicKey.findProgramAddressSync(
  [Buffer.from('lottery')],
  PROGRAM_ID
);
console.log('Lottery PDA:', lotteryPDA.toBase58());
// Should output: HsZZAW2hPyeewapZEGrNJWgnHKc1mQU34oLuBXJUSV2x
```

## Deployment Status

✅ Program deployed to devnet  
✅ Lottery PDA initialized  
✅ Ready for payments  

## Next Steps

1. Update environment variables in deployment platforms (DigitalOcean, Vercel)
2. Restart services to pick up new configs
3. Test V3 payment processing
4. Monitor for any issues

