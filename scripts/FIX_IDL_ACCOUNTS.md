# IDL Account List Issue

## Problem
The IDL generated for `initializeLottery` is missing accounts compared to the Rust definition.

### IDL Shows (6 accounts):
1. lottery
2. authority
3. jackpotTokenAccount
4. usdcMint
5. tokenProgram
6. systemProgram

### Rust Code Has (8 accounts):
1. lottery
2. authority
3. jackpot_wallet ← **MISSING IN IDL**
4. jackpot_token_account
5. usdc_mint
6. token_program
7. associated_token_program ← **MISSING IN IDL**
8. system_program

## Solution
The IDL needs to be regenerated with the correct Anchor version. The current IDL was generated with an older or incorrect version of Anchor that didn't capture all accounts.

## Fix
1. Update Anchor CLI to match Anchor.toml version (0.31.2) or use the version that matches package.json (0.30.1)
2. Run `anchor build` to regenerate IDL
3. Verify IDL has all 8 accounts

## Alternative
Manually fix the IDL JSON to add the missing accounts, but this is error-prone and may cause other issues.

