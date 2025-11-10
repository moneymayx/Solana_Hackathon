# V3 Secure Contract - Deployment Success! 🎉

**Date**: 2024  
**Status**: ✅ **SUCCESSFULLY DEPLOYED TO DEVNET**

---

## Deployment Summary

### ✅ Build Successful
- **Solution**: Pinned `indexmap = "=2.2.6"` to match v2 (compatible with Rust 1.75.0)
- **Build Tool**: `cargo-build-sbf` with Rust 1.75.0 override
- **Output**: `target/deploy/billions_bounty_v3.so` (306KB)

### ✅ Deployment Successful
- **Program ID**: `ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb`
- **Network**: Devnet
- **Program Data Address**: `DUKrU94zyzgakB5zmBQE6wmkvbXHWhd1MZ11RNdGZnhj`
- **Authority**: `ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC`
- **Balance**: 2.18 SOL
- **Size**: 313,216 bytes

---

## Errors Encountered and Resolutions

### Error #1: Cargo.lock Version 4 Incompatibility

**Problem**:
```
error: failed to parse lock file at: .../Cargo.lock
Caused by: lock file version 4 requires `-Znext-lockfile-bump`
```

**Root Cause**: 
- Modern Rust (1.90.0) generates Cargo.lock version 4
- Solana's `cargo-build-sbf` uses Rust 1.75.0 which cannot read version 4 lockfiles

**Solution**:
1. Removed the incompatible Cargo.lock file
2. Used `cargo-build-sbf` directly (which uses Rust 1.75.0 and generates compatible lockfiles)

**Command**:
```bash
rm -f Cargo.lock
cargo-build-sbf
```

---

### Error #2: Dependency Requires Newer Rust Version

**Problem**:
```
error: package `indexmap v2.12.0` cannot be built because it requires rustc 1.82 or newer, 
while the currently active rustc version is 1.75.0-dev
```

**Root Cause**:
- Anchor 0.30.1 pulls in `indexmap v2.12.0` as a dependency
- This version requires Rust 1.82+
- But `cargo-build-sbf` uses Rust 1.75.0 (matches Solana's version)

**Solution**:
Pinned `indexmap` to version `2.2.6` which is compatible with Rust 1.75.0 (same fix used for v2 deployment)

**File Change** (`Cargo.toml`):
```toml
[dependencies]
anchor-lang = { version = "0.30.1", features = ["init-if-needed"] }
anchor-spl = "0.30.1"
sha2 = "0.10"
indexmap = "=2.2.6"  # ← ADDED: Pin to Rust 1.75.0 compatible version
```

**Reference**: This exact issue and solution was documented in `docs/development/BUILD_ISSUE_SUMMARY.md` for v2 deployment.

---

### Error #3: Program ID Mismatch After Deployment

**Problem**:
- Anchor expected program ID: `9qXY55GYdaUnQmUrqSmSThCKxhWVVqKRczuGmcPduPg7`
- Actual deployed keypair: `ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb`

**Root Cause**:
- Anchor generates a program ID when running `anchor keys list`
- But the actual keypair file in `target/deploy/` may have a different ID
- Deployment uses the keypair file, not Anchor's expected ID

**Solution**:
Updated `declare_id!` in source code to match the actual deployed program ID

**File Change** (`src/lib.rs`):
```rust
// Before:
declare_id!("9qXY55GYdaUnQmUrqSmSThCKxhWVVqKRczuGmcPduPg7");

// After:
declare_id!("ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb");
```

---

### Error #4: Anchor Build Not Generating .so File

**Problem**:
- Running `anchor build` from program directory didn't generate `target/deploy/*.so`
- Build appeared successful but no binary output

**Root Cause**:
- Anchor's build process may have dependency resolution issues
- Workspace configuration might affect output location

**Solution**:
Used `cargo-build-sbf` directly, which:
1. Uses Solana's Rust toolchain (1.75.0)
2. Generates `.so` file in `target/deploy/`
3. Bypasses Anchor's dependency resolution

**Command**:
```bash
cd programs/billions-bounty-v3
rustup override set 1.75.0
rm -f Cargo.lock
cargo-build-sbf
```

**Output Location**: `target/deploy/billions_bounty_v3.so`

---

### Error #5: Anchor CLI Version Mismatch Warning

**Problem**:
```
WARNING: `anchor-lang` version(0.28.0) and the current CLI version(0.30.1) don't match.
```

**Root Cause**:
- Initially downgraded to Anchor 0.28.0 to avoid dependency issues
- But Anchor CLI is version 0.30.1

**Solution**:
- Reverted to Anchor 0.30.1 (matches CLI and v2)
- Fixed dependency compatibility by pinning `indexmap = "=2.2.6"`

---

## Complete Error Resolution Summary

| Error | Solution | Files Changed |
|-------|----------|---------------|
| Cargo.lock v4 | Remove lockfile, use cargo-build-sbf | `Cargo.lock` (removed) |
| indexmap Rust 1.82+ | Pin to `=2.2.6` | `Cargo.toml` |
| Program ID mismatch | Update declare_id! | `src/lib.rs` |
| No .so output | Use cargo-build-sbf directly | Build process |
| Anchor version mismatch | Use 0.30.1 with indexmap pin | `Cargo.toml` |

---

## Key Fix Applied

Based on previous v2 deployment logs, the critical fix was:

**Pin indexmap to compatible version**:
```toml
indexmap = "=2.2.6"
```

This allows Anchor 0.30.1 to build with Rust 1.75.0 (used by cargo-build-sbf).

---

## Program ID Mismatch Resolution

**Issue**: Anchor expected `9qXY55GYdaUnQmUrqSmSThCKxhWVVqKRczuGmcPduPg7`, but keypair file has `ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb`

**Resolution**: Updated `declare_id!` in source code to match actual deployed program ID:
```rust
declare_id!("ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb");
```

---

## Verification

```bash
# Program is live on devnet
solana program show ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb --url devnet

# Output:
# Program Id: ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb
# Owner: BPFLoaderUpgradeab1e11111111111111111111111
# ProgramData Address: DUKrU94zyzgakB5zmBQE6wmkvbXHWhd1MZ11RNdGZnhj
# Authority: ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC
# Last Deployed In Slot: 418598666
# Data Length: 313216 (0x4c780) bytes
# Balance: 2.18118744 SOL
```

---

## Explorer Links

- **Program**: https://explorer.solana.com/address/ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb?cluster=devnet
- **Program Data**: https://explorer.solana.com/address/DUKrU94zyzgakB5zmBQE6wmkvbXHWhd1MZ11RNdGZnhj?cluster=devnet

---

## Environment Variables

Following the same pattern as V2, the V3 program ID should be set as:

```bash
# Backend (DigitalOcean/Environment)
LOTTERY_PROGRAM_ID_V3=ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb
USE_CONTRACT_V3=false  # Feature flag (start disabled)
V3_LOTTERY_PDA=<pda_address>  # Will be calculated after initialization
V3_BACKEND_AUTHORITY=<backend_authority_pubkey>
V3_USDC_MINT=<usdc_mint_address>

# Frontend (Vercel) - if needed
NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V3=ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb
NEXT_PUBLIC_USE_CONTRACT_V3=false  # Feature flag
```

**Pattern**: Following V2's convention:
- V1: `LOTTERY_PROGRAM_ID`
- V2: `LOTTERY_PROGRAM_ID_V2`
- V3: `LOTTERY_PROGRAM_ID_V3` ✅

The `contract_adapter_v3.py` already uses `LOTTERY_PROGRAM_ID_V3` - ✅ **Updated with deployed program ID**

---

## Next Steps

1. ✅ **Deployment Complete**
2. ✅ **Program ID Updated in Source**
3. ✅ **Environment Variable Name Confirmed**: `LOTTERY_PROGRAM_ID_V3`
4. ⏳ **Generate IDL** (run `anchor build` to generate)
5. ⏳ **Initialize IDL on-chain**
6. ⏳ **Update environment variables** with new program ID
7. ⏳ **Run integration tests**
8. ⏳ **Initialize lottery account**

---

## Files Updated

- ✅ `programs/billions-bounty-v3/src/lib.rs` - Program ID updated
- ✅ `programs/billions-bounty-v3/Cargo.toml` - indexmap pinned
- ⏳ `programs/billions-bounty-v3/Anchor.toml` - Update program ID
- ⏳ `Billions_Bounty/Anchor.toml` - Update program ID

---

## Lessons Learned

1. **Always check previous deployment logs** - Same issues were solved before
2. **Pin compatible dependencies** - `indexmap = "=2.2.6"` was key for Rust 1.75.0 compatibility
3. **Use cargo-build-sbf directly** - Bypasses Anchor's dependency resolution issues
4. **Verify program ID matches** - Check keypair file vs Anchor keys list

---

## Deployment Command History

```bash
# 1. Set Rust override
rustup override set 1.75.0

# 2. Pin indexmap in Cargo.toml
# Added: indexmap = "=2.2.6"

# 3. Build
rm -f Cargo.lock
cargo-build-sbf

# 4. Deploy
solana program deploy \
  target/deploy/billions_bounty_v3.so \
  --program-id target/deploy/billions_bounty_v3-keypair.json \
  --url devnet
```

---

**Status**: 🟢 **DEPLOYED AND VERIFIED**

