# Wallet Funding Explanation

## How It Works

The tests use **two types of wallets**:

### 1. Provider Wallet (Fixed - Needs Funding)
- **Address**: `ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC`
- **Current Balance**: 0.307 SOL
- **Location**: `~/.config/solana/id.json`
- **Role**: This is the **source wallet** that funds the test accounts
- **Status**: ❌ Needs more SOL (currently insufficient)

### 2. Test Wallets (Dynamic - Generated Each Run)
- **Generated with**: `Keypair.generate()` - creates random wallets each test run
- **Addresses**: Change every time tests run
- **Examples**:
  - `authority` - Random address each time
  - `user` - Random address each time
  - `jackpotWallet` - Random address each time
  - `backendAuthority` - Random address each time

---

## The Flow

```
1. Provider Wallet (Apmfs...C) 
   ↓ [has 0.307 SOL - NOT ENOUGH]
   ↓ 
2. Tests generate random wallets: authority, user, jackpotWallet, etc.
   ↓
3. Tests try to transfer SOL from Provider → Test Wallets
   ↓
4. ❌ FAILS: Provider wallet doesn't have enough SOL
```

---

## Solution 1 Explanation

**Solution 1** means: **Fund the Provider Wallet** (the fixed one), not the test wallets.

The test wallets are **destination wallets** that receive SOL from the provider wallet. We don't need to know their addresses because:
- They're created by the tests
- The tests handle transferring SOL to them automatically
- We just need the **source wallet** (provider) to have enough SOL

### What Solution 1 Actually Does:

```bash
# This funds the PROVIDER wallet (source of funds)
solana transfer ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC 5 --url devnet

# Then when tests run:
# 1. Tests generate random wallets (we don't know addresses yet)
# 2. Tests transfer from Provider Wallet → Random Test Wallets
# 3. Tests use funded test wallets for testing
```

---

## Current Test Code Flow

```typescript
// Step 1: Generate random test wallets (addresses unknown until runtime)
authority = Keypair.generate();      // Random address
user = Keypair.generate();           // Random address  
jackpotWallet = Keypair.generate();   // Random address
backendAuthority = Keypair.generate(); // Random address

// Step 2: Get the provider wallet (fixed address: Apmfs...C)
const providerWallet = provider.wallet;

// Step 3: Transfer from Provider → Test Wallets
// This is where it fails - provider doesn't have enough SOL
await provider.sendAndConfirm(
  SystemProgram.transfer({
    fromPubkey: providerWallet.publicKey,  // Apmfs...C (needs SOL)
    toPubkey: authority.publicKey,        // Random address (receives SOL)
    lamports: 0.5 * LAMPORTS_PER_SOL
  })
);
```

---

## Summary

**You only need to fund ONE wallet** - the provider wallet (`ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC`).

The test wallets are dynamically generated and receive SOL automatically from the provider wallet during test execution. You don't need to know their addresses ahead of time.

---

## Recommended: Use Local Validator

Since devnet airdrops are rate-limited, the best solution is to use a local validator:

```bash
# Terminal 1: Start local validator (unlimited SOL)
solana-test-validator --reset

# Terminal 2: Run tests
cd programs/billions-bounty-v3
anchor test  # No rate limits, unlimited SOL!
```

This avoids all funding issues because local validators start with unlimited SOL for testing.

