# V2 Staging Deployment - Quick Start Guide

**Status**: ✅ Ready to Deploy  
**Last Validation**: October 30, 2024

---

## Pre-Flight Check ✈️

Run this command to validate everything is ready:
```
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty && ./scripts/staging/validate_v2_deployment.sh
```

Expected output: `🎉 All validations passed! (6/6)`

---

## Deployment Steps

### 1. Backend (DigitalOcean)

#### A. Set Environment Variables
Add these to your backend's `.env` file or export them:
```
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

#### B. Restart Backend
```
# SSH to your DigitalOcean server and restart your backend service
pm2 restart backend
```

#### C. Check Logs
```
pm2 logs backend | grep -i "v2\|error"
```

### 2. Frontend (Vercel)

#### A. Add Environment Variables
Go to Vercel Dashboard → Project → Settings → Environment Variables

Add to **Preview** environment:
```
NEXT_PUBLIC_USE_CONTRACT_V2=false
NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V2=HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm
```

#### B. Deploy Preview
First, create and push the staging-v2 branch:
```
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty && git checkout -b staging-v2 && git push -u origin staging-v2
```

Or if the branch already exists remotely, just push:
```
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty && git push origin staging-v2
```

---

## Testing Sequence

### Phase 1: Smoke Tests (V2 Disabled)
**Duration**: 30 minutes

- [ ] Backend starts without errors
- [ ] Frontend loads correctly
- [ ] Existing v1 lottery flows work
- [ ] No console errors
- [ ] No new errors in logs

**If any fail**: Fix before proceeding

### Phase 2: Enable V2
**Duration**: 2 hours

#### A. Enable Backend
```bash
export USE_CONTRACT_V2=true
pm2 restart backend
```

#### B. Test Entry Payment
```
# Replace with your actual staging API URL
curl -X POST https://your-staging-api.com/api/entry \
  -H "Content-Type: application/json" \
  -d '{"bounty_id": 1, "amount": 10000000}'
```

#### C. Verify On-Chain
Check Solana Explorer:
- Bounty pool wallet: https://explorer.solana.com/address/CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF?cluster=devnet
- Transaction should show 60/20/10/10 split

#### D. Test Price Escalation
```
# Second entry should require higher price (base_price * 1.0078)
# Verify rejection if amount is less than required
```

### Phase 3: Monitor
**Duration**: 24 hours

- [ ] Check logs every 2 hours
- [ ] Monitor transaction success rate
- [ ] Verify wallet balances match expected split
- [ ] No critical errors

---

## Rollback Plan 🔙

If anything goes wrong:

### 1. Disable V2 Immediately
```
# Backend (on DigitalOcean server)
export USE_CONTRACT_V2=false
pm2 restart backend

# Frontend (Vercel Dashboard)
# Go to Settings → Environment Variables
# Change NEXT_PUBLIC_USE_CONTRACT_V2 to false
# Redeploy from dashboard
```

### 2. Verify V1 Works
- Test existing lottery flows
- Check logs for errors
- Verify transactions succeed

### 3. Investigate
- Review logs: `pm2 logs backend --lines 100`
- Check Solana explorer for failed transactions
- Review error messages

---

## Success Criteria ✅

### Deployment Success
- [x] All validation tests pass
- [ ] Backend deployed with v2 env vars
- [ ] Frontend deployed with v2 env vars
- [ ] Smoke tests pass

### V2 Enabled Success
- [ ] Entry payment works
- [ ] 4-way split verified on-chain
- [ ] Price escalation works
- [ ] No critical errors for 24 hours
- [ ] Transaction success rate >95%

---

## Quick Commands

### Validation
```
# Full validation
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty && ./scripts/staging/validate_v2_deployment.sh

# Check devnet contract
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/programs/billions-bounty-v2 && ANCHOR_PROVIDER_URL=https://api.devnet.solana.com npx ts-node -T tests/devnet_simple_validation.ts

# Check backend integration
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty && source venv/bin/activate && python3 scripts/devnet/test_v2_integration.py
```

### Monitoring
```
# Backend logs (on DigitalOcean server)
pm2 logs backend --lines 50

# Check specific wallet balance
solana balance CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF --url devnet

# Check transaction
solana confirm <SIGNATURE> --url devnet
```

### Debugging
```
# Test backend service directly
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty && source venv/bin/activate && python3 -c "import sys; sys.path.insert(0, 'src'); from services.v2.contract_service import ContractServiceV2; import asyncio; s = ContractServiceV2(program_id='HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm'); result = asyncio.run(s.get_bounty_status(1)); print(result)"

# Check IDL
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty && anchor idl fetch --provider.cluster devnet HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm | head -20
```

---

## Explorer Links 🔍

- **Program**: https://explorer.solana.com/address/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm?cluster=devnet
- **Global PDA**: https://explorer.solana.com/address/BursCahsMxKjiSUgTCy11uUTWnaZ1eqcGcADUxiMzHMb?cluster=devnet
- **Bounty[1]**: https://explorer.solana.com/address/2J455GTdBfceWWUF7dcPawixW4PEfWBdVgX7Soqc3trb?cluster=devnet

---

## Documentation 📚

- **Full Checklist**: `docs/deployment/STAGING_CHECKLIST.md`
- **Staging Summary**: `docs/deployment/V2_STAGING_SUMMARY.md`
- **Completion Report**: `V2_COMPLETION_REPORT.md`
- **E2E Test Plan**: `docs/development/E2E_V2_TEST_PLAN.md`

---

## Emergency Contacts 🚨

If you encounter issues:
1. Check `docs/deployment/V2_STAGING_SUMMARY.md` for known issues
2. Review `V2_COMPLETION_REPORT.md` for architecture details
3. Rollback immediately if critical errors occur

---

**Remember**: Start with `USE_CONTRACT_V2=false` and only enable after smoke tests pass!

**Good luck! 🚀**

