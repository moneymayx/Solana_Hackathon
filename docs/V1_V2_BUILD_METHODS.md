# V1 and V2 Build Methods - Reference Guide

## Summary

After examining deployment logs and status documents, here's how V1 and V2 were successfully built:

### V1 Build Method
- **Command**: `cargo build-sbf`
- **Location**: `scripts/deployment/deploy_devnet.sh` (line 68)
- **Result**: ✅ Successfully deployed to devnet
- **Program ID**: `4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK`

### V2 Build Method
- **Command**: `rustup run solana cargo build-sbf`
- **Location**: `docs/archive/v2_consolidation/V2_COMPLETE_STATUS.md` (line 11)
- **Key Fix**: "Solved by using Solana's Rust toolchain (`rustup run solana cargo`) to generate v3 lockfiles"
- **Result**: ✅ Successfully deployed to devnet
- **Program ID**: `HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`

## Key Difference

**V2's success** came from using `rustup run solana cargo` instead of direct `cargo-build-sbf`:
- This ensures Solana's Rust 1.75.0 is used consistently
- Generates Cargo.lock v3 (compatible with Solana toolchain)
- Avoids lockfile version conflicts

## Applying to V3

Use the same method that worked for V2:

```bash
cd programs/billions-bounty-v3
rustup run solana cargo build-sbf --release
```

This should work even with Anchor 0.31.1 dependencies if the lockfile is v3.

## Initialization Methods

### V1 Initialization
- Not fully documented, but program deployed and active
- Likely used Anchor's initialization commands

### V2 Initialization
- **Method**: TypeScript script (`init_v2_raw.ts`)
- **Transactions**:
  - `initialize_lottery`: `wuBg9FscP71pHSzNE5jBGsdRVJtASE35WoBETAx8X6H43JSatHKdjzJvaa3psA3qv4KWL5WdRcvkXoBrJRoeKhF`
  - `initialize_bounty`: `4MNgLTDuJ49ZGrqGA9nctKF2MisGuNkQfq7Nu6jcnaLBW4deo8auUqjW55k9GhuBf38CZLm8zrKzrhuEWcwgxbUY`
- **Status**: ✅ Fully initialized with all PDAs

## Deployment Commands

### V1 Deployment (from deploy_devnet.sh)
```bash
cd programs/billions-bounty
cargo build-sbf
cd ../..
solana program deploy \
    --program-id target/deploy/billions_bounty-keypair.json \
    programs/billions-bounty/target/deploy/billions_bounty.so \
    --url https://api.devnet.solana.com
```

### V2 Deployment
```bash
cd programs/billions-bounty-v2
rustup run solana cargo build-sbf --release
anchor deploy --program-name billions_bounty_v2 --provider.cluster devnet
```

## Recommendation for V3

**Use V2's proven method**:
1. Build: `rustup run solana cargo build-sbf --release`
2. Deploy: `solana program deploy --program-id <keypair> <binary.so> --url devnet`
3. Initialize: Use raw TypeScript/JavaScript instructions (like V2)

This method successfully resolved Cargo.lock v4 issues for V2 and should work for V3.

