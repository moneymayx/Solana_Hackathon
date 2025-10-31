# V2 Smart Contract Deployment Guide

**Last Updated**: October 31, 2025  
**Status**: ✅ Deployed on Devnet  
**Network**: Solana Devnet

---

## 📋 Table of Contents

1. [Deployment Status](#deployment-status)
2. [Contract Details](#contract-details)
3. [Initialization](#initialization)
4. [Enabling V2](#enabling-v2)
5. [Staging Deployment](#staging-deployment)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Deployment Status

### Current Deployment ✅

**Program ID**: `HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`  
**Network**: Solana Devnet  
**Status**: ✅ Deployed, Initialized, and Verified

**Explorer**: https://explorer.solana.com/address/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm?cluster=devnet

### Initialized Accounts (PDAs)

- **Global PDA**: `BursCahsMxKjiSUgTCy11uUTWnaZ1eqcGcADUxiMzHMb`
- **Bounty 1 PDA**: `2J455GTdBfceWWUF7dcPawixW4PEfWBdVgX7Soqc3trb`
- **Buyback Tracker PDA**: `9ceXx23oRrdAzdzUTzgj224y4KYhXN5eSug2CkJHpZpr`

### Wallet Configuration

- **Bounty Pool**: `CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF`
- **Operational**: `46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D`
- **Buyback**: `7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya`
- **Staking**: `Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX`

### SPL Token Mint

- **USDC Mint (Devnet Test Token)**: `JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh`

---

## Contract Details

### Features Implemented

#### Phase 1 ✅
- 4-way revenue split (60/20/10/10)
- Per-bounty tracking (pool size, entry count)
- AI decision verification (signature format + hash)
- Anti-replay protection (nonce-based)

#### Phase 2 ✅
- Price escalation (1.0078^n formula)
- Buyback primitive (allocate + execute)

#### Phase 3 & 4 ✅ (Implemented, Needs E2E Testing)
- Referral system
- Team bounties

### IDL Status

**IDL Account**: Published on devnet  
**Status**: ✅ Verifiable on Solana explorers

**Fetch IDL**:
```bash
anchor idl fetch --provider.cluster devnet HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm
```

---

## Initialization

### Initialization Transactions

1. **Global PDA Initialization**:
   - Transaction: `wuBg9FscP71pHSzNE5jBGsdRVJtASE35WoBETAx8X6H43JSatHKdjzJvaa3psA3qv4KWL5WdRcvkXoBrJRoeKhF`

2. **Bounty 1 Initialization**:
   - Transaction: `4MNgLTDuJ49ZGrqGA9nctKF2MisGuNkQfq7Nu6jcnaLBW4deo8auUqjW55k9GhuBf38CZLm8zrKzrhuEWcwgxbUY`

### Initialization Script

Use `programs/billions-bounty-v2/scripts/init_v2_raw.ts` for initialization:

```bash
cd programs/billions-bounty-v2
npm run init:devnet
```

**Note**: Research fund floor set to `0` for devnet initialization only.

---

## Enabling V2

### Backend (DigitalOcean)

1. Go to DigitalOcean App Platform
2. Navigate to your app → Settings → Environment Variables
3. Set `USE_CONTRACT_V2=true`
4. Save (auto-deploys in 2-5 minutes)

**Required Variables**:
```bash
USE_CONTRACT_V2=true
LOTTERY_PROGRAM_ID_V2=HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm
V2_GLOBAL_PDA=BursCahsMxKjiSUgTCy11uUTWnaZ1eqcGcADUxiMzHMb
V2_BOUNTY_1_PDA=2J455GTdBfceWWUF7dcPawixW4PEfWBdVgX7Soqc3trb
V2_USDC_MINT=JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh
V2_BOUNTY_POOL_WALLET=CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF
V2_OPERATIONAL_WALLET=46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D
V2_BUYBACK_WALLET=7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya
V2_STAKING_WALLET=Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX
```

### Frontend (Vercel)

1. Go to Vercel Dashboard
2. Navigate to your project → Settings → Environment Variables
3. Add V2 variables (see Configuration section)
4. Redeploy

**Required Variables**:
```bash
NEXT_PUBLIC_USE_CONTRACT_V2=true
NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V2=HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm
# ... (other NEXT_PUBLIC_* variables)
```

### Verification

Check that V2 is active:

```bash
# Backend
curl https://your-backend-url/api/lottery/status | jq .program_id

# Should return: "HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm"
```

Check logs for:
```
🆕 Using V2 smart contract
```

---

## Staging Deployment

### Phased Rollout Strategy

#### Phase 1: Backend Only
1. Enable `USE_CONTRACT_V2=true` on backend
2. Keep `NEXT_PUBLIC_USE_CONTRACT_V2=false` on frontend
3. Monitor backend logs for 24 hours
4. Test backend endpoints

#### Phase 2: Full Integration
1. Enable `NEXT_PUBLIC_USE_CONTRACT_V2=true` on frontend
2. Test payment flow end-to-end
3. Verify 4-way split
4. Monitor for 48 hours

### Staging Checklist

- [ ] Backend deployed to DigitalOcean
- [ ] Frontend deployed to Vercel
- [ ] Environment variables set
- [ ] V2 flag enabled on backend
- [ ] Backend logs show "🆕 Using V2 smart contract"
- [ ] API endpoints responding correctly
- [ ] Payment flow tested
- [ ] 4-way split verified
- [ ] Error handling tested
- [ ] Rollback plan ready

### Monitoring

**Check Backend Logs**:
- Look for V2 initialization messages
- Monitor for errors
- Verify transaction signatures

**Check Frontend**:
- Wallet connection works
- Payment button appears
- Transactions submit successfully

---

## Production Deployment

### Prerequisites

- [ ] Staging testing complete
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Rollback plan documented
- [ ] Monitoring setup
- [ ] Alerting configured

### Deployment Steps

1. **Update Environment Variables**:
   - Set `USE_CONTRACT_V2=true` in production
   - Verify all V2 variables are set

2. **Deploy Backend**:
   - Push to production branch
   - DigitalOcean auto-deploys
   - Monitor deployment logs

3. **Deploy Frontend**:
   - Merge to production
   - Vercel auto-deploys
   - Verify deployment

4. **Verify**:
   - Check API endpoints
   - Test payment flow
   - Monitor for errors

### Rollback Procedure

If issues occur:

1. **Backend Rollback**:
   - Set `USE_CONTRACT_V2=false` in DigitalOcean
   - Wait for auto-redeploy
   - Verify V1 is active

2. **Frontend Rollback**:
   - Set `NEXT_PUBLIC_USE_CONTRACT_V2=false` in Vercel
   - Redeploy
   - Verify V1 UI

**Rollback Time**: < 5 minutes (feature flag controlled)

---

## Troubleshooting

### Issue: Backend Not Switching to V2

**Problem**: `USE_CONTRACT_V2=true` but backend still uses V1.

**Fix**: Ensure `SmartContractService` checks the flag (already fixed in codebase).

**Verify**:
```python
# Check logs for:
🆕 Using V2 smart contract  # V2 active
📌 Using V1 smart contract  # V1 active
```

### Issue: IDL Not Found

**Problem**: Cannot fetch IDL from chain.

**Solution**: IDL is published on devnet. Use:
```bash
anchor idl fetch --provider.cluster devnet HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm
```

### Issue: Transaction Fails

**Problem**: Payment transactions failing.

**Possible Causes**:
1. Insufficient SOL for fees
2. Insufficient USDC balance
3. Price escalation - amount too low
4. Account not initialized

**Solution**: Check transaction logs on explorer for specific error.

### Issue: Environment Variables Not Loading

**Problem**: Backend not reading V2 variables.

**Fix**:
1. Verify variables in DigitalOcean dashboard
2. Restart application
3. Check `.env` file (local) or DigitalOcean env vars (production)

---

## Related Documentation

- **Integration**: [V2_INTEGRATION_GUIDE.md](./V2_INTEGRATION_GUIDE.md)
- **Testing**: [V2_TESTING_GUIDE.md](../V2_TESTING_GUIDE.md)
- **Architecture**: [ARCHITECTURE.md](../ARCHITECTURE.md)
- **Staging Checklist**: `docs/deployment/STAGING_CHECKLIST.md`

---

**Deployment Status**: ✅ Ready for production deployment on devnet



