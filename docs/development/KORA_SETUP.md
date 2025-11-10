# Kora Private Key Setup

## What is KORA_PRIVATE_KEY?

The `KORA_PRIVATE_KEY` is a **Solana keypair** (private key in base58 format) that Kora uses to:
- Sign transactions on behalf of users
- Pay transaction fees in USDC (or other configured tokens) instead of requiring users to have SOL
- Act as the "fee payer" for transactions

## Important Notes

⚠️ **Security Considerations**:
- This keypair will hold funds (USDC, SOL) that are used to pay fees
- **Never commit this key to Git or share it publicly**
- Keep it secure and backed up
- Consider using a dedicated wallet for Kora fee payments

## Setup Steps

### Option 1: Generate a New Keypair (Recommended for Devnet)

For development/testing, you can generate a new keypair:

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
python3 -c "
from solders.keypair import Keypair
import base58

keypair = Keypair()
private_key_base58 = base58.b58encode(bytes(keypair)).decode('utf-8')
print('KORA_PRIVATE_KEY=' + private_key_base58)
print('Public Key: ' + str(keypair.pubkey()))
"
```

Then add the output to your `.env` file:
```
KORA_PRIVATE_KEY=<generated_private_key>
```

### Option 2: Use an Existing Wallet

If you have an existing Solana wallet/keypair, you can convert it to base58 format:

```bash
# If you have a keypair file (JSON format):
python3 -c "
import json
import base58

with open('path/to/your/keypair.json', 'r') as f:
    keypair_bytes = bytes(json.load(f))
    private_key_base58 = base58.b58encode(keypair_bytes).decode('utf-8')
    print('KORA_PRIVATE_KEY=' + private_key_base58)
"
```

### Option 3: Use Solana CLI (if installed)

```bash
# Generate new keypair
solana-keygen new -o kora-keypair.json --force

# Convert to base58
python3 -c "
import json
import base58
with open('kora-keypair.json', 'r') as f:
    keypair_bytes = bytes(json.load(f))
    print(base58.b58encode(keypair_bytes).decode('utf-8'))
"
```

## Funding the Kora Wallet

Once you have the keypair, you need to fund it:

1. **Get the public key**:
   ```bash
   python3 -c "
   import base58
   from solders.keypair import Keypair
   
   # Replace with your private key
   private_key = 'YOUR_PRIVATE_KEY_HERE'
   keypair = Keypair.from_base58_string(private_key)
   print('Public Key:', str(keypair.pubkey()))
   print('Fund this address with USDC (or SOL) for fee payments')
   "
   ```

2. **Fund the wallet**:
   - For **devnet**: Use Solana faucet to get SOL
   - For **mainnet**: Send USDC or SOL to the public key address
   - Amount depends on usage (start with small amounts for testing)

## Configuration in .env

Add these to your `.env` file:

```bash
# Enable Kora SDK
ENABLE_KORA_SDK=true

# Kora private key (base58 encoded)
KORA_PRIVATE_KEY=<your_private_key_here>

# Solana RPC endpoint (default: http://127.0.0.1:8899)
KORA_RPC_URL=https://api.devnet.solana.com

# Optional: Path to kora.toml config file
# KORA_CONFIG=kora.toml
```

## Verify Setup

Test that Kora is configured correctly:

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate
python examples/sdk/kora_fee_abstraction_example.py
```

You should see:
- ✅ Kora SDK enabled
- ✅ Configuration loaded
- (May show warnings if wallet not funded or CLI issues)

## Next Steps

1. ✅ Generate keypair (see commands above)
2. ✅ Add to `.env` as `KORA_PRIVATE_KEY`
3. ⏳ Fund the wallet with USDC/SOL for fee payments
4. ⏳ Configure `kora.toml` if needed (for fee token settings)
5. ⏳ Test with actual transactions

---

**Note**: For production, consider using a hardware wallet or secure key management system instead of storing the private key directly in `.env`.

