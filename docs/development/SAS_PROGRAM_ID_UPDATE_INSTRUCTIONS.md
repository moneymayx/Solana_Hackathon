# Add SAS Program ID to .env

## ✅ Program ID Found

**SAS Program ID**: `22zoJMtdu4tQc2PzL74ZUT7FrwgB1Udec8DdW4yw4BdG`

## 📝 Add to .env File

Open your `.env` file and add these lines:

```bash
# Attestations SDK Configuration
ENABLE_ATTESTATIONS_SDK=true
ATTESTATIONS_PROGRAM_ID_DEVNET=22zoJMtdu4tQc2PzL74ZUT7FrwgB1Udec8DdW4yw4BdG
```

## ⚠️ Mainnet Program ID

The program ID you found might be for devnet. To get the mainnet program ID:

1. Visit: https://explorer.solana.com/?cluster=mainnet-beta
2. Search for: `Solana Attestation Service Program`
3. Copy the mainnet program ID
4. Add to `.env`:
```bash
ATTESTATIONS_PROGRAM_ID_MAINNET=<mainnet_program_id>
```

(If same on both networks, use the same ID for both)

## ✅ Verify Configuration

After adding to `.env`, test:

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate

python3 -c "
from src.services.sdk.attestations_service import AttestationsService
service = AttestationsService()
print(f'Program ID: {service.program_id}')
print(f'Expected: 22zoJMtdu4tQc2PzL74ZUT7FrwgB1Udec8DdW4yw4BdG')
print('Match!' if str(service.program_id) == '22zoJMtdu4tQc2PzL74ZUT7FrwgB1Udec8DdW4yw4BdG' else 'Mismatch')
"
```

---

**Once configured, Attestations SDK will be fully functional!** 🎉

