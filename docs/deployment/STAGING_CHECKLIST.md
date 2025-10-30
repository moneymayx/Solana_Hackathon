# V2 Staging Deployment Checklist

## Pre-Deployment Validation ✅

### 1. Devnet Contract Status
- [x] Program deployed: `GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm`
- [x] IDL published: `HicBwRnacuFcfYXWGBFSCWofc8ZmJU4v4rKKxtxvXBQr`
- [x] Global PDA initialized: `F4YATUC3tEA3Gb3Tt3v7sZBT9iKRhHXJsZ6s7nBWKDgh`
- [x] Bounty[1] PDA initialized: `AJC6D2mvMcktdzpJJQmbYXkTZn9xGpd3qm4VAZK83Z`
- [x] Contract verifiable on Solana explorers

### 2. Documentation
- [x] Deployment summary created (`docs/deployment/V2_DEPLOYMENT_SUMMARY.md`)
- [x] Environment variables documented (`docs/development/STAGING_ENV_FLAGS.md`)
- [x] Integration plan documented (`docs/development/INTEGRATION_V2_PLAN.md`)
- [x] E2E test plan created (`docs/development/E2E_V2_TEST_PLAN.md`)

### 3. Testing
- [x] Devnet validation tests passed (4/5 - ATAs will be created on first use)
- [x] Program account verified
- [x] PDA accounts verified
- [x] IDL fetchable

## Staging Environment Setup

### Backend (DigitalOcean)

#### Environment Variables
Add these to your backend's `.env` file or export them on your DigitalOcean server:
```
USE_CONTRACT_V2=false
LOTTERY_PROGRAM_ID_V2=GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm
V2_GLOBAL_PDA=F4YATUC3tEA3Gb3Tt3v7sZBT9iKRhHXJsZ6s7nBWKDgh
V2_BOUNTY_1_PDA=AJC6D2mvMcktdzpJJQmbYXkTZn9xGpd2C3qm4VAZK83Z
V2_USDC_MINT=Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr
V2_BOUNTY_POOL_WALLET=CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF
V2_OPERATIONAL_WALLET=46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D
V2_BUYBACK_WALLET=7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya
V2_STAKING_WALLET=Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX
SOLANA_RPC_ENDPOINT=https://api.devnet.solana.com
```

#### Deployment Steps
1. SSH into DigitalOcean droplet
2. Navigate to backend directory
3. Set environment variables (add to `.env` or export)
4. Restart backend service
5. Verify logs show v2 config loaded

### Frontend (Vercel)

#### Environment Variables
Add these in Vercel Dashboard → Settings → Environment Variables:
```
NEXT_PUBLIC_USE_CONTRACT_V2=false
NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V2=GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm
NEXT_PUBLIC_API_URL=<your-staging-backend-url>
```

#### Deployment Steps
1. Go to Vercel dashboard
2. Navigate to project settings → Environment Variables
3. Add v2 variables to "Preview" environment
4. Redeploy preview branch
5. Test with `USE_CONTRACT_V2=false` first

## Staging Test Plan

### Phase 1: Smoke Tests (V2 Disabled)
- [ ] Backend starts successfully with v2 env vars
- [ ] Frontend loads without errors
- [ ] Existing v1 flows work normally
- [ ] No console errors related to v2

### Phase 2: V2 Validation (Backend Only)
- [ ] Set `USE_CONTRACT_V2=true` on backend
- [ ] Test entry payment endpoint
  - Verify 4-way split (60/20/10/10)
  - Check bounty pool increments
  - Check total_entries increments
- [ ] Test price escalation
  - First entry: base price
  - Second entry: escalated price
  - Reject payment below required price
- [ ] Test AI decision logging
  - Verify signature format check
  - Verify nonce anti-replay
- [ ] Monitor logs for errors

### Phase 3: Full E2E (Frontend + Backend)
- [ ] Enable `NEXT_PUBLIC_USE_CONTRACT_V2=true`
- [ ] Test complete user flow:
  1. Connect wallet
  2. Submit entry
  3. Verify transaction on explorer
  4. Check balances updated correctly
- [ ] Test edge cases:
  - Insufficient balance
  - Network errors
  - Transaction failures

### Phase 4: Load Testing
- [ ] Multiple concurrent entries
- [ ] Verify no race conditions
- [ ] Check gas/compute limits
- [ ] Monitor RPC rate limits

## Rollback Plan

### If Issues Detected
1. Set `USE_CONTRACT_V2=false` on backend
2. Set `NEXT_PUBLIC_USE_CONTRACT_V2=false` on frontend
3. Redeploy/restart services
4. Verify v1 flows restored
5. Investigate logs
6. Fix issues on devnet
7. Re-test before re-enabling

### Rollback Commands
```
# Backend (on DigitalOcean server)
export USE_CONTRACT_V2=false
pm2 restart backend

# Frontend (Vercel Dashboard)
# Go to Settings → Environment Variables
# Change NEXT_PUBLIC_USE_CONTRACT_V2 to false
# Redeploy from dashboard
```

## Success Criteria

- [ ] All smoke tests pass
- [ ] V2 validation tests pass
- [ ] E2E tests pass
- [ ] No errors in logs for 24 hours
- [ ] Transaction success rate > 95%
- [ ] Explorer shows correct transaction decoding

## Post-Deployment

### Monitoring
- Set up alerts for:
  - Transaction failures
  - RPC errors
  - Unexpected contract errors
- Monitor Solana explorer for transaction patterns
- Track wallet balances (bounty pool, operational, etc.)

### Documentation Updates
- [ ] Update README with v2 status
- [ ] Document any issues encountered
- [ ] Update runbooks with v2 procedures

## Mainnet Preparation

Once staging is stable for 7+ days:
- [ ] Review all staging metrics
- [ ] Audit smart contract code
- [ ] Generate mainnet keypairs
- [ ] Deploy to mainnet-beta
- [ ] Initialize with production wallets
- [ ] Publish mainnet IDL
- [ ] Update production env vars
- [ ] Gradual rollout (10% → 50% → 100%)

---

**Validation Script**: 
```
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty && ./scripts/staging/validate_v2_deployment.sh
```

**Last Updated**: October 30, 2024

