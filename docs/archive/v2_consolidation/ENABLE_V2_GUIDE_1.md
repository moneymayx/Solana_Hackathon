# Enable V2 Smart Contract Features

**Current Status**: V2 deployed but disabled (`USE_CONTRACT_V2=false`)  
**Ready to Enable**: ✅ Yes - All validations passed  
**Risk Level**: Low (can rollback instantly)

---

## 🎯 What Enabling V2 Does

When you set `USE_CONTRACT_V2=true`, your backend will:

1. **Use the V2 smart contract** for entry payments
2. **Implement 4-way split**: 60% bounty pool, 20% operational, 10% buyback, 10% staking
3. **Enable price escalation**: Each entry costs slightly more (1.0078^n)
4. **Track per-bounty data** on-chain
5. **Verify AI decisions** with signature checking

---

## 📋 Step-by-Step: Enable V2 on Backend

### Step 1: Go to DigitalOcean

1. Open: https://cloud.digitalocean.com/apps
2. Click on your **solana-hackathon** app
3. Click **Settings** tab (top menu)

### Step 2: Edit Environment Variables

1. Scroll down to **Environment Variables** section
2. Click **Edit** button
3. Find `USE_CONTRACT_V2`
4. Change value from `false` to `true`
5. Click **Save**

**Screenshot of what to change**:
```
Before:
USE_CONTRACT_V2 = false

After:
USE_CONTRACT_V2 = true
```

### Step 3: Wait for Auto-Deploy

- DigitalOcean will automatically redeploy (2-5 minutes)
- Watch the deployment status at the top of the page
- Wait for it to show **"Live"** with a green checkmark

### Step 4: Check Logs

1. Click **Runtime Logs** tab
2. Look for:
   - ✅ "Server started" message
   - ✅ No errors about V2
   - ❌ Any red error messages

---

## 🧪 Testing V2 Features

### Test 1: Verify V2 is Enabled

Check the stats endpoint to see if V2 is active:

```bash
curl https://billions-bounty-iwnh3.ondigitalocean.app/api/stats
```

Look for any V2-related fields in the response.

### Test 2: Test Entry Payment (If you have test credentials)

```bash
curl -X POST https://billions-bounty-iwnh3.ondigitalocean.app/api/payment/create \
  -H "Content-Type: application/json" \
  -d '{
    "bounty_id": 1,
    "amount": 10,
    "wallet_address": "YOUR_TEST_WALLET"
  }'
```

**Expected**: Transaction signature returned

### Test 3: Verify On-Chain Split

1. Copy the transaction signature from the response
2. Go to: https://explorer.solana.com/?cluster=devnet
3. Paste the signature
4. Look for **4 token transfers**:
   - 60% to `CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF` (bounty pool)
   - 20% to `46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D` (operational)
   - 10% to `7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya` (buyback)
   - 10% to `Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX` (staking)

### Test 4: Check Wallet Balances

```bash
# Bounty pool (should increase by 60% of entry amount)
solana balance CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF --url devnet

# Operational (should increase by 20%)
solana balance 46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D --url devnet

# Buyback (should increase by 10%)
solana balance 7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya --url devnet

# Staking (should increase by 10%)
solana balance Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX --url devnet
```

---

## 🔍 Monitoring After Enabling V2

### What to Watch:

**First Hour**:
- Check logs every 15 minutes
- Look for any V2-related errors
- Test a few transactions

**First 24 Hours**:
- Check logs every 2-4 hours
- Monitor wallet balances
- Verify splits are correct
- Track transaction success rate

### Key Metrics:

| Metric | Target | How to Check |
|--------|--------|--------------|
| Transaction Success Rate | >95% | Count successful vs failed in logs |
| 4-Way Split Accuracy | Exactly 60/20/10/10 | Check Solana Explorer |
| Response Time | <2 seconds | Test API endpoints |
| Error Rate | <5% | Count errors in logs |

---

## 🚨 Rollback Plan (If Issues Occur)

### Quick Rollback (Takes 2 minutes):

1. Go to DigitalOcean → Your App → Settings
2. Find `USE_CONTRACT_V2` in Environment Variables
3. Change from `true` back to `false`
4. Click **Save**
5. Wait for auto-redeploy
6. Verify existing features work

### When to Rollback:

- ❌ Transaction success rate drops below 90%
- ❌ Multiple errors in logs
- ❌ Wallet splits are incorrect
- ❌ Users reporting payment issues
- ❌ Any critical functionality broken

### After Rollback:

1. Review logs to identify the issue
2. Fix the problem
3. Test on local/dev environment
4. Re-enable V2 when ready

---

## 📊 Expected Behavior After Enabling V2

### What Should Happen:

✅ **Entry payments** route through V2 contract  
✅ **Funds split** 60/20/10/10 automatically  
✅ **Price escalates** with each entry (1.0078^n)  
✅ **Per-bounty tracking** on-chain  
✅ **Existing features** continue to work  

### What Should NOT Change:

✅ User experience (same flow)  
✅ Frontend interface  
✅ API endpoints  
✅ Authentication  
✅ Non-payment features  

---

## 🎯 Success Criteria

V2 is considered successful when:

- [ ] No errors in logs for 2 hours
- [ ] At least 3 successful test transactions
- [ ] All 3 transactions show correct 60/20/10/10 split
- [ ] Wallet balances match expected amounts
- [ ] Price escalation working correctly
- [ ] No user complaints

---

## 🔗 Quick Links

- **DigitalOcean App**: https://cloud.digitalocean.com/apps
- **Backend URL**: https://billions-bounty-iwnh3.ondigitalocean.app
- **Solana Explorer**: https://explorer.solana.com/?cluster=devnet
- **API Docs**: https://billions-bounty-iwnh3.ondigitalocean.app/docs

### Wallet Addresses (for monitoring):

```
Bounty Pool:  CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF
Operational:  46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D
Buyback:      7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya
Staking:      Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX
```

---

## 📝 Checklist

### Before Enabling:
- [x] V2 contract deployed to devnet
- [x] All validations passed (6/6)
- [x] Environment variables configured
- [x] Backend deployed and running
- [x] Rollback plan understood

### After Enabling:
- [ ] Changed `USE_CONTRACT_V2` to `true`
- [ ] Waited for deployment to complete
- [ ] Checked logs for errors
- [ ] Tested entry payment
- [ ] Verified 4-way split on-chain
- [ ] Checked wallet balances
- [ ] Monitoring for 24 hours

---

## 💡 Tips

1. **Enable during low-traffic hours** - Easier to monitor and rollback if needed
2. **Have Solana Explorer open** - Watch transactions in real-time
3. **Keep logs visible** - Catch issues immediately
4. **Test with small amounts first** - Minimize risk
5. **Document any issues** - Helps with troubleshooting

---

## 🆘 Troubleshooting

### Issue: "Contract not initialized"
**Fix**: Run the initialization script again
```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/programs/billions-bounty-v2
npm run init:devnet
```

### Issue: "Insufficient balance"
**Fix**: Ensure wallets have enough SOL/USDC for transactions

### Issue: "Transaction failed"
**Fix**: Check RPC endpoint is responding, verify wallet addresses

### Issue: "Split amounts incorrect"
**Fix**: Verify contract rates are 60/20/10/10, check for rounding errors

---

**Ready to Enable V2?** Follow the steps above! 🚀

**Need Help?** Check the logs first, then review `V2_COMPLETION_REPORT.md` for details.

**Last Updated**: October 30, 2024



