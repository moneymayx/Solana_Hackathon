# SDK Testing Guide

This guide helps you test the SDK integrations once you have the required setup.

## Prerequisites

### For Attestations Testing

1. **Find SAS Program ID**:
   ```bash
   python scripts/sdk/find_attestations_program.py --network devnet
   ```

2. **Update `.env`**:
   ```bash
   ENABLE_ATTESTATIONS_SDK=true
   ATTESTATIONS_PROGRAM_ID_DEVNET=<found_program_id>
   ATTESTATIONS_PROGRAM_ID_MAINNET=<found_mainnet_id>
   SOLANA_RPC_ENDPOINT=https://api.devnet.solana.com
   ```

3. **Find a test wallet with attestation** (optional but helpful):
   - Use Solana Explorer to find wallets with attestations
   - Or create your own attestation for testing
   - Set `WALLET_WITH_ATTESTATION` environment variable

### For Kora Testing

1. **Install Kora CLI**:
   ```bash
   cargo install kora-cli
   ```

2. **Run Kora server**:
   ```bash
   kora rpc
   # Runs on http://localhost:8080 by default
   ```

3. **Update `.env`**:
   ```bash
   ENABLE_KORA_SDK=true
   KORA_RPC_URL=http://localhost:8080
   KORA_API_KEY=<if_required>
   ```

4. **Test connection**:
   ```bash
   python scripts/sdk/test_kora_setup.py --url http://localhost:8080
   ```

---

## Running Tests

### Unit Tests

```bash
# Test Attestations SDK
ENABLE_ATTESTATIONS_SDK=true pytest tests/sdk/test_attestations_integration.py -v

# Test Kora SDK
ENABLE_KORA_SDK=true KORA_RPC_URL=http://localhost:8080 pytest tests/sdk/test_kora_integration.py -v
```

### API Endpoint Tests

```bash
# Start backend
python apps/backend/main.py

# Test Attestations endpoints
curl -X POST http://localhost:8000/api/sdk-test/attestations/verify-kyc \
  -H "Content-Type: application/json" \
  -d '{"wallet_address": "your_wallet_address"}'

# Test Kora endpoints
curl http://localhost:8000/api/sdk-test/kora/config
curl http://localhost:8000/api/sdk-test/kora/supported-tokens
```

---

## Test Cases

### Attestations Test Cases

#### 1. Verify KYC Attestation
```bash
curl -X POST http://localhost:8000/api/sdk-test/attestations/verify-kyc \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "wallet_with_attestation",
    "credential_authority": "optional_credential_pubkey"
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "wallet_address": "...",
  "kyc_verified": true,
  "attestation_account": "...",
  "parsed_data": {...},
  "provider": "solana_attestations"
}
```

#### 2. Get All Attestations
```bash
curl http://localhost:8000/api/sdk-test/attestations/all/wallet_address_here
```

#### 3. Verify Geographic Attestation
```bash
curl -X POST http://localhost:8000/api/sdk-test/attestations/verify-geographic \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "wallet_address",
    "allowed_countries": ["US", "CA", "GB"]
  }'
```

### Kora Test Cases

#### 1. Get Configuration
```bash
curl http://localhost:8000/api/sdk-test/kora/config
```

**Expected Response**:
```json
{
  "success": true,
  "result": {
    "network": "devnet",
    "supported_tokens": ["USDC", "SOL"],
    ...
  }
}
```

#### 2. Get Supported Tokens
```bash
curl http://localhost:8000/api/sdk-test/kora/supported-tokens
```

#### 3. Estimate Transaction Fee
```bash
curl -X POST http://localhost:8000/api/sdk-test/kora/estimate-fee \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_base64": "base64_encoded_transaction",
    "fee_token": "USDC"
  }'
```

#### 4. Sign Transaction
```bash
curl -X POST http://localhost:8000/api/sdk-test/kora/sign-transaction \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_base64": "base64_encoded_transaction",
    "options": {}
  }'
```

---

## Troubleshooting

### Attestations Issues

**Problem**: "Invalid Attestations program ID"
- **Solution**: Find the correct SAS program ID and update `.env`

**Problem**: "No attestation found" (but you know one exists)
- **Solution**: 
  1. Verify program ID is correct
  2. Check PDA derivation matches SAS program
  3. Verify wallet address is correct
  4. Check if credential authority is required

**Problem**: "Error parsing account data"
- **Solution**: Account structure needs to be determined. Query a known attestation account and analyze its structure.

### Kora Issues

**Problem**: "Connection failed"
- **Solution**: 
  1. Ensure Kora server is running: `kora rpc`
  2. Check `KORA_RPC_URL` is correct
  3. Test connection: `python scripts/sdk/test_kora_setup.py`

**Problem**: "JSON-RPC error"
- **Solution**: 
  1. Check method names match Kora API
  2. Verify parameter format
  3. Check authentication (API key if required)

**Problem**: "Transaction encoding error"
- **Solution**: 
  1. Verify transaction is properly serialized
  2. Check if base64 encoding is correct
  3. Test with a simple transaction first

---

## Next Steps After Testing

1. **Update Account Parsing**: Once you query real attestation accounts, update `_parse_attestation_account_data` with correct structure

2. **Document API Formats**: Record actual Kora JSON-RPC request/response formats

3. **Create POCs**:
   - Kora POC: USDC fee payment flow
   - Attestations POC: KYC check before payment

4. **Integration**:
   - Add KYC check to payment endpoint
   - Add fee abstraction option to frontend
   - Test end-to-end flows

---

## Test Data

### Sample Test Wallets

For testing, you may want to:
1. Create test attestations on devnet
2. Use known wallets with attestations
3. Set up test data in `.env`:
   ```bash
   TEST_WALLET_WITH_ATTESTATION=...
   TEST_WALLET_WITHOUT_ATTESTATION=...
   ```

---

**Status**: Ready for testing once prerequisites are met

