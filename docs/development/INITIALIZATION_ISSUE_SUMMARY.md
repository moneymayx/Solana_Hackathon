# 🚨 Lottery Initialization Issue - Action Required

## Current Status

**Issue**: The lottery contract cannot be initialized due to a **Program ID Mismatch** error.

**Root Cause**: The deployed program's `declare_id!` doesn't match the actual program ID at runtime.

## What Happened

1. ✅ Contract deployed to: `Exdfc34rowaKJDnJtLpf5hNs5EF6eGXghRB2ocjrPd6H`
2. ✅ All wallet addresses configured
3. ✅ Authority has sufficient balance (2.16 SOL)
4. ❌ Initialization fails with: `DeclaredProgramIdMismatch (0x1004)`

## Error Details

```
Program log: AnchorError occurred. Error Code: DeclaredProgramIdMismatch. 
Error Number: 4100. Error Message: The declared program id does not match 
the actual program id.
```

This error indicates the compiled binary has a different `declare_id!` than the source code.

## Options to Resolve

### ⭐ Option 1: Airdrop More SOL & Redeploy (RECOMMENDED)

The existing binary is out of sync. To fix:

```bash
# 1. Airdrop more SOL (need ~2.2 SOL total, have 2.16)
solana airdrop 1 ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC --url devnet

# 2. Redeploy the program
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
solana program deploy \
  target/deploy/billions_bounty.so \
  --program-id target/deploy/billions_bounty-keypair.json \
  --url devnet

# 3. Run initialization
node scripts/init_lottery.js
```

**Time**: ~5 minutes  
**Cost**: Free (devnet SOL is free)  
**Risk**: Low - standard deployment procedure

---

### Option 2: Deploy Fresh Program with New ID

Create a completely new program instance:

```bash
# 1. Generate new keypair
solana-keygen new -o target/deploy/billions_bounty-new.json

# 2. Get the new program ID
NEW_ID=$(solana-keygen pubkey target/deploy/billions_bounty-new.json)
echo "New Program ID: $NEW_ID"

# 3. Update source code
# Edit programs/billions-bounty/src/lib.rs
# Change: declare_id!("Exdfc34rowaKJDnJtLpf5hNs5EF6eGXghRB2ocjrPd6H");
# To:     declare_id!("$NEW_ID");

# 4. Update Anchor.toml with new ID

# 5. Rebuild
anchor build

# 6. Airdrop SOL if needed
solana airdrop 2 --url devnet

# 7. Deploy new program
anchor deploy --provider.cluster devnet

# 8. Update all references to new program ID in:
#    - .env (LOTTERY_PROGRAM_ID)
#    - src/network_config.py
#    - Anchor.toml

# 9. Restart backend services

# 10. Run initialization
node scripts/init_lottery.js
```

**Time**: ~15 minutes  
**Cost**: Free (devnet SOL)  
**Risk**: Medium - requires updating many configuration files

---

### Option 3: Use Existing Staking Contract (Temporary Workaround)

The staking contract at `5Yx1QzgapjAAFTR4mN4oxy3Qk3imj4nAAaNXQCYTMgCc` initialized successfully. You could:

1. Test staking features now
2. Fix lottery deployment later
3. Focus on backend testing with mock data

**Time**: Immediate  
**Cost**: None  
**Risk**: Low - but lottery features unavailable

---

## Recommended Action Plan

**STEP 1**: Add more SOL to deployer wallet

```bash
# Run this command:
solana airdrop 1 ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC --url devnet
```

**STEP 2**: Redeploy the lottery program

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
solana program deploy \
  target/deploy/billions_bounty.so \
  --program-id target/deploy/billions_bounty-keypair.json \
  --url devnet
```

**STEP 3**: Initialize the contract

```bash
node scripts/init_lottery.js
```

**STEP 4**: Verify initialization

```bash
python3 scripts/initialize_lottery_devnet.py
```

**STEP 5**: Continue with testing

---

## Current Configuration (Ready to Use)

```
✅ Program ID: Exdfc34rowaKJDnJtLpf5hNs5EF6eGXghRB2ocjrPd6H
✅ Lottery PDA: Cdb3TimgJSasfvmLvKCHTMxKPPdYXxDAy8wqqLUHwk9U
✅ Authority: ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC
✅ Wallets:
   - Jackpot (60%):     CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF
   - Operational (20%): 46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D
   - Buyback (10%):     7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya
   - Staking (10%):     Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX
```

---

## What's Blocking You

| Task | Status | Blocker |
|------|--------|---------|
| Initialize lottery | ❌ Blocked | Need to fix program deployment |
| Test escape timer | ❌ Blocked | Requires initialized lottery |
| Test revenue split | ❌ Blocked | Requires initialized lottery |
| Test buyback | ⚠️ Partial | Can test monitoring, not execution |
| Test staking | ✅ Ready | Staking contract works |

---

## Summary

**Problem**: The lottery program has a code mismatch error preventing initialization.

**Solution**: Airdrop 1 more SOL and redeploy the program (5 minutes).

**Alternative**: Deploy a fresh program with a new ID (15 minutes, more complex).

**Next Step**: Choose an option above and I'll help you execute it.

---

**Priority**: 🔴 **CRITICAL** - All lottery testing is blocked

**Estimated Time to Fix**: 5-15 minutes depending on option chosen

**Need Help?**: I can guide you through any of the three options above step-by-step.


