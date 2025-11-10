# SAS Program ID - Found! ✅

## Program ID Information

**From Solana Explorer:**
- **Program ID**: `22zoJMtdu4tQc2PzL74ZUT7FrwgB1Udec8DdW4yw4BdG`
- **Label**: Solana Attestation Service Program
- **Network**: This appears to be the program ID
- **Status**: Valid Solana program address

## Configuration

### For Devnet

Add to your `.env` file:
```bash
ATTESTATIONS_PROGRAM_ID_DEVNET=22zoJMtdu4tQc2PzL74ZUT7FrwgB1Udec8DdW4yw4BdG
```

### For Mainnet

⚠️ **Important**: The program ID may be different on mainnet.

To find the mainnet program ID:
1. Visit: https://explorer.solana.com/?cluster=mainnet-beta
2. Search for the same program
3. Copy the mainnet program ID
4. Add to `.env`:
```bash
ATTESTATIONS_PROGRAM_ID_MAINNET=<mainnet_program_id>
```

## Enable Attestations SDK

Also add to `.env`:
```bash
ENABLE_ATTESTATIONS_SDK=true
```

## Test After Configuration

Once added to `.env`, test it:

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate

# Test service initialization
python3 -c "
from src.services.sdk.attestations_service import AttestationsService
service = AttestationsService()
print(f'Program ID: {service.program_id}')
print(f'Enabled: {service.is_enabled()}')
"

# Run example
python examples/sdk/attestations_kyc_example.py
```

## What This Enables

With the program ID configured, you can now:
- ✅ Query attestation accounts on-chain
- ✅ Verify KYC attestations
- ✅ Check geographic restrictions
- ✅ Verify accreditation status
- ✅ Get all attestations for a wallet

## Next Steps

1. ✅ **Program ID Found** - `22zoJMtdu4tQc2PzL74ZUT7FrwgB1Udec8DdW4yw4BdG`
2. ⏳ **Update .env** - Add the program ID
3. ⏳ **Test Service** - Verify it can query attestations
4. ⏳ **Find Mainnet ID** - Check if different on mainnet
5. ⏳ **Test with Real Accounts** - Query known attestation accounts

---

**Status**: Program ID discovered! Ready to configure and test.

