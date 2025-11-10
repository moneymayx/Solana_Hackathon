# Wallet Balance Clarification

## Current Status

**Provider Wallet**: `ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC`
- **Current Balance Check**: 0.307 SOL (checked via `solana balance --url devnet`)
- **Program Authority**: 2.18 SOL (this is the **program data account**, not the wallet)

---

## Confusion Point

When you see "14 SOL" or "2.18 SOL", it might be referring to:

1. **Program Data Account Balance** (2.18 SOL)
   - This is the SOL stored in the **program's data account** on-chain
   - Shows when you run: `solana program show ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb`
   - This is NOT available for transfers - it's locked in the program account

2. **Provider Wallet Balance** (0.307 SOL)
   - This is the SOL in the **wallet file** (`~/.config/solana/id.json`)
   - This is what the tests use to transfer to test accounts
   - This is what needs funding

---

## Why the Provider Wallet Balance is Low

The provider wallet (`ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC`) only has **0.307 SOL**, which is not enough to fund all the test accounts.

When tests try to transfer:
- Need: ~3-5 SOL total (0.5 SOL × 4-5 accounts per test suite × 3 test suites)
- Have: 0.307 SOL
- Result: ❌ Insufficient funds

---

## Solution

If you have **14 SOL somewhere**, we need to identify where it is:

1. **Check if it's in a different wallet**:
   ```bash
   # Check all known wallets
   solana balance WALLET_ADDRESS --url devnet
   ```

2. **Transfer from that wallet to the provider wallet**:
   ```bash
   solana transfer ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC 5 --from OTHER_WALLET --url devnet
   ```

3. **Or use local validator** (best option):
   - Unlimited SOL for testing
   - No rate limits
   - Faster test execution

---

## Verification

**Current provider wallet balance** (what tests use):
```bash
$ solana balance --url devnet
0.307350294 SOL
```

**Program data account balance** (not usable for transfers):
```bash
$ solana program show ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb --url devnet | grep Balance
Balance: 2.18118744 SOL
```

These are **different accounts**! The program data account SOL is locked in the program and can't be used for test transfers.

---

**Bottom line**: If you have 14 SOL somewhere, we need to transfer it to `ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC` (the provider wallet).

