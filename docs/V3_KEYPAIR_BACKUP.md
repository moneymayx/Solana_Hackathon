# V3 Keypair Backup Information

## ⚠️ CRITICAL: Backup This Keypair!

The V3 program keypair has been generated and saved. **This must be backed up securely.**

## Keypair Details

**Program ID**: `52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov`

**Keypair Location**: `target/deploy/billions_bounty_v3-keypair.json`

## Recovery Seed Phrase

```
average rebel skirt aim alcohol cross leopard phrase cause twin lesson dignity
```

**⚠️ WARNING**: Store this seed phrase securely! It can be used to recover the keypair.

## Recovery Command

To recover the keypair from seed phrase:
```bash
solana-keygen recover 'prompt://' -o target/deploy/billions_bounty_v3-keypair.json
# Then enter the seed phrase when prompted
```

## What This Keypair Controls

- **Program Upgrades**: Required to upgrade the V3 program
- **Program Authority**: Control over program deployment and management
- **Program Lifecycle**: Cannot be recovered if lost!

## Backup Locations

1. ✅ **Primary**: `target/deploy/billions_bounty_v3-keypair.json`
2. ✅ **ID saved to**: `target/deploy/v3_new_program_id.txt`
3. ✅ **Info saved to**: `target/deploy/V3_KEYPAIR_INFO.txt`

## Next Steps

1. **Backup keypair file** to secure location (encrypted storage recommended)
2. **Save seed phrase** to password manager or secure vault
3. **Test recovery** using seed phrase to verify backup works
4. **Never commit** keypair files to Git!

## Old Program ID (Closed)

**Old Program ID**: `ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb` (CLOSED - cannot be reused)

The old program was closed because:
- Program data account too small for upgrade (313KB → 490KB)
- Required fresh deployment with new program ID

