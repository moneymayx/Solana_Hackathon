# V2 Payment Test - Step-by-Step Instructions

**Date**: October 31, 2025  
**Status**: 🧪 READY TO TEST

---

## ✅ Pre-Test Status

### Confirmed Ready:
- ✅ Frontend accessible: https://solana-hackathon-5ljqwcujg-jay-brantleys-projects.vercel.app/
- ✅ Backend operational with V2 active
- ✅ V2 smart contract deployed: `HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`
- ✅ All 4 wallets configured

### Current Wallet Balances:
```
Bounty Pool: 0 USDC (token account exists)
Operational: No token account yet
Buyback: No token account yet
Staking: No token account yet
```

**Note**: Token accounts will be created automatically during the first payment.

---

## 🎯 What We're Testing

### V2 Features:
1. **4-Way Split** (60/20/10/10):
   - 60% → Bounty Pool
   - 20% → Operational
   - 10% → Buyback
   - 10% → Staking

2. **On-Chain Tracking**:
   - Bounty PDA updates
   - Total entries increment

3. **Smart Contract Execution**:
   - Transaction succeeds
   - Funds distributed correctly

---

## ⚠️ Important Note: Backend Currently Uses Placeholder

The backend's `SmartContractService` currently has **placeholder** smart contract calls. This means:

### Current Behavior:
- Backend simulates the transaction
- Returns success but doesn't actually call V2 contract
- No real on-chain transaction happens

### To Test V2 For Real:
You have 3 options:

#### **Option A: Wait for Full Integration** (Recommended)
- Backend needs to be updated to actually call V2 contract
- Would require modifying `src/services/smart_contract_service.py`
- Add real Anchor client integration

#### **Option B: Test Via Direct Contract Call** (Advanced)
- Use TypeScript script to call contract directly
- Bypass backend entirely
- See `V2_PAYMENT_TEST_GUIDE.md` for script

#### **Option C: Test Backend Flow** (Current State)
- Test that frontend → backend flow works
- Verify API responses
- Actual V2 contract call comes later

---

## 🧪 Option C: Test Current Backend Flow

### Step 1: Open Frontend
1. Go to: https://solana-hackathon-5ljqwcujg-jay-brantleys-projects.vercel.app/
2. Should load without password

### Step 2: Connect Wallet
1. Click "Connect Wallet" button
2. Select your Solana wallet (Phantom, Solflare, etc.)
3. Approve connection
4. Verify wallet address shows in UI

### Step 3: Select a Bounty
1. Browse available bounties
2. Click on a bounty (e.g., "Claude Champ")
3. Should see bounty details

### Step 4: Submit Entry
1. Click "Enter Bounty" or similar
2. Enter amount: $10
3. Review transaction details
4. Click "Submit" or "Pay"

### Step 5: Check Response
**What to expect** (with current placeholder):
- ✅ Transaction appears to succeed
- ✅ Backend returns success message
- ✅ Entry recorded in database
- ❌ No actual on-chain transaction (placeholder)
- ❌ Wallet balances don't change (no real tx)

### Step 6: Verify Backend Logs
Check DigitalOcean logs for:
```
🎫 Processing lottery entry: $10 from <wallet>
   Bounty pool (60%): $6.00
   Operational fee (20%): $2.00
   Buyback (10%): $1.00
   Staking (10%): $1.00
```

---

## 🔧 Option B: Test V2 Contract Directly

If you want to test the **actual V2 smart contract**, you'll need to:

### Step 1: Create Test Script

Create `test_v2_direct.ts` in `programs/billions-bounty-v2/scripts/`:

```typescript
import * as anchor from "@coral-xyz/anchor";
import { Connection, Keypair, PublicKey, SystemProgram } from "@solana/web3.js";
import { 
  TOKEN_PROGRAM_ID, 
  getAssociatedTokenAddress,
  createAssociatedTokenAccountInstruction 
} from "@solana/spl-token";
import * as fs from "fs";

const PROGRAM_ID = new PublicKey("HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm");
const USDC_MINT = new PublicKey("JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh");

// Destination wallets
const BOUNTY_POOL = new PublicKey("CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
const OPERATIONAL = new PublicKey("46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D");
const BUYBACK = new PublicKey("7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya");
const STAKING = new PublicKey("Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX");

async function testV2Payment() {
  console.log("🧪 Testing V2 Entry Payment...\n");
  
  const connection = new Connection("https://api.devnet.solana.com", "confirmed");
  
  // Load your wallet
  const keypairPath = process.env.HOME + "/.config/solana/id.json";
  const keypairData = JSON.parse(fs.readFileSync(keypairPath, "utf-8"));
  const userKeypair = Keypair.fromSecretKey(new Uint8Array(keypairData));
  
  console.log("User Wallet:", userKeypair.publicKey.toString());
  
  // Derive PDAs
  const [globalPda] = PublicKey.findProgramAddressSync(
    [Buffer.from("global")],
    PROGRAM_ID
  );
  
  const bountyId = 1;
  const [bountyPda] = PublicKey.findProgramAddressSync(
    [Buffer.from("bounty"), new anchor.BN(bountyId).toArrayLike(Buffer, "le", 8)],
    PROGRAM_ID
  );
  
  console.log("Global PDA:", globalPda.toString());
  console.log("Bounty PDA:", bountyPda.toString());
  
  // Get/create token accounts
  const userTokenAccount = await getAssociatedTokenAddress(USDC_MINT, userKeypair.publicKey);
  const bountyPoolTokenAccount = await getAssociatedTokenAddress(USDC_MINT, BOUNTY_POOL);
  const operationalTokenAccount = await getAssociatedTokenAddress(USDC_MINT, OPERATIONAL);
  const buybackTokenAccount = await getAssociatedTokenAddress(USDC_MINT, BUYBACK);
  const stakingTokenAccount = await getAssociatedTokenAddress(USDC_MINT, STAKING);
  
  console.log("\nToken Accounts:");
  console.log("User:", userTokenAccount.toString());
  console.log("Bounty Pool:", bountyPoolTokenAccount.toString());
  console.log("Operational:", operationalTokenAccount.toString());
  console.log("Buyback:", buybackTokenAccount.toString());
  console.log("Staking:", stakingTokenAccount.toString());
  
  // Check user USDC balance
  const userBalance = await connection.getTokenAccountBalance(userTokenAccount);
  console.log("\nUser USDC Balance:", userBalance.value.uiAmount);
  
  if (!userBalance.value.uiAmount || userBalance.value.uiAmount < 10) {
    console.log("❌ Insufficient USDC balance. Need at least 10 USDC.");
    console.log("   Get devnet USDC from a faucet or mint if you have authority.");
    return;
  }
  
  // Load IDL
  const idlPath = "../target/idl/billions_bounty_v2.json";
  const idl = JSON.parse(fs.readFileSync(idlPath, "utf-8"));
  
  // Create program instance
  const provider = new anchor.AnchorProvider(
    connection,
    new anchor.Wallet(userKeypair),
    { commitment: "confirmed" }
  );
  const program = new anchor.Program(idl, PROGRAM_ID, provider);
  
  // Entry amount: 10 USDC (with 6 decimals)
  const entryAmount = new anchor.BN(10_000_000);
  
  console.log("\n🚀 Sending transaction...");
  console.log("Amount: 10 USDC");
  console.log("Bounty ID:", bountyId);
  
  try {
    const tx = await program.methods
      .processEntryPaymentV2(new anchor.BN(bountyId), entryAmount)
      .accounts({
        global: globalPda,
        bounty: bountyPda,
        user: userKeypair.publicKey,
        userTokenAccount: userTokenAccount,
        bountyPoolWallet: BOUNTY_POOL,
        bountyPoolTokenAccount: bountyPoolTokenAccount,
        operationalWallet: OPERATIONAL,
        operationalTokenAccount: operationalTokenAccount,
        buybackWallet: BUYBACK,
        buybackTokenAccount: buybackTokenAccount,
        stakingWallet: STAKING,
        stakingTokenAccount: stakingTokenAccount,
        usdcMint: USDC_MINT,
        tokenProgram: TOKEN_PROGRAM_ID,
        systemProgram: SystemProgram.programId,
      })
      .rpc();
    
    console.log("\n✅ Transaction successful!");
    console.log("Signature:", tx);
    console.log("\nView on Explorer:");
    console.log(`https://explorer.solana.com/tx/${tx}?cluster=devnet`);
    
    // Check new balances
    console.log("\n📊 Checking new balances...");
    const bountyPoolBalance = await connection.getTokenAccountBalance(bountyPoolTokenAccount);
    const operationalBalance = await connection.getTokenAccountBalance(operationalTokenAccount);
    const buybackBalance = await connection.getTokenAccountBalance(buybackTokenAccount);
    const stakingBalance = await connection.getTokenAccountBalance(stakingTokenAccount);
    
    console.log("Bounty Pool:", bountyPoolBalance.value.uiAmount, "USDC (should be +6)");
    console.log("Operational:", operationalBalance.value.uiAmount, "USDC (should be +2)");
    console.log("Buyback:", buybackBalance.value.uiAmount, "USDC (should be +1)");
    console.log("Staking:", stakingBalance.value.uiAmount, "USDC (should be +1)");
    
  } catch (error) {
    console.log("\n❌ Transaction failed:");
    console.error(error);
  }
}

testV2Payment();
```

### Step 2: Run Test Script

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/programs/billions-bounty-v2

# Install dependencies if needed
npm install

# Run test
npx ts-node scripts/test_v2_direct.ts
```

### Step 3: Verify Results

**Expected Output**:
```
✅ Transaction successful!
Signature: <transaction_id>

Bounty Pool: 6 USDC (should be +6)
Operational: 2 USDC (should be +2)
Buyback: 1 USDC (should be +1)
Staking: 1 USDC (should be +1)
```

---

## 📊 Success Criteria

### For Option C (Backend Flow Test):
- [ ] Frontend loads
- [ ] Wallet connects
- [ ] Can select bounty
- [ ] Can submit entry
- [ ] Backend responds with success
- [ ] Entry recorded in database

### For Option B (Direct Contract Test):
- [ ] Transaction succeeds on devnet
- [ ] Bounty Pool receives 6 USDC (60%)
- [ ] Operational receives 2 USDC (20%)
- [ ] Buyback receives 1 USDC (10%)
- [ ] Staking receives 1 USDC (10%)
- [ ] Total = 10 USDC
- [ ] Transaction visible on Solana Explorer

---

## 🚨 Troubleshooting

### Issue: Insufficient USDC
**Solution**: Get devnet USDC
```bash
# Option 1: Use a devnet faucet (if available)
# Option 2: If you have mint authority:
spl-token mint JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh 100 <YOUR_TOKEN_ACCOUNT> --url devnet
```

### Issue: Token Account Not Found
**Solution**: Create associated token account
```bash
spl-token create-account JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh --url devnet
```

### Issue: Transaction Fails
**Check**:
- PDAs initialized?
- Sufficient USDC balance?
- Token accounts exist?
- Program ID correct?

---

## 📝 Next Steps

### After Testing:

1. **If Backend Flow Works** (Option C):
   - ✅ Frontend → Backend integration confirmed
   - ⏳ Need to implement real V2 contract calls in backend
   - ⏳ Update `SmartContractService` to use Anchor client

2. **If Direct Contract Works** (Option B):
   - ✅ V2 smart contract confirmed working
   - ✅ 4-way split verified
   - ⏳ Integrate into backend
   - ⏳ Update frontend to call contract directly

3. **Monitor Logs**:
   - Check DigitalOcean logs for 24 hours
   - Watch for any errors
   - Verify all transactions succeed

---

## 🎯 Recommended Approach

**For Now** (Quickest):
1. Test **Option C** (Backend Flow)
   - Verify frontend works
   - Verify backend responds
   - Confirm user flow is smooth

**Next** (Full V2 Testing):
2. Test **Option B** (Direct Contract)
   - Verify V2 contract works
   - Confirm 4-way split
   - Get transaction on explorer

**Then** (Production Ready):
3. Integrate V2 into backend
   - Update `SmartContractService`
   - Add Anchor client
   - Replace placeholders with real calls

---

**Ready to test!** Start with Option C to verify the flow, then move to Option B for full V2 testing. 🚀



