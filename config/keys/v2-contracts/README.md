# V2 Contract Keypairs

This directory contains keypairs for the Phase 1-2 smart contract implementations.

## Keypairs

### billions_bounty_v2-keypair.json
- **Program ID**: `4ChHkYCu5Q8KpBh1pPEx5KgKTQGySikhvzhi3KYrUMuW`
- **Purpose**: Main v2 contract program (Phase 1-2 features)
- **Created**: October 2025
- **Location**: `programs/billions-bounty-v2/target/deploy/billions_bounty_v2-keypair.json`
- **Backup**: This directory (`config/keys/v2-contracts/billions_bounty_v2-keypair.json`)

## Important Notes

⚠️ **SECURITY WARNING**: 
- These keypairs contain private keys
- Never commit these files to version control
- Keep backups in secure locations
- Use different keypairs for devnet vs mainnet deployments

## Usage

To use this keypair for deployment:
```bash
# Deploy to devnet
cd programs/billions-bounty-v2
anchor deploy --provider.cluster devnet --provider.wallet config/keys/v2-contracts/billions_bounty_v2-keypair.json

# Or set as default wallet
solana config set --keypair config/keys/v2-contracts/billions_bounty_v2-keypair.json
```

## Recovery

If you need to recover the keypair:
- Seed phrase was displayed when keypair was generated
- Store seed phrase securely (not in this repository)

## Related Files

- Contract source: `programs/billions-bounty-v2/src/lib.rs`
- Anchor config: `programs/billions-bounty-v2/Anchor.toml`
- Documentation: `docs/development/CONTRACT_V2_README.md`

