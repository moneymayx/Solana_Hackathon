# V3 IDL Rebuild Attempt Summary

## Attempted: Install Anchor 0.31.2 and Rebuild IDL

### Results

✅ **NPM Install**: Successfully installed `@coral-xyz/anchor-cli@0.31.2`

❌ **Version Check**: Anchor still reports version mismatch:
- Installed: `0.31.2` (via npm)
- System uses: `0.30.1` (via cargo)
- Error: "Expected anchor-cli 0.31.2, found anchor-cli 0.30.1"

### Root Cause Analysis

1. **NPM Package Limitation**: The npm package says "Only x86_64 / Linux distributed in NPM package right now", so on macOS it falls back to cargo-installed version (0.30.1)

2. **Cargo Install Blocked**: 
   - Attempting `cargo install anchor-cli --version 0.31.2` fails: version not in registry
   - Attempting `cargo install anchor-cli` (latest) fails: requires Rust 1.81+, system has 1.75.0

3. **Where 0.31.2 Expectation Comes From**: 
   - Unknown source - not in Anchor.toml (which says 0.30.1)
   - Possibly cached in Anchor registry or workspace metadata

### Current IDL Status

✅ **IDL Already Patched**: The IDL at `target/idl/billions_bounty_v3.json` has:
- ✅ 8 accounts in `initializeLottery` (includes `jackpotWallet` and `associatedTokenProgram`)
- ✅ Size fields added to accounts (lottery: 194, entry: 73)
- ✅ Size fields added to types array
- ✅ Last modified: Nov 2 12:04 (after our manual patches)

### Build Blockers

1. **Anchor Version Check**: Won't proceed without matching versions
2. **Rust Dependency Conflicts**: Workspace has conflicting `solana-program` versions:
   - V3 needs: `solana-program ^1.17.3` (from anchor-lang 0.30.1)
   - NFT-verification needs: `solana-program >=1.14, <1.17` (from anchor-lang 0.28.0)
3. **Direct Cargo Build**: Fails due to workspace dependency conflicts

### Options Moving Forward

1. **Use Patched IDL As-Is**: The IDL has all manual fixes applied. Test initialization with current IDL.

2. **Fix Workspace Dependencies**: Update all programs to compatible Anchor/Solana versions

3. **Build Outside Workspace**: Copy V3 to isolated directory and build there (breaks workspace benefits)

4. **Manual IDL Update**: Continue using manually patched IDL - it has all required fields

### Recommendation

Since the IDL is already properly patched with all required fields, proceed with testing initialization using the current patched IDL rather than attempting to rebuild, which is blocked by multiple systemic issues.

---

## 2025-11-10 Update
- After adding `entry_nonce`, manually re-synced IDL:
  ```bash
  cp frontend/src/lib/v3/idl.json target/idl/billions_bounty_v3.json
  ```
- Frontend + backend now share the same IDL (includes `entryNonce` argument and updated account list)

