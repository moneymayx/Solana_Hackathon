# E2E Test Plan - Contract V2 (Staging)

## Preconditions
- ✅ Devnet program deployed: `GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm`
- ✅ IDL published: `HicBwRnacuFcfYXWGBFSCWofc8ZmJU4v4rKKxtxvXBQr`
- ✅ Global PDA initialized: `F4YATUC3tEA3Gb3Tt3v7sZBT9iKRhHXJsZ6s7nBWKDgh`
- ✅ Bounty[1] initialized: `AJC6D2mvMcktdzpJJQmbYXkTZn9xGpd2C3qm4VAZK83Z`
- Staging env with `USE_CONTRACT_V2=true`
- Test wallets funded (≥2 SOL + test USDC)

## Scenarios
1. Initialize Global + Bounty
2. Entry Payment
   - Correct 60/20/10/10 distribution observed on token accounts
   - Bounty pool increments; total_entries increments
3. Price Escalation
   - Second entry requires higher price; reject < required
4. AI Decision (format verification)
   - Hash match required; signature length 64 required
   - Nonce PDA increments
5. Buyback Primitive
   - Allocation increments and execute reduces allocation

## Negative Cases
- Insufficient payment
- Wrong nonce PDA
- Zero amount
- Disabled lottery/bounty

## Observability
- Event logs captured
- Backend logs (adapter v2) include request/response

## Rollback
- Set `USE_CONTRACT_V2=false` and verify legacy flows unaffected
