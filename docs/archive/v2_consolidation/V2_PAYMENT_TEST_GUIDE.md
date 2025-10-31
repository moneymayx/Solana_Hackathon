# V2 Entry Payment Testing Guide

**Date**: October 31, 2025  
**Purpose**: Test V2 smart contract entry payment with 4-way split  
**Status**: 🧪 READY TO TEST

---

## 🎯 What We're Testing

### V2 Features:
1. **4-Way Split** (60/20/10/10):
   - 60% → Bounty Pool Wallet
   - 20% → Operational Wallet
   - 10% → Buyback Wallet
   - 10% → Staking Wallet

2. **Price Escalation**:
   - Base price: $10
   - Formula: `base_price * (1.0078 ^ total_entries)`
   - Each entry increases price

3. **On-Chain Tracking**:
   - Bounty PDA updates
   - Total entries increment
   - Current pool increases

---

## 📋 Pre-Test Checklist

### ✅ Confirmed Ready:
- [x] V2 smart contract deployed (`HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`)
- [x] Backend using V2 (`USE_CONTRACT_V2=true`)
- [x] Environment variables loaded
- [x] All 4 wallets configured

### ⏳ Need to Verify:
- [ ] Wallet has devnet SOL
- [ ] Wallet has devnet USDC
- [ ] All 4 destination wallets exist
- [ ] Bounty PDA initialized

---

## 🔍 Step 1: Check Current Wallet Balances

### Check Devnet SOL Balances:
```bash
# Bounty Pool Wallet
solana balance CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF --url devnet

# Operational Wallet
solana balance 46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D --url devnet

# Buyback Wallet
solana balance 7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya --url devnet

# Staking Wallet
solana balance Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX --url devnet
```

### Check USDC Token Balances:
```bash
# USDC Mint: JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh

# Bounty Pool USDC
spl-token balance JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh --owner CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF --url devnet

# Operational USDC
spl-token balance JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh --owner 46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D --url devnet

# Buyback USDC
spl-token balance JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh --owner 7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya --url devnet

# Staking USDC
spl-token balance JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh --owner Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX --url devnet
```

**Record Initial Balances**:
```
Bounty Pool: _____ USDC
Operational: _____ USDC
Buyback: _____ USDC
Staking: _____ USDC
```

---

## 🧪 Step 2: Check Bounty PDA Status

### Get Current Bounty State:
```bash
# Using Solana CLI
solana account 2J455GTdBfceWWUF7dcPawixW4PEfWBdVgX7Soqc3trb --url devnet

# Or via backend API
curl -s https://billions-bounty-iwnh3.ondigitalocean.app/api/bounties/1 | python3 -m json.tool
```

**Record Current State**:
```
Current Pool: _____ USDC
Total Entries: _____
Is Active: _____
```

---

## 💰 Step 3: Prepare Test Payment

### Option A: Via Backend API (Simulated)

The backend currently has placeholder smart contract calls. To test the full flow, we need to either:
1. Use the frontend (once deployed)
2. Create a test script that calls the V2 contract directly

### Option B: Direct Smart Contract Call (TypeScript)

Create a test script:

```typescript
// test_v2_entry.ts
import * as anchor from "@coral-xyz/anchor";
import { Connection, Keypair, PublicKey } from "@solana/web3.js";
import { getAssociatedTokenAddress } from "@solana/spl-token";

const PROGRAM_ID = new PublicKey("HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm");
const USDC_MINT = new PublicKey("JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh");

// Destination wallets
const BOUNTY_POOL = new PublicKey("CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
const OPERATIONAL = new PublicKey("46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D");
const BUYBACK = new PublicKey("7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya");
const STAKING = new PublicKey("Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX");

async function testV2Entry() {
  const connection = new Connection("https://api.devnet.solana.com", "confirmed");
  
  // Load your wallet keypair
  const userKeypair = Keypair.fromSecretKey(
    // Load from ~/.config/solana/id.json or your wallet
  );
  
  // Derive PDAs
  const [globalPda] = PublicKey.findProgramAddressSync(
    [Buffer.from("global")],
    PROGRAM_ID
  );
  
  const bountyId = 1;
  const [bountyPda] = PublicKey.findProgramAddressSync(
    [Buffer.from("bounty"), Buffer.from(bountyId.toString().padStart(8, '0'))],
    PROGRAM_ID
  );
  
  // Get token accounts
  const userTokenAccount = await getAssociatedTokenAddress(USDC_MINT, userKeypair.publicKey);
  const bountyPoolTokenAccount = await getAssociatedTokenAddress(USDC_MINT, BOUNTY_POOL);
  const operationalTokenAccount = await getAssociatedTokenAddress(USDC_MINT, OPERATIONAL);
  const buybackTokenAccount = await getAssociatedTokenAddress(USDC_MINT, BUYBACK);
  const stakingTokenAccount = await getAssociatedTokenAddress(USDC_MINT, STAKING);
  
  // Entry amount: 10 USDC (with 6 decimals)
  const entryAmount = 10_000_000;
  
  console.log("Testing V2 Entry Payment...");
  console.log("User:", userKeypair.publicKey.toString());
  console.log("Amount:", entryAmount / 1_000_000, "USDC");
  console.log("Bounty ID:", bountyId);
  
  // TODO: Build and send transaction
  // This requires the Anchor IDL and program instance
  
  console.log("Transaction sent!");
}

testV2Entry();
```

### Option C: Via Frontend (Recommended)

Once frontend is deployed:
1. Connect wallet
2. Select a bounty
3. Enter amount ($10)
4. Submit payment
5. Confirm transaction in wallet
6. Wait for confirmation

---

## 📊 Step 4: Verify 4-Way Split

After payment is processed, check wallet balances again:

### Expected Distribution for $10 Entry:
```
Bounty Pool: +$6.00 (60%)
Operational: +$2.00 (20%)
Buyback: +$1.00 (10%)
Staking: +$1.00 (10%)
```

### Check New Balances:
```bash
# Re-run balance checks from Step 1
# Compare with initial balances
```

### Calculate Differences:
```
Bounty Pool: [New] - [Initial] = _____ (should be ~6 USDC)
Operational: [New] - [Initial] = _____ (should be ~2 USDC)
Buyback: [New] - [Initial] = _____ (should be ~1 USDC)
Staking: [New] - [Initial] = _____ (should be ~1 USDC)
```

---

## 🔍 Step 5: Verify On-Chain Updates

### Check Bounty PDA:
```bash
# Get updated bounty state
curl -s https://billions-bounty-iwnh3.ondigitalocean.app/api/bounties/1 | python3 -m json.tool
```

### Expected Changes:
```
Current Pool: [Old] + 6.00 USDC
Total Entries: [Old] + 1
```

### Check Transaction on Explorer:
1. Get transaction signature from response
2. View on Solana Explorer:
   - Devnet: https://explorer.solana.com/?cluster=devnet
   - Search for transaction signature
3. Verify:
   - ✅ Transaction succeeded
   - ✅ 4 token transfers visible
   - ✅ Correct amounts
   - ✅ Correct destinations

---

## 🧪 Step 6: Test Price Escalation

### Make Second Entry:
1. Submit another $10 entry
2. Expected price: `$10 * 1.0078 = $10.078`
3. Backend should require at least $10.078

### Verify:
- [ ] Price increased
- [ ] Transaction requires higher amount
- [ ] Rejection if amount too low

---

## 📝 Test Results Template

```markdown
## V2 Entry Payment Test Results

**Date**: ___________
**Tester**: ___________
**Entry Amount**: $10.00

### Initial Balances:
- Bounty Pool: _____ USDC
- Operational: _____ USDC
- Buyback: _____ USDC
- Staking: _____ USDC

### Transaction:
- Signature: _____________________
- Status: [ ] Success / [ ] Failed
- Block: _____

### Final Balances:
- Bounty Pool: _____ USDC (+_____)
- Operational: _____ USDC (+_____)
- Buyback: _____ USDC (+_____)
- Staking: _____ USDC (+_____)

### Split Verification:
- Bounty Pool (60%): [ ] ✅ Correct / [ ] ❌ Incorrect
- Operational (20%): [ ] ✅ Correct / [ ] ❌ Incorrect
- Buyback (10%): [ ] ✅ Correct / [ ] ❌ Incorrect
- Staking (10%): [ ] ✅ Correct / [ ] ❌ Incorrect

### On-Chain Updates:
- Bounty Pool: [ ] ✅ Updated / [ ] ❌ Not Updated
- Total Entries: [ ] ✅ Incremented / [ ] ❌ Not Incremented

### Price Escalation:
- Second entry price: $_____
- [ ] ✅ Escalated correctly
- [ ] ❌ Did not escalate

### Overall: [ ] ✅ PASS / [ ] ❌ FAIL

### Notes:
_____________________
```

---

## 🚨 Troubleshooting

### Issue: Insufficient Balance
**Solution**: Airdrop devnet SOL and USDC
```bash
# Airdrop SOL
solana airdrop 2 <YOUR_WALLET> --url devnet

# Mint devnet USDC (if you have mint authority)
spl-token mint JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh 100 <YOUR_TOKEN_ACCOUNT> --url devnet
```

### Issue: Transaction Fails
**Check**:
- Program ID correct?
- PDAs initialized?
- Token accounts exist?
- Sufficient balance?
- Correct instruction data?

### Issue: Split Doesn't Match
**Check**:
- Are rates correct in contract? (60/20/10/10)
- Are destination wallets correct?
- Did transaction actually succeed?
- Check transaction logs for errors

### Issue: Price Doesn't Escalate
**Check**:
- Is `total_entries` incrementing?
- Is calculation correct? (`base * 1.0078^n`)
- Check contract logs

---

## 📞 Quick Reference

### Wallets:
```
Bounty Pool: CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF
Operational: 46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D
Buyback: 7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya
Staking: Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX
```

### Contract:
```
Program ID: HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm
Global PDA: BursCahsMxKjiSUgTCy11uUTWnaZ1eqcGcADUxiMzHMb
Bounty 1 PDA: 2J455GTdBfceWWUF7dcPawixW4PEfWBdVgX7Soqc3trb
USDC Mint: JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh
```

### Backend:
```
API: https://billions-bounty-iwnh3.ondigitalocean.app
Status: https://billions-bounty-iwnh3.ondigitalocean.app/api/lottery/status
```

---

## ✅ Success Criteria

Test is successful when:
1. ✅ Transaction succeeds on devnet
2. ✅ 4-way split matches expected percentages
3. ✅ Bounty pool increases by 60% of entry
4. ✅ Operational wallet increases by 20%
5. ✅ Buyback wallet increases by 10%
6. ✅ Staking wallet increases by 10%
7. ✅ Total entries increments by 1
8. ✅ Price escalates for second entry
9. ✅ Transaction visible on Solana Explorer
10. ✅ No errors in logs

---

**Ready to test!** 🚀

