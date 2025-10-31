# How to Get Devnet USDC for Testing

**Date**: October 31, 2025  
**Status**: ⏳ NEED DEVNET USDC

---

## ✅ What We've Done

1. ✅ Created USDC token account: `AyjjnpamARk9bBg9D6RtVbzYU29yxgaCiL9T3j1EBYMb`
2. ✅ Test script ready
3. ⏳ Need devnet USDC to run test

---

## 🎯 Options to Get Devnet USDC

### Option 1: Use Solana Devnet Faucet (Recommended)

**SPL Token Faucet** (if available):
- Some devnet faucets provide SPL tokens including USDC
- Check: https://spl-token-faucet.com (if exists)
- Or search for "Solana devnet USDC faucet"

### Option 2: Create Your Own Test Token

Instead of using the existing USDC mint, create your own test token:

```bash
# Create a new token
spl-token create-token --url devnet

# This will output a token address like: <YOUR_TOKEN_ADDRESS>

# Create token account
spl-token create-account <YOUR_TOKEN_ADDRESS> --url devnet

# Mint 1000 tokens to yourself
spl-token mint <YOUR_TOKEN_ADDRESS> 1000 --url devnet

# Check balance
spl-token balance <YOUR_TOKEN_ADDRESS> --url devnet
```

Then update the test script to use your token instead:
- Change `USDC_MINT` in `test_v2_direct.ts`
- Change `USDC_MINT` in V2 initialization

### Option 3: Ask Token Owner

The current USDC mint (`JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh`) is owned by someone else.

You could:
1. Find who owns it
2. Ask them to mint some to your account
3. Or ask for mint authority

### Option 4: Use Real Devnet USDC (If Available)

Check if there's an official Solana devnet USDC:
- Circle might have a devnet USDC mint
- Check Solana documentation
- Look for official test tokens

---

## 🚀 Quick Solution: Create Your Own Test Token

This is the fastest way to test:

```bash
# 1. Create token
echo "Creating test token..."
TOKEN=$(spl-token create-token --url devnet | grep "Creating token" | awk '{print $3}')
echo "Token created: $TOKEN"

# 2. Create account
echo "Creating token account..."
spl-token create-account $TOKEN --url devnet

# 3. Mint tokens
echo "Minting 1000 tokens..."
spl-token mint $TOKEN 1000 --url devnet

# 4. Check balance
echo "Checking balance..."
spl-token balance $TOKEN --url devnet

echo ""
echo "✅ Done! Your test token: $TOKEN"
echo ""
echo "Update test script with this token address"
```

---

## 📝 After Getting USDC

Once you have devnet USDC (or your own test token):

### Run the Test:
```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/programs/billions-bounty-v2
npx ts-node scripts/test_v2_direct.ts
```

### Expected Output:
```
✅ TRANSACTION SUCCESSFUL!
Signature: <transaction_id>

📊 VERIFYING 4-WAY SPLIT
Bounty Pool: 6 USDC ✅ (expected 6)
Operational: 2 USDC ✅ (expected 2)
Buyback: 1 USDC ✅ (expected 1)
Staking: 1 USDC ✅ (expected 1)

🎉 TEST PASSED! 4-way split verified!
```

---

## ⚠️ Important Notes

### If Using Your Own Token:

You'll need to update:
1. **Test Script**: Change `USDC_MINT` in `test_v2_direct.ts`
2. **V2 Initialization**: Re-initialize with your token mint
3. **Backend Config**: Update `USDC_MINT` environment variable

### If You Find Devnet USDC:

Keep the current setup and just get some tokens to your account.

---

## 🎯 Recommended Approach

**For Testing V2 Smart Contract**:
1. Create your own test token (fastest)
2. Mint 1000 tokens to yourself
3. Update test script with your token address
4. Run test
5. Verify 4-way split works

**For Production**:
- Use real USDC mint
- Get proper devnet/mainnet USDC
- Test with actual USDC tokens

---

## 📊 Current Status

```
✅ Wallet: ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC
✅ Token Account: AyjjnpamARk9bBg9D6RtVbzYU29yxgaCiL9T3j1EBYMb
✅ Test Script: Ready
⏳ USDC Balance: 0 (need tokens)
```

---

## 🚀 Next Steps

1. **Get devnet USDC** (choose an option above)
2. **Run test**: `npx ts-node scripts/test_v2_direct.ts`
3. **Verify 4-way split** works correctly
4. **Check Solana Explorer** for transaction

---

**Once you have devnet USDC, the test will run and verify the V2 smart contract!** 🎉



