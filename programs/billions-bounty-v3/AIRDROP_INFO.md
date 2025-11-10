# Airdrop Requirements for V3 Tests

## Overview

The tests generate **random keypairs** dynamically, so wallet addresses change each test run. They need **SOL for transaction fees**, not USDC.

---

## Wallets Needing Airdrops

Each test suite requests airdrops to **4-5 dynamically generated wallets**:

### Test Wallets (Generated per test run)
1. **authority** - 2 SOL (lottery authority, creates mint)
2. **user** - 2 SOL (test user making payments)
3. **jackpotWallet** - 2 SOL (jackpot recipient)
4. **backendAuthority** - 2 SOL (backend signing authority)
5. **attacker** - 2 SOL (only in edge_cases.spec.ts)

**Total per test suite**: ~8-10 SOL in airdrops

**Note**: These are randomly generated, so addresses change every run.

---

## Current Issue

The tests are hitting **devnet rate limits (429 errors)** when requesting airdrops because:
- Each test suite requests 4-5 airdrops
- Devnet limits airdrop requests per IP/wallet
- Multiple test suites run in parallel, multiplying requests

---

## Solutions

### Option 1: Use Your Wallet to Fund (Recommended)

The **provider wallet** (your `~/.config/solana/id.json`) already has SOL. You can transfer from it instead of airdropping:

**Check your wallet balance:**
```bash
solana balance --url devnet
```

**If you have enough SOL (> 20 SOL), modify tests to:**
- Transfer SOL from provider wallet to test accounts instead of airdropping
- This bypasses rate limits

### Option 2: Pre-fund Test Wallets

Create fixed test wallets and fund them once:
```bash
# Create test wallets
solana-keygen new --outfile test_authority.json
solana-keygen new --outfile test_user.json
# ... etc

# Fund them manually (using faucet or transfers)
solana transfer test_authority.json 2 --allow-unfunded-recipient --url devnet
```

Then modify tests to use these fixed wallets instead of generating new ones.

### Option 3: Use Local Validator (Best for Testing)

```bash
# Terminal 1: Start local validator with unlimited SOL
solana-test-validator --reset

# Terminal 2: Run tests (no rate limits!)
cd programs/billions-bounty-v3
anchor test
```

### Option 4: Increase Delays Between Airdrops

Add longer delays between airdrop requests to avoid rate limits:
```typescript
await provider.connection.requestAirdrop(authority.publicKey, 2 * anchor.web3.LAMPORTS_PER_SOL);
await new Promise(resolve => setTimeout(resolve, 3000)); // Wait 3 seconds
await provider.connection.requestAirdrop(user.publicKey, 2 * anchor.web3.LAMPORTS_PER_SOL);
// etc...
```

---

## Current Provider Wallet

**Wallet**: Your default Solana wallet (`~/.config/solana/id.json`)  
**Address**: Check with `solana address --url devnet`  
**Balance**: Check with `solana balance --url devnet`

**This wallet does NOT need an airdrop** - it's the one making the requests.

---

## Quick Check

Run this to see your current wallet balance:
```bash
solana balance --url devnet
```

If you have **> 20 SOL**, you can modify the tests to transfer from your wallet instead of airdropping.

---

## Recommended Approach

**For immediate testing**: Use local validator (Option 3)  
**For devnet testing**: Modify tests to transfer from provider wallet (Option 1)  
**For CI/CD**: Use pre-funded test wallets (Option 2)

