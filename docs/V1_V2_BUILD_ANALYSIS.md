# V1 and V2 Build Method Analysis

## Findings from Deployment Logs

### V1 Build Method
- **Location**: `scripts/deployment/deploy_devnet.sh`
- **Command**: `cargo build-sbf` (line 68)
- **Context**: Direct build in program directory
- **Result**: ✅ Successfully deployed
- **Program ID**: `4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK`

### V2 Build Method (from V2_COMPLETE_STATUS.md)
- **Documentation**: `docs/archive/v2_consolidation/V2_COMPLETE_STATUS.md`
- **Key Quote**: "Solved by using Solana's Rust toolchain (`rustup run solana cargo`) to generate v3 lockfiles"
- **Command**: `rustup run solana cargo build-sbf` (likely without --release flag)
- **Result**: ✅ Successfully built and deployed
- **Program ID**: `HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`

## Critical Discovery

The documentation says V2 used `rustup run solana cargo` but:
- When we tried this with V3, it uninstalled the Solana toolchain
- The exact command syntax may differ
- V2 was likely built with **Anchor 0.28.0 or earlier** (compatible with Rust 1.75.0)

## V3 Current State

- **Anchor 0.31.1**: Requires Rust 1.79.0+
- **Solana Rust 1.75.0**: Cannot compile Anchor 0.31.1 dependencies
- **Blocked**: Toolchain incompatibility

## Solution: Downgrade V3 to Anchor 0.28.0

Since V2 successfully built, and Anchor 0.28.0 was the version documented in CONTRACT_V2_README.md, we should:

1. **Downgrade V3 to Anchor 0.28.0** (same as V2 originally)
2. **Use the same build command**: `cargo build-sbf` (like V1)
3. **Or**: `rustup run solana cargo build-sbf` (like V2)

This avoids both:
- Anchor 0.30.1 workspace bug
- Anchor 0.31.1+ Rust 1.79+ requirement

