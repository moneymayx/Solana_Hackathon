# Rounding Invariants — Billions Bounty V3

This document captures the key arithmetic invariants that guard against the kind of rounding/precision exploits described in the Balancer v2 incident. Each invariant makes explicit whether rounding should favor the protocol or the user, and how to validate the invariant at runtime.

## Invariant 1: Entry Payment Split (60/40)

- **Purpose**: Every entry amount must be split into 60% for the jackpot (research fund) and 40% for the buyback wallet.
- **Rounding Direction**: Integer division rounds **down** for the jackpot contribution; any remainder is retained by the protocol via the buyback amount. This favors the protocol because unexpected dust never inflates the jackpot.
- **Validation Guidance**: Always check `jackpot_amount + buyback_amount == entry_amount`. If the split ever loses or creates dust, fail the transaction.

## Invariant 2: Escape Plan Distribution (20/80)

- **Purpose**: When the escape plan triggers, 20% of the jackpot goes to the last participant and 80% to the community pool.
- **Rounding Direction**: Integer division rounds down for the last participant share; any remainder stays with the community pool. This ensures the protocol keeps the extra dust instead of handing it to a single user.
- **Validation Guidance**: Check `last_participant_share + community_share == total_jackpot`. Document that the community share absorbs any dust.

## Invariant 3: Emergency Recovery Cap (10%)

- **Purpose**: Emergency recovery must never extract more than 10% of the jackpot in a single call.
- **Rounding Direction**: Integer division truncates down, so the authority can never claim more than 10% (it cannot round upward and steal extra funds).
- **Validation Guidance**: No additional adjustment required, but log the `max_recovery_allowed` value so audits can confirm the truncation behavior.

## Invariant 4: Total Input Conservation

- **Purpose**: Across every multi-transfer action, the total tokens moved must equal the amount provided by the user or stored in the jackpot.
- **Rounding Direction**: Donations and payouts round **toward the protocol** when dust is unavoidable.
- **Validation Guidance**: Maintain runtime `require!` statements that explicitly assert each sum equality described above. Failing the invariant must revert the instruction.

## Testing Guidance

- Cover these invariants with deterministic edge case tests (entries that do not divide evenly, escape plan with odd jackpots) and fuzzing (random entry amounts between 1 and 1,000,000 USDC). Each test should assert the sum invariants so regressions are caught during CI.

