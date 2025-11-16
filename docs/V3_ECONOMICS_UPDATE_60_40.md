## V3 Economics Update – 60/40 Jackpot/Buyback Split

### Overview

The V3 lottery contract now uses a **60/40 split** for every user entry:

- **60%** of each entry is added to the on-chain **jackpot pot**, which is paid out entirely to the winner when a successful jailbreak is detected.
- **40%** of each entry is routed directly to a dedicated **USDC buyback wallet** that funds automatic buy-and-burn operations for the 100Bs token.

This replaces the older **60/20/10/10** model. Operational costs and staking rewards are now funded from separate treasury flows, not from per-entry percentages.

### Smart Contract Changes (V3)

- `process_entry_payment` in `programs/billions-bounty-v3/src/lib.rs`:
  - Calculates `jackpot_amount = 60%` and `buyback_amount = 40%` of `entry_amount`.
  - Increases `lottery.current_jackpot` by **only** the 60% contribution.
  - Transfers:
    - 60% from `user_token_account` → `jackpot_token_account`.
    - 40% from `user_token_account` → `buyback_token_account`.
  - Reuses existing fields:
    - `research_contribution` now represents the **60% jackpot contribution**.
    - `operational_fee` now represents the **40% buyback allocation** (for backward compatibility).
  - `ProcessEntryPayment` accounts now include:
    - `buyback_wallet`
    - `buyback_token_account`

### Backend Changes

- `src/config/token_config.py`:
  - `BOUNTY_CONTRIBUTION_RATE = 0.60`
  - `BUYBACK_RATE = 0.40`
  - `OPERATIONAL_FEE_RATE` and the old staking percentage are effectively **0.0** and treated as deprecated for v3 per-entry flows.
  - `REVENUE_SPLIT_TOTAL` now validates `60% + 40% = 100%`.

- `src/services/smart_contract_service.py`:
  - Uses `BOUNTY_CONTRIBUTION_RATE` and `BUYBACK_RATE` from `token_config`.
  - Logs:
    - `Jackpot (60%)` and `Buyback (40%)` for each entry.
  - Records entries so that:
    - `bounty_contribution` = 60% jackpot contribution.
    - `operational_fee` field in `extra_data` semantically represents the 40% buyback allocation (kept for compatibility).

### Frontend Changes

- `frontend/src/lib/v3/idl.json`:
  - `processEntryPayment` accounts now include `buybackWallet` and `buybackTokenAccount`.

- `frontend/src/lib/v3/paymentProcessor.ts`:
  - Derives the buyback wallet from:
    - `NEXT_PUBLIC_V3_BUYBACK_WALLET` (preferred), or
    - `NEXT_PUBLIC_BUYBACK_WALLET_ADDRESS` (fallback).
  - Derives the buyback USDC ATA and passes both buyback accounts into the `process_entry_payment` instruction.

- `frontend/src/lib/v3/README.md`:
  - Documents the new **60/40 jackpot/buyback** economics and the required buyback wallet environment variable.

### Testing & Monitoring

- `scripts/test_revenue_split.py`:
  - Updated narrative and calculations to describe and display the **60/40** split.

- `tests/test_revenue_split_verification.py`:
  - Reframed as a v3-focused verification, emphasizing 60% jackpot and 40% buyback semantics.

- `tests/test_mainnet_readiness.py`:
  - `check_revenue_split_configuration` now expects:
    - `BOUNTY_CONTRIBUTION_RATE = 0.60`
    - `BUYBACK_RATE = 0.40`
  - Total per-entry split = 100% (jackpot + buyback).

### Documentation Touchpoints

- `README.md`:
  - The “Revenue Distribution” section now describes the **60/40 jackpot/buyback split** and clarifies that staking/ops are funded elsewhere.

- Historical V2 documentation under `docs/archive/v2_consolidation/` still references the older **60/20/10/10** split for accuracy but is clearly scoped to **V2** behavior.

### Operational Notes

- Ensure the **buyback wallet** used in:
  - `.env` (`BUYBACK_WALLET_ADDRESS`, `V3_BUYBACK_WALLET`), and
  - Frontend env (`NEXT_PUBLIC_V3_BUYBACK_WALLET` or `NEXT_PUBLIC_BUYBACK_WALLET_ADDRESS`)
  all point to the same USDC account used for 100Bs buy-and-burn.
- When inspecting devnet/mainnet transactions:
  - Verify that for test entries, the jackpot PDA’s USDC ATA increases by **60%** of the payment.
  - Verify that the buyback ATA increases by **40%** of the payment.


