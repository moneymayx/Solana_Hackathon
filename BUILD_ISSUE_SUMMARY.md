# V2 Build Issue - Cargo.lock Version 4

**Date**: October 31, 2025  
**Status**: 🔴 BLOCKED - Need Manual Intervention

---

## Problem

We successfully:
1. ✅ Generated new program keypair: `HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`
2. ✅ Updated all source files with new program ID
3. ✅ Deployed the old .so file to the new program ID
4. ❌ **BLOCKED**: Cannot rebuild because Cargo creates version 4 lockfiles

The deployed program still has the old program ID (`HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`) compiled into it, causing:
```
Error: DeclaredProgramIdMismatch (0x1004)
```

---

## Root Cause

- Your system Cargo (1.90.0) creates Cargo.lock version 4
- Solana's cargo-build-sbf (rustc 1.75.0) cannot read version 4 lockfiles
- The Cargo.lock gets created immediately when any cargo command runs
- We cannot prevent it from being created

---

## Solutions

### Option A: Use Old Program ID (FASTEST - 5 minutes)

Just revert to the old program ID and use the existing deployed contract:

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/programs/billions-bounty-v2

# 1. Revert lib.rs
sed -i '' 's/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm/g' src/lib.rs

# 2. Revert Anchor.toml
sed -i '' 's/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm/g' Anchor.toml

# 3. Revert test script
sed -i '' 's/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm/g' scripts/test_v2_direct.ts

# 4. Revert init script
sed -i '' 's/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm/g' scripts/init_v2_raw.ts

# 5. Revert IDL generator
sed -i '' 's/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm/g' scripts/generate_idl.js

# 6. Regenerate IDL
node scripts/generate_idl.js
node /tmp/fix_idl_structure.js
node /tmp/fix_events_structure.js
node /tmp/fix_ai_event.js

# 7. Test
npx ts-node scripts/test_v2_direct.ts
```

**Pros**: Fast, uses existing working deployment  
**Cons**: Still has the old Global PDA with old USDC mint

---

### Option B: Downgrade Cargo (RECOMMENDED - 15 minutes)

Install an older Rust toolchain that creates v3 lockfiles:

```bash
# 1. Install Rust 1.75.0 (matches Solana's version)
rustup install 1.75.0

# 2. Set it as override for this project
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/programs/billions-bounty-v2
rustup override set 1.75.0

# 3. Remove Cargo.lock
rm -f Cargo.lock

# 4. Build
cargo build-sbf

# 5. Deploy
cd ../..
solana program deploy \
  --program-id programs/billions-bounty-v2/target/deploy/billions_bounty_v2-keypair.json \
  programs/billions-bounty-v2/target/deploy/billions_bounty_v2.so \
  --url devnet

# 6. Initialize
cd programs/billions-bounty-v2
USDC_MINT=JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh \
BOUNTY_POOL_WALLET=CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF \
OPERATIONAL_WALLET=46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D \
BUYBACK_WALLET=7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya \
STAKING_WALLET=Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX \
npx ts-node scripts/init_v2_raw.ts

# 7. Test
npx ts-node scripts/test_v2_direct.ts
```

**Pros**: Clean solution, new deployment with correct USDC mint  
**Cons**: Requires installing older Rust version

---

### Option C: Manual Build on Different Machine

If you have access to another machine with an older Rust version:

1. Copy the source code
2. Build there
3. Copy the .so file back
4. Deploy

---

## What We've Accomplished

1. ✅ Fixed all IDL issues for Anchor 0.30.x
2. ✅ Updated USDC mint to your test token
3. ✅ Fixed contract code (added `init_if_needed` for buyback_tracker)
4. ✅ Generated new program keypair
5. ✅ Updated all source files with new program ID
6. ✅ IDL generator working perfectly
7. ✅ Test scripts ready
8. ⚠️ **BLOCKED**: Cannot rebuild due to Cargo.lock version mismatch

---

## Recommendation

**Go with Option B** (Downgrade Cargo):
- It's the proper solution
- Takes only 15 minutes
- Gives you a clean deployment
- Solves the problem permanently for this project

Run this now:
```bash
rustup install 1.75.0
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/programs/billions-bounty-v2
rustup override set 1.75.0
rm -f Cargo.lock
cargo build-sbf
```

Then we can deploy and test!

---

## Files Ready

All these files have the new program ID and are ready to use once we rebuild:

- ✅ `src/lib.rs` - declare_id! updated
- ✅ `Anchor.toml` - program ID updated
- ✅ `scripts/test_v2_direct.ts` - program ID updated
- ✅ `scripts/init_v2_raw.ts` - program ID updated
- ✅ `scripts/generate_idl.js` - program ID updated
- ✅ IDL fixes automated and working
- ✅ USDC mint updated to your test token
- ✅ All wallet addresses configured

**We're 99% there - just need to rebuild!**

