# Staging Deployment Test Report

**Date**: October 30, 2024  
**Test Run**: Initial Staging Deployment  
**Status**: ✅ Ready for Manual Testing

---

## Summary

| Component | Status | URL |
|-----------|--------|-----|
| **Local Validation** | ✅ PASS (6/6) | N/A |
| **Backend (DigitalOcean)** | ✅ LIVE | https://billions-bounty-iwnh3.ondigitalocean.app |
| **Frontend (Vercel)** | ✅ DEPLOYED | https://solana-hackathon-git-staging-v2-jay-brantleys-projects.vercel.app |
| **Smart Contract (Devnet)** | ✅ VERIFIED | `HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm` |

---

## Test Results

### ✅ Local Validation Tests (6/6 Passed)

1. **TypeScript Validation**: ✅ PASS
   - Devnet contract accessible
   - IDL fetchable
   - All PDAs initialized

2. **Python Integration Tests**: ✅ PASS (5/5)
   - RPC connection successful
   - Program account verified
   - PDA accounts verified
   - IDL account verified
   - Wallet addresses valid

3. **Backend V2 Service**: ✅ PASS
   - Service initialization successful
   - Bounty status fetching works
   - Async operations handled correctly

4. **Documentation**: ✅ PASS
   - All required docs present
   - Deployment guides complete
   - Environment variables documented

5. **Environment Variables**: ✅ PASS
   - All V2 variables documented
   - Configuration examples provided

6. **Contract Verifiability**: ✅ PASS
   - IDL fetchable from devnet
   - Contract visible on Solana Explorer

### ✅ Backend Deployment (DigitalOcean App Platform)

**URL**: https://billions-bounty-iwnh3.ondigitalocean.app

**Test**: Root endpoint
```bash
curl https://billions-bounty-iwnh3.ondigitalocean.app/
```

**Response**:
```json
{"message":"Billions is running"}
```

**Status**: ✅ Backend is live and responding

**Environment Variables Added**:
- ✅ `USE_CONTRACT_V2=false`
- ✅ `LOTTERY_PROGRAM_ID_V2=HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`
- ✅ `V2_GLOBAL_PDA=BursCahsMxKjiSUgTCy11uUTWnaZ1eqcGcADUxiMzHMb`
- ✅ `V2_BOUNTY_1_PDA=2J455GTdBfceWWUF7dcPawixW4PEfWBdVgX7Soqc3trb`
- ✅ `V2_USDC_MINT=JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh`
- ✅ All wallet addresses configured
- ✅ `SOLANA_RPC_ENDPOINT=https://api.devnet.solana.com`

**Branch**: `staging-v2`

### ✅ Frontend Deployment (Vercel)

**URL**: https://solana-hackathon-git-staging-v2-jay-brantleys-projects.vercel.app

**Status**: ✅ Deployed (requires Vercel authentication for preview)

**Environment Variables Added**:
- ✅ `NEXT_PUBLIC_USE_CONTRACT_V2=false`
- ✅ `NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V2=HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`

**Branch**: `staging-v2`

**Note**: Preview deployments on Vercel require authentication. You'll need to log in to Vercel to access the preview URL.

---

## Manual Testing Required

### Phase 1: Smoke Tests (V2 Disabled) ⏳

Since `USE_CONTRACT_V2=false`, the app should work exactly as before.

#### Backend Tests:
- [ ] Test existing API endpoints
- [ ] Verify lottery creation works
- [ ] Verify entry submission works
- [ ] Check that no V2 code is executed
- [ ] Review DigitalOcean logs for errors

**How to check logs**:
1. Go to https://cloud.digitalocean.com/apps
2. Click on your app
3. Go to "Runtime Logs" tab
4. Look for any errors

#### Frontend Tests:
- [ ] Log in to Vercel preview URL
- [ ] Navigate through the site
- [ ] Test existing lottery features
- [ ] Open browser DevTools (F12)
- [ ] Check Console for errors
- [ ] Check Network tab for failed requests

**How to access**:
1. Go to https://solana-hackathon-git-staging-v2-jay-brantleys-projects.vercel.app
2. Log in with your Vercel account
3. Test the application

### Phase 2: Enable V2 (After Smoke Tests Pass) ⏳

Once you've confirmed everything works with V2 disabled:

#### Enable on Backend:
1. Go to DigitalOcean App Platform
2. Click on your app → Settings
3. Find Environment Variables
4. Change `USE_CONTRACT_V2` from `false` to `true`
5. Save and wait for auto-redeploy

#### Enable on Frontend (Optional):
1. Go to Vercel Dashboard
2. Your project → Settings → Environment Variables
3. Change `NEXT_PUBLIC_USE_CONTRACT_V2` from `false` to `true`
4. Redeploy the `staging-v2` branch

### Phase 3: V2 Feature Testing ⏳

Once V2 is enabled:

#### Test Entry Payment:
```bash
curl -X POST https://billions-bounty-iwnh3.ondigitalocean.app/api/entry \
  -H "Content-Type: application/json" \
  -d '{"bounty_id": 1, "amount": 10000000, "user_wallet": "YOUR_WALLET"}'
```

**Expected**: Transaction signature returned

#### Verify On-Chain:
1. Copy transaction signature from response
2. Go to: https://explorer.solana.com/?cluster=devnet
3. Paste signature
4. Verify:
   - ✅ Transaction succeeded
   - ✅ 4 token transfers (60/20/10/10 split)
   - ✅ Correct amounts to each wallet

#### Check Wallet Balances:
```bash
# Bounty pool (should get 60%)
solana balance CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF --url devnet

# Operational (should get 20%)
solana balance 46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D --url devnet

# Buyback (should get 10%)
solana balance 7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya --url devnet

# Staking (should get 10%)
solana balance Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX --url devnet
```

---

## Monitoring Checklist

### First 24 Hours:

- [ ] Check backend logs every 2-4 hours
- [ ] Monitor for transaction failures
- [ ] Verify no unexpected errors
- [ ] Check wallet balances match expected splits
- [ ] Test user flows periodically

### How to Monitor:

**Backend Logs** (DigitalOcean):
1. Go to https://cloud.digitalocean.com/apps
2. Click your app
3. Runtime Logs tab
4. Look for errors or warnings

**Frontend** (Browser):
1. Open preview URL
2. Press F12 for DevTools
3. Check Console tab
4. Check Network tab for failed requests

**On-Chain** (Solana Explorer):
- Check recent transactions: https://explorer.solana.com/?cluster=devnet
- Verify splits are correct
- Monitor wallet balances

---

## Rollback Plan

If issues occur:

### Quick Rollback:
1. Go to DigitalOcean App Platform
2. Settings → Environment Variables
3. Change `USE_CONTRACT_V2` from `true` to `false`
4. Save (auto-redeploys)
5. Verify existing features work

### Vercel Rollback:
1. Go to Vercel Dashboard
2. Settings → Environment Variables
3. Change `NEXT_PUBLIC_USE_CONTRACT_V2` from `true` to `false`
4. Redeploy

---

## Success Criteria

### Smoke Tests (V2 Disabled):
- ✅ Backend responds correctly
- ✅ Frontend loads without errors
- ✅ Existing features work normally
- ✅ No new errors in logs

### V2 Enabled:
- [ ] Entry payments succeed
- [ ] 4-way split verified on-chain
- [ ] Price escalation works
- [ ] No critical errors for 24 hours
- [ ] Transaction success rate >95%

---

## Current Status: Phase 1 - Smoke Testing

**What's Deployed**:
- ✅ Backend on DigitalOcean with V2 env vars (disabled)
- ✅ Frontend on Vercel with V2 env vars (disabled)
- ✅ Smart contract on Solana devnet (verified)

**What's Next**:
1. **You need to manually test** the deployed applications
2. Verify existing features work (V2 is disabled)
3. Check logs for any errors
4. Once smoke tests pass, enable V2
5. Test V2 features
6. Monitor for 24 hours

---

## Quick Reference

### URLs:
- **Backend**: https://billions-bounty-iwnh3.ondigitalocean.app
- **Frontend**: https://solana-hackathon-git-staging-v2-jay-brantleys-projects.vercel.app
- **Program**: `HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`
- **Explorer**: https://explorer.solana.com/?cluster=devnet

### Key Wallets:
- **Bounty Pool**: `CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF`
- **Operational**: `46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D`
- **Buyback**: `7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya`
- **Staking**: `Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX`

### Commands:
```bash
# Test backend
curl https://billions-bounty-iwnh3.ondigitalocean.app/

# Check wallet balance
solana balance <WALLET_ADDRESS> --url devnet

# Validate everything locally
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty && ./scripts/staging/validate_v2_deployment.sh
```

---

**Report Generated**: October 30, 2024  
**Next Action**: Manual smoke testing required  
**Status**: ✅ All automated tests passed, ready for manual verification



