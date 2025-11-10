# Staging Deployment - Next Steps Guide

**Status**: Ready to proceed with staging deployment  
**Last Updated**: October 31, 2025

---

## ✅ Prerequisites (Already Done)

- [x] V2 contract deployed to devnet
- [x] All PDAs initialized
- [x] Payment flow tested and verified
- [x] Documentation updated with correct IDs
- [x] Environment variables documented

---

## 🎯 Phased Rollout Strategy

**Important**: We enable V2 in phases to test safely:

1. **Phase 1** (Steps 1-3): Both services start with V2 **disabled** (`false`)
   - Backend: `USE_CONTRACT_V2=false`
   - Frontend: `NEXT_PUBLIC_USE_CONTRACT_V2=false`
   - **Why?** Smoke tests to ensure nothing breaks

2. **Phase 2** (Step 4): Enable V2 on **backend only**
   - Backend: `USE_CONTRACT_V2=true` ✅
   - Frontend: `NEXT_PUBLIC_USE_CONTRACT_V2=false` (stays false)
   - **Why?** Test backend contract integration first, independently

3. **Phase 3** (Step 5): Enable V2 on **frontend** after backend is stable
   - Backend: `USE_CONTRACT_V2=true` ✅
   - Frontend: `NEXT_PUBLIC_USE_CONTRACT_V2=true` ✅
   - **Why?** Full E2E testing once backend is verified

**Key Point**: Backend and Frontend are separate services with separate flags. We test backend first, then frontend, to isolate issues.

### Quick Reference - Flag States by Phase

| Phase | Backend (DigitalOcean)<br/>`USE_CONTRACT_V2` | Frontend (Vercel)<br/>`NEXT_PUBLIC_USE_CONTRACT_V2` | Purpose |
|-------|:---:|:---:|---------|
| **Phase 1** | `false` | `false` | Smoke tests - ensure everything works with V2 disabled |
| **Phase 2** | `true` ✅ | `false` | Test backend contract integration independently |
| **Phase 3** | `true` ✅ | `true` ✅ | Full E2E testing after backend is verified |

---

## Step 1: Configure Backend (DigitalOcean App Platform)

### 1.1 Add Environment Variables

Go to: **DigitalOcean Dashboard → Your App → Settings → App-Level Environment Variables**

Add these variables (copy from STAGING_CHECKLIST.md lines 32-41):

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

**Note**: Keep `USE_CONTRACT_V2=false` initially for smoke tests.

### 1.2 Trigger Redeployment

After adding variables:
1. Go to **Deployments** tab
2. Click **"Force Rebuild"** or push a commit to trigger rebuild
3. Wait for deployment to complete
4. Check logs to verify environment variables are loaded

### 1.3 Verify Backend Started

Check the deployment logs for:
- ✅ No errors about missing environment variables
- ✅ Backend service started successfully
- ✅ API endpoints responding

**Test command:**
```bash
curl https://billions-bounty-iwnh3.ondigitalocean.app/api/lottery/status
```

---

## Step 2: Configure Frontend (Vercel)

### 2.1 Update Environment Variables

Go to: **Vercel Dashboard → Your Project → Settings → Environment Variables**

**Set for Preview environment:**

```bash
NEXT_PUBLIC_API_URL=https://billions-bounty-iwnh3.ondigitalocean.app
NEXT_PUBLIC_USE_CONTRACT_V2=false
```

**You can remove** (if they exist):
- `NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V2` (not needed - frontend doesn't use it)
- Any other `NEXT_PUBLIC_*` contract variables (frontend doesn't need them)

### 2.2 Redeploy Frontend

1. Go to **Deployments** tab
2. Find the latest deployment
3. Click **"Redeploy"**
4. Or push a commit to trigger auto-deployment

### 2.3 Verify Frontend Loads

Visit your frontend URL:
```
https://solana-hackathon-5ljqwcujg-jay-brantleys-projects.vercel.app/
```

Check:
- ✅ Page loads without errors
- ✅ No console errors
- ✅ Frontend can communicate with backend API

---

## Step 3: Phase 1 - Smoke Tests (V2 Disabled)

With `USE_CONTRACT_V2=false` on both services:

### 3.1 Test Existing V1 Flow

- [ ] Backend `/api/lottery/status` returns data
- [ ] Frontend loads and displays lottery info
- [ ] Existing payment flows work (if any)
- [ ] No console errors related to V2

### 3.2 Check Logs

**Backend logs** (DigitalOcean):
- No errors about missing V2 variables
- All API endpoints responding

**Frontend logs** (Vercel):
- No errors in browser console
- API requests succeeding

**If all pass → Proceed to Step 4**

---

## Step 4: Phase 2 - Enable V2 on Backend Only

**Why Backend Only?** We test the backend's contract integration first, independently. The frontend flag stays `false` during this phase so we can isolate backend issues.

### 4.1 Enable V2 Backend

In **DigitalOcean → Environment Variables**:
- Change `USE_CONTRACT_V2=false` → `USE_CONTRACT_V2=true`
- Save changes
- App will auto-redeploy

**Note**: Frontend (`NEXT_PUBLIC_USE_CONTRACT_V2`) stays `false` during this phase. We'll enable it in Step 5 after backend is verified.

### 4.2 Test V2 Backend Endpoints

Wait for deployment, then test:

```bash
# Check lottery status (should show V2 program ID)
curl https://billions-bounty-iwnh3.ondigitalocean.app/api/lottery/status

# Expected response should include:
# "program_id": "HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm"
```

### 4.3 Test Entry Payment (If Endpoint Exists)

Test a payment via API:
- [ ] Payment transaction succeeds
- [ ] 4-way split verified (check wallet balances)
- [ ] Price escalation working (test with minimum payment)
- [ ] Logs show no errors

### 4.4 Monitor for 24 Hours

- [ ] Watch DigitalOcean logs for errors
- [ ] Check transaction success rate
- [ ] Verify wallet balances are updating correctly
- [ ] No unexpected errors

**If all pass → Proceed to Step 5**

---

## Step 5: Phase 3 - Enable V2 on Frontend

### 5.1 Enable V2 Frontend

In **Vercel → Environment Variables**:
- Change `NEXT_PUBLIC_USE_CONTRACT_V2=false` → `NEXT_PUBLIC_USE_CONTRACT_V2=true`
- Save and redeploy

### 5.2 Test Full User Flow

1. Connect wallet
2. Submit entry payment
3. Verify transaction on explorer
4. Check wallet balances updated correctly

### 5.3 Test Edge Cases

- [ ] Insufficient balance handling
- [ ] Network error handling
- [ ] Transaction failure recovery
- [ ] Price escalation UI feedback

---

## Step 6: Phase 4 - Load Testing

- [ ] Multiple concurrent entries
- [ ] Verify no race conditions
- [ ] Check compute limits (should be fine)
- [ ] Monitor RPC rate limits

---

## Troubleshooting

### Backend Issues

**Problem**: Backend not starting
- Check DigitalOcean logs
- Verify all environment variables are set
- Check for typos in variable names/values

**Problem**: API errors
- Check backend logs
- Verify Solana RPC endpoint is accessible
- Check program ID and PDA addresses are correct

### Frontend Issues

**Problem**: Frontend can't connect to backend
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings on backend
- Test backend URL directly in browser

**Problem**: Environment variables not updating
- Clear Vercel build cache
- Force redeploy
- Check variable is set for correct environment (Preview vs Production)

---

## Rollback Plan

If issues occur:

1. **Backend**: Set `USE_CONTRACT_V2=false` in DigitalOcean
2. **Frontend**: Set `NEXT_PUBLIC_USE_CONTRACT_V2=false` in Vercel
3. Redeploy both services
4. Verify V1 flows restored
5. Investigate logs
6. Fix on devnet
7. Re-test before re-enabling

---

## Success Criteria

- [ ] All smoke tests pass
- [ ] V2 validation tests pass (backend only)
- [ ] Full E2E tests pass (frontend + backend)
- [ ] No errors in logs for 24 hours
- [ ] Transaction success rate > 95%
- [ ] Explorer shows correct transaction decoding

---

## Quick Reference

### Backend URL
```
https://billions-bounty-iwnh3.ondigitalocean.app
```

### Frontend URL
```
https://solana-hackathon-5ljqwcujg-jay-brantleys-projects.vercel.app/
```

### Program Explorer Link
```
https://explorer.solana.com/address/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm?cluster=devnet
```

---

## Next Steps After Staging

Once staging is stable for 7+ days:
1. Review all staging metrics
2. Audit smart contract code
3. Deploy to mainnet-beta
4. Update production environment variables
5. Gradual rollout (10% → 50% → 100%)

---

**Ready to start? Begin with Step 1! 🚀**

