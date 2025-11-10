# SDK Integration Examples

This directory contains example code showing how to integrate the SDK services into your application.

## Examples

### Kora Fee Abstraction
**File**: `kora_fee_abstraction_example.py`

Shows how to:
- Connect to Kora server
- Estimate fees in USDC
- Sign transactions with fee abstraction
- Integrate into payment flow

**Prerequisites**:
- Kora server running (`kora rpc`)
- `ENABLE_KORA_SDK=true` in `.env`

**Usage**:
```bash
python examples/sdk/kora_fee_abstraction_example.py
```

### Attestations KYC Verification
**File**: `attestations_kyc_example.py`

Shows how to:
- Verify KYC attestations before payments
- Check geographic restrictions
- Get all attestations for a wallet
- Integrate into payment flow

**Prerequisites**:
- SAS program ID configured
- `ENABLE_ATTESTATIONS_SDK=true` in `.env`

**Usage**:
```bash
python examples/sdk/attestations_kyc_example.py
```

## Integration Patterns

### Payment Flow with KYC Check

```python
# 1. Verify KYC before payment
kyc_result = await attestations_service.verify_kyc_attestation(user_wallet)

if not kyc_result.get("kyc_verified"):
    return {"error": "KYC required"}

# 2. Build payment transaction
transaction = build_v2_payment_transaction(...)

# 3. Optionally use Kora for fee abstraction
if use_fee_abstraction:
    signed = await kora_service.sign_transaction(transaction_base64)
else:
    signed = await user_wallet.sign_transaction(transaction)

# 4. Send transaction
await send_transaction(signed)
```

### Fee Abstraction Option

```python
# Estimate fees in different tokens
fee_usdc = await kora_service.estimate_transaction_fee(
    transaction_base64,
    fee_token="USDC"
)

# Show user options
if user_has_sol:
    # Pay with SOL (standard)
    process_payment(user_signs=True)
else:
    # Pay fees with USDC via Kora
    signed = await kora_service.sign_transaction(transaction_base64)
    process_payment(transaction=signed)
```

## Next Steps

1. **Run examples** to see how services work
2. **Adapt patterns** to your specific use case
3. **Test integrations** with your payment flows
4. **Create POCs** based on these examples

---

**Note**: Examples use placeholder data. Replace with actual transactions and wallets for real testing.

