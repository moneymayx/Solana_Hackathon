# Contract V2 Integration Plan (Parallel Rollout)

## Goals
- Integrate `programs/billions-bounty-v2` without breaking existing backend/frontend.
- Use feature flags to switch traffic gradually.
- Complete testing suite before any production switch.

## Feature Flags
- Backend env:
  - `USE_CONTRACT_V2=false` (default)
  - `LOTTERY_PROGRAM_ID_V2=HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`
  - `BOUNTY_POOL_WALLET=...`
  - `OPERATIONAL_WALLET=...`
  - `BUYBACK_WALLET=...`
  - `STAKING_WALLET=...`

## Parallel Integration Steps
1. Keep existing flows on v1; wire v2 behind adapter:
   - Use `src/services/contract_adapter_v2.py` when `USE_CONTRACT_V2=true`.
2. Duplicate critical backend call paths under `src/services/v2/` (isolated):
   - Mirror serialization, RPC, and error handling for entries, AI decision, buyback.
   - Point E2E tests at v2 endpoints only.
3. Extract and store IDL for v2:
   - `anchor idl extract -o programs/billions-bounty-v2/target/idl/billions_bounty_v2.json HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`
   - Commit IDL and generated types (if used) to repo for stable clients.
4. Backend integration (staged):
   - Add new internal endpoints (v2) and guard with flag.
   - Maintain current API responses/data shapes.
5. Frontend (optional phase):
   - If calling directly, add a `NEXT_PUBLIC_USE_CONTRACT_V2` flag.
   - Prefer backend mediation initially.
6. Dry run on devnet:
   - Initialize global + bounty PDAs with test wallets.
   - Run E2E tests that cover: entry split, per-bounty tracking, price escalation, AI decision path.

## Git & Deploy Safety (DigitalOcean/Vercel)
- Create branch `feature/contract-v2-parallel`.
- CI gates:
  - Anchor build (local validator), Python tests, TypeScript tests before merge.
- DO backend (FastAPI):
  - Deploy branch to a staging environment.
  - Add env vars (flags + wallets) in staging only.
- Vercel frontend:
  - Preview deployments from branch; keep `NEXT_PUBLIC_USE_CONTRACT_V2=false` by default.
- Merge to `main` only after staging sign-off; keep v2 disabled in production until go-live.

## Test Suite Requirements (must-pass before integration)
- Anchor: unit + integration tests for all v2 instructions.
- Python: adapter tests (happy/edge cases), serialization, RPC error propagation.
- E2E: devnet flows for entry, escalation threshold, AI decision (format-verified), buyback.
- Non-regression: with `USE_CONTRACT_V2=false`, production endpoints unchanged.

## Compatibility/Risk Checklist
- Anchor CLI vs crate versions aligned (0.30 CLI acceptable with 0.28 crates for on-chain).
- Lockfile/cargo: prefer stable lockfiles; avoid nightly-only flags in CI.
- Ed25519: full on-chain verification via CPI is a future enhancement; currently verifies format + hash match. Keep backend verification authoritative until CPI is added.
- BPF stack: avoid large stack allocations; keep buffers small.
- SPL/ATA: all CPIs require correct authorities; double-check.

## Rollout Guide
1. Staging enablement: set flag true in staging only; validate flows.
2. Canary enablement (internal only) on prod: small sample via hidden flag.
3. Full switch: set `USE_CONTRACT_V2=true` in production; monitor logs/metrics.
4. Fallback: revert flag to false to return to v1.

## Post-Go-Live
- Add CPI Ed25519 verification.
- Expand price escalations and buyback automation if needed.
- Decommission v1 after observation window.

**Status**: Ready for staged integration.


