# SDK Integration Services - Parallel Development

This directory contains SDK integration services developed in parallel to the main codebase. These services are tested independently before integration into production.

## Structure

```
src/services/sdk/
├── __init__.py              # Feature flags and exports
├── kora_service.py          # Fee abstraction service
├── attestations_service.py  # Verifiable credentials (KYC replacement)
├── solana_pay_service.py    # Standardized payments (TODO)
└── commercekit_service.py  # Drop-in payment SDK (TODO)
```

## Enabled Services

Services are enabled via environment variables:

```bash
# Enable Kora fee abstraction
ENABLE_KORA_SDK=true
KORA_API_KEY=your_api_key
KORA_BASE_URL=https://api.kora.so

# Enable Attestations for KYC
ENABLE_ATTESTATIONS_SDK=true
ATTESTATIONS_PROGRAM_ID=program_id_here

# Enable Solana Pay (when implemented)
ENABLE_SOLANA_PAY_SDK=true

# Enable CommerceKit (when implemented)
ENABLE_COMMERCEKIT_SDK=true
```

## Testing Endpoints

All SDK functionality is tested via isolated endpoints at `/api/sdk-test/`:

- `/api/sdk-test/kora/*` - Kora fee abstraction testing
- `/api/sdk-test/attestations/*` - Attestations verification testing
- `/api/sdk-test/solana-pay/*` - Solana Pay protocol testing (when implemented)
- `/api/sdk-test/commercekit/*` - CommerceKit evaluation (when implemented)

## Integration Status

### Phase 1: High Priority (Structure Complete - Needs IDs & Testing)
- ✅ **Kora Service**: JSON-RPC 2.0 client implemented correctly
  - ⏳ Need to run Kora server locally or deploy
  - ⏳ Test JSON-RPC calls with actual server
- ✅ **Attestations Service**: On-chain program query implemented correctly
  - ⚠️ Need actual SAS program ID (currently placeholder)
  - ⏳ Need to parse account data structure
  - ⏳ Need schema pubkeys for KYC, geographic, etc.

### Phase 2: Medium Priority (Planned)
- ⏳ **Solana Pay Service**: Structure pending, compatibility check needed
- ⏳ **CommerceKit Service**: Evaluation pending

## Usage Examples

### Kora - Fee Abstraction

```python
from src.services.sdk.kora_service import kora_service

# Create sponsored transaction (fees paid by Kora)
result = await kora_service.create_sponsored_transaction(
    transaction=transaction_bytes,
    fee_token="USDC"
)

# Estimate fee cost in USDC
fee_estimate = await kora_service.estimate_fee_cost(
    transaction_size=512,
    fee_token="USDC"
)
```

### Attestations - KYC Verification

```python
from src.services.sdk.attestations_service import attestations_service

# Verify KYC attestation
kyc_result = await attestations_service.verify_kyc_attestation(
    wallet_address="user_wallet"
)

# Get all attestations
all_attestations = await attestations_service.get_all_attestations(
    wallet_address="user_wallet"
)
```

## Next Steps

### Immediate (Required for Testing)
1. **Kora**: 
   - Install Kora CLI: `cargo install kora-cli`
   - Run Kora server: `kora rpc` (local) or deploy to Railway
   - Test JSON-RPC endpoints

2. **Attestations**:
   - Find actual SAS program ID from official docs
   - Understand account data structure for parsing
   - Get schema pubkeys for standard schemas (KYC, geographic)

### Integration (After Testing)
3. **Kora Integration**: Replace SOL fee requirement with USDC via Kora
4. **Attestations Integration**: Replace MoonPay KYC with attestation verification
5. **Production Integration**: Merge into main codebase once validated

## Notes

- All services are disabled by default
- Test endpoints are isolated and don't affect production
- Services follow the same pattern as V2 smart contract integration (parallel development)

