# V2 Smart Contract Switch Fix

**Date**: October 31, 2025  
**Status**: ✅ FIXED

---

## 🐛 Problem Discovered

The backend was **NOT** switching to V2 even when `USE_CONTRACT_V2=true` was set in DigitalOcean.

### Root Cause:
The `SmartContractService` class (used by `/api/lottery/status` and other endpoints) was **hardcoded** to only use the V1 program ID:

```python
# OLD CODE (BROKEN):
self.program_id = Pubkey.from_string(os.getenv(
    "LOTTERY_PROGRAM_ID",  # <-- Always V1!
    "4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK"
))
```

### Symptoms:
- API returned V1 program ID: `Bjek6uN5WzxZtjVvyghpsa57GzVaxXYQ8Lpg2CfPAMGW`
- Expected V2 program ID: `GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm`
- Setting `USE_CONTRACT_V2=true` had no effect on `SmartContractService`

---

## ✅ Solution

Updated `src/services/smart_contract_service.py` to check the `USE_CONTRACT_V2` flag and switch between V1 and V2 program IDs:

```python
# NEW CODE (FIXED):
use_v2 = os.getenv("USE_CONTRACT_V2", "false").lower() == "true"

if use_v2:
    # Use V2 program ID
    self.program_id = Pubkey.from_string(os.getenv(
        "LOTTERY_PROGRAM_ID_V2",
        "GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm"
    ))
    logger.info("🆕 Using V2 smart contract")
else:
    # Use V1 program ID
    self.program_id = Pubkey.from_string(os.getenv(
        "LOTTERY_PROGRAM_ID",
        "4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK"
    ))
    logger.info("📌 Using V1 smart contract")
```

---

## 🚀 Deployment Steps

### 1. Commit and Push Fix
```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
git add src/services/smart_contract_service.py V2_SWITCH_FIX.md
git commit -m "fix: SmartContractService now respects USE_CONTRACT_V2 flag"
git push origin staging-v2
```

### 2. DigitalOcean Will Auto-Deploy
- DigitalOcean detects the push
- Auto-deploys in 2-3 minutes
- No manual action needed

### 3. Verify After Deploy
```bash
# Check that program_id switches to V2
curl -s https://billions-bounty-iwnh3.ondigitalocean.app/api/lottery/status | python3 -m json.tool

# Expected output:
# "program_id": "GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm"  ✅
```

---

## 📊 Environment Variables Required

Make sure these are set in DigitalOcean:

```bash
# Enable V2
USE_CONTRACT_V2=true

# V2 Program ID
LOTTERY_PROGRAM_ID_V2=GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm

# V2 Wallets
BOUNTY_POOL_WALLET=CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF
OPERATIONAL_WALLET=46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D
BUYBACK_WALLET=7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya
STAKING_WALLET=Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX

# V2 Token
USDC_MINT=Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr
```

---

## 🎯 Impact

### Before Fix:
- ❌ V2 flag ignored by `SmartContractService`
- ❌ Always used V1 contract
- ❌ V2 features unavailable

### After Fix:
- ✅ Respects `USE_CONTRACT_V2` flag
- ✅ Switches to V2 when enabled
- ✅ Logs which version is active
- ✅ Can toggle V2 on/off instantly

---

## 🔍 Testing Checklist

After deployment:

- [ ] `/api/lottery/status` returns V2 program ID
- [ ] Logs show "🆕 Using V2 smart contract"
- [ ] Entry payments route through V2 contract
- [ ] 4-way split (60/20/10/10) works correctly
- [ ] Can rollback to V1 by setting `USE_CONTRACT_V2=false`

---

## 📝 Related Files

- `src/services/smart_contract_service.py` - Main fix
- `src/services/contract_adapter_v2.py` - Already had V2 switch (working)
- `LOTTERY_STATUS_FIX.md` - Previous fix for `Pubkey` serialization
- `ENABLE_V2_GUIDE.md` - V2 enablement guide

---

## 🎉 Status

**FIXED** - Ready to deploy!

The backend will now correctly switch to V2 when `USE_CONTRACT_V2=true` is set.

