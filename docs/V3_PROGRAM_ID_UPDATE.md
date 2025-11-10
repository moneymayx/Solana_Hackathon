# V3 Program ID Update Required

## Change Summary

The V3 program was closed and redeployed with a **new program ID** because:
1. Old program data account was too small (313KB)
2. Upgrade failed due to size limit
3. Closed program IDs cannot be reused
4. New deployment required fresh program ID

## New Program ID

**Old Program ID**: `ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb` (closed)  
**New Program ID**: `$(solana-keygen pubkey target/deploy/billions_bounty_v3-keypair.json)` ✅

## Files Updated

✅ **Already Updated**:
- `programs/billions-bounty-v3/src/lib.rs` - `declare_id!` updated
- Binary rebuilt with new program ID

## Files That Need Updating

⚠️ **Must Update**:
1. `Anchor.toml` - All network program IDs:
   ```toml
   [programs.devnet]
   billions_bounty_v3 = "<NEW_PROGRAM_ID>"
   
   [programs.mainnet]
   billions_bounty_v3 = "<NEW_PROGRAM_ID>"
   
   [programs.localnet]
   billions_bounty_v3 = "<NEW_PROGRAM_ID>"
   ```

2. `programs/billions-bounty-v3/Anchor.toml`:
   ```toml
   [programs.devnet]
   billions_bounty_v3 = "<NEW_PROGRAM_ID>"
   ```

3. Environment Variables:
   - `LOTTERY_PROGRAM_ID_V3=<NEW_PROGRAM_ID>`
   - `NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V3=<NEW_PROGRAM_ID>`

4. Frontend Configuration Files
5. Backend Configuration Files
6. Documentation References

## Next Steps

1. ✅ Deploy new program (done)
2. ⏳ Update all configuration files with new program ID
3. ⏳ Initialize lottery account with new program ID
4. ⏳ Update integrations to use new program ID

