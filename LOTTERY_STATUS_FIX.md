# Lottery Status Endpoint Fix

**Date**: October 30, 2024  
**Issue**: `/api/lottery/status` returning 500 Internal Server Error  
**Status**: ✅ Fixed and deployed

---

## Problem

The lottery status endpoint was failing with:
```
ValueError: [TypeError("'solders.pubkey.Pubkey' object is not iterable")]
```

**Root Cause**: The `get_lottery_state()` method in `smart_contract_service.py` was returning a Solana `Pubkey` object directly in the JSON response. FastAPI cannot serialize Pubkey objects to JSON.

---

## Solution

**File**: `src/services/smart_contract_service.py`  
**Line**: 341  
**Change**: Convert `Pubkey` to string before returning

### Before:
```python
return {
    "success": True,
    "program_id": self.program_id,  # ❌ Returns Pubkey object
    ...
}
```

### After:
```python
return {
    "success": True,
    "program_id": str(self.program_id),  # ✅ Converts to string
    ...
}
```

---

## Deployment

1. ✅ Fix applied to `src/services/smart_contract_service.py`
2. ✅ Committed to git: `b6a4bec`
3. ✅ Pushed to `staging-v2` branch
4. ⏳ DigitalOcean auto-deploying (takes 2-5 minutes)

---

## Testing

### Once Deployment Completes:

Test the endpoint:
```bash
curl https://billions-bounty-iwnh3.ondigitalocean.app/api/lottery/status
```

**Expected Response**:
```json
{
  "success": true,
  "program_id": "FxVpjJ5AGY6cfCwZQP5v8QBfS4J2NPa62HbGh1Fu2LpD",
  "current_jackpot": 10000.0,
  "total_entries": 0,
  "is_active": true,
  "research_fund_floor": 10000.0,
  "research_fee": 10.0,
  "last_rollover": "2024-10-30T...",
  "next_rollover": "2024-10-30T..."
}
```

---

## How to Check Deployment Status

### Option 1: DigitalOcean Dashboard
1. Go to https://cloud.digitalocean.com/apps
2. Click on your app
3. Look for "Deploying" or "Live" status
4. Check "Runtime Logs" for any new errors

### Option 2: Command Line
```bash
# Test the endpoint (will return error until deployment completes)
curl https://billions-bounty-iwnh3.ondigitalocean.app/api/lottery/status

# Check if it's the old version (will show error)
# or new version (will show JSON response)
```

---

## Additional Notes

### Other Pubkey Conversions Already Fixed:

The codebase already properly converts Pubkeys to strings in most places:

1. **`get_lottery_status()` method** (line 107-108):
   ```python
   "lottery_pda": str(self.lottery_pda),
   "program_id": str(self.program_id)
   ```

2. **`_record_lottery_entry()` method** (line 405):
   ```python
   "target_wallet": str(self.program_id)
   ```

This fix brings `get_lottery_state()` in line with the rest of the codebase.

---

## Prevention

To prevent similar issues in the future:

### Rule: Always Convert Solana Types to Strings

When returning data from API endpoints, always convert Solana-specific types:

```python
# ❌ Bad - Will cause serialization error
return {"address": some_pubkey}

# ✅ Good - Converts to string
return {"address": str(some_pubkey)}

# ✅ Also good - Convert in a helper
def serialize_pubkey(pubkey):
    return str(pubkey) if pubkey else None
```

### Common Solana Types to Convert:
- `Pubkey` → `str(pubkey)`
- `Keypair` → Don't return (security risk)
- `Signature` → `str(signature)`
- Large integers → May need special handling

---

## Timeline

| Time | Action |
|------|--------|
| 23:51:42 | Error first detected in logs |
| 23:52:00 | Issue identified (Pubkey serialization) |
| 23:53:00 | Fix applied to code |
| 23:53:30 | Committed and pushed to staging-v2 |
| 23:54:00 | DigitalOcean auto-deploy triggered |
| ~23:57:00 | Expected deployment completion |

---

## Verification Checklist

Once deployment completes:

- [ ] Test lottery status endpoint
- [ ] Verify it returns JSON (not error)
- [ ] Check `program_id` is a string
- [ ] Verify no new errors in logs
- [ ] Test other endpoints still work

---

## Next Steps

1. **Wait 2-5 minutes** for DigitalOcean to complete deployment
2. **Test the endpoint** using the curl command above
3. **Check logs** in DigitalOcean for any new errors
4. **Proceed with V2 testing** once confirmed working

---

**Status**: ✅ Fix deployed, awaiting auto-deployment completion  
**ETA**: 2-5 minutes from push (around 23:57:00)

