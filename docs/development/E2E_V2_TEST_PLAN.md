# E2E Test Plan - Contract V2 (Staging)

## Preconditions
- ✅ Devnet program deployed: `HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`
- ✅ IDL generated locally (use raw Web3.js for client integration)
- ✅ Global PDA initialized: `BursCahsMxKjiSUgTCy11uUTWnaZ1eqcGcADUxiMzHMb`
- ✅ Bounty[1] initialized: `2J455GTdBfceWWUF7dcPawixW4PEfWBdVgX7Soqc3trb`
- ✅ Buyback Tracker initialized: `9ceXx23oRrdAzdzUTzgj224y4KYhXN5eSug2CkJHpZpr`
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
