# CI: Contract V2 IDL and Tests

## Goals
- Generate IDL for v2 post-deploy and commit artifacts
- Run Anchor tests on local validator
- Run Python adapter tests

## Suggested Steps
1. Setup job matrix with cached Rust/Node/Python
2. Anchor build + test:
   - `anchor --version`
   - `anchor build --program-name billions_bounty_v2`
   - `anchor test`
3. Python tests:
   - `pip install -r requirements.txt`
   - `pytest tests/integration/test_contract_v2_adapter.py -q`
4. IDL generation:
   - `anchor idl fetch --provider.cluster devnet 4ChHkYCu5Q8KpBh1pPEx5KgKTQGySikhvzhi3KYrUMuW > programs/billions-bounty-v2/target/idl/billions_bounty_v2.json`
   - Commit the IDL file on success

## Notes
- Keep `USE_CONTRACT_V2=false` in production until staging sign-off
- Prefer stable toolchains in CI (avoid nightly flags)
