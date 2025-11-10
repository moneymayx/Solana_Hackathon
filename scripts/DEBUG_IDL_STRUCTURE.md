# IDL Structure Debug

## Issue
Anchor's `AccountClient` is trying to read `size` from `undefined`, causing:
```
TypeError: Cannot read properties of undefined (reading 'size')
at new AccountClient
```

## Findings

### 1. Program ID Check ✅
- Source: `ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb` ✅
- IDL: `ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb` ✅
- Deployed: `ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb` ✅
- **All match!**

### 2. Anchor Version Mismatch ⚠️
- Installed CLI: `0.30.1`
- Anchor.toml expects: `0.31.2` (but toolchain says `0.30.1`)
- NPM package: `@coral-xyz/anchor@0.30.1`

### 3. IDL Account Structure
Accounts in IDL have:
- `name`: "lottery" or "entry"
- `discriminator`: 8-byte array
- `type`: Object with `kind: "struct"` and `fields` array
- **Missing**: `size` property

### 4. Anchor AccountClient Expectation
Anchor's `AccountClient` constructor tries to read `size` from account metadata.
The location where it's reading from is undefined.

## Solution Options

### Option A: Rebuild IDL with correct Anchor version
```bash
cd programs/billions-bounty-v3
anchor build
# This should regenerate IDL with proper account sizes
```

### Option B: Manually patch IDL file permanently
Add `size` field directly to `target/idl/billions_bounty_v3.json`

### Option C: Use tests to initialize (they work!)
The tests successfully initialize because they use Anchor's test framework which handles IDL differently.

### Option D: Skip Anchor Program class entirely
Use raw Web3.js instructions (but we tried this and got program ID mismatch)

## Next Steps

Since tests work, the best approach is likely:
1. Use Anchor's test framework to initialize
2. OR rebuild IDL properly
3. OR find why tests work but scripts don't (might be AnchorProvider.env() vs manual provider)

