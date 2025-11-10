# SDK Backend Testing Guide

## ✅ Integration Verified

Your SDK integrations are **working with your backend**! Here's how to test them:

---

## Quick Test (Service Layer)

Test services directly (no backend needed):

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate
python scripts/sdk/test_backend_integration.py
```

**Expected Results**:
- ✅ Kora Service: Working
- ✅ Attestations Service: Working  
- ✅ Backend Integration: 11 routes registered

---

## Full Test (With HTTP Endpoints)

### Step 1: Start Backend

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate
python apps/backend/main.py
```

Look for these log messages:
```
✅ Kora SDK test router registered
✅ Attestations SDK test router registered
✅ SDK test routers registered: 2
```

### Step 2: Test Endpoints

In another terminal:

#### Kora Endpoints

```bash
# Check status
curl http://localhost:8000/api/sdk-test/kora/status

# Get configuration
curl http://localhost:8000/api/sdk-test/kora/config

# Get supported tokens
curl http://localhost:8000/api/sdk-test/kora/supported-tokens
```

#### Attestations Endpoints

```bash
# Check status
curl http://localhost:8000/api/sdk-test/attestations/status

# Verify KYC
curl -X POST http://localhost:8000/api/sdk-test/attestations/verify-kyc \
  -H "Content-Type: application/json" \
  -d '{"wallet_address": "11111111111111111111111111111111"}'

# Get all attestations
curl http://localhost:8000/api/sdk-test/attestations/all/11111111111111111111111111111111
```

### Step 3: Use Test Script

```bash
# Automatically tests all endpoints
./scripts/sdk/test_sdk_endpoints.sh

# Or with custom URL
./scripts/sdk/test_sdk_endpoints.sh http://localhost:8000
```

---

## Expected Responses

### Kora Status
```json
{
  "enabled": true,
  "cli_path": "kora-cli",
  "rpc_url": "http://127.0.0.1:8899",
  "private_key_configured": true
}
```

### Attestations Status
```json
{
  "enabled": true,
  "program_id": "22zoJMtdu4tQc2PzL74ZUT7FrwgB1Udec8DdW4yw4BdG",
  "rpc_endpoint": "https://api.devnet.solana.com"
}
```

### Attestations Verify KYC
```json
{
  "success": true,
  "wallet_address": "...",
  "kyc_verified": false,
  "message": "No KYC attestation found for this wallet"
}
```

---

## Integration Points in Your Code

### Backend (Python)

The SDK services are already integrated. You can use them in your endpoints:

```python
from src.services.sdk.kora_service import kora_service
from src.services.sdk.attestations_service import attestations_service

# Use in payment endpoint
if kora_service.is_enabled():
    # Use fee abstraction
    result = await kora_service.sign_transaction(transaction_base64)

# Use in KYC check
if attestations_service.is_enabled():
    kyc_result = await attestations_service.verify_kyc_attestation(wallet)
```

### Frontend (TypeScript/React)

Call the backend API endpoints:

```typescript
// Check KYC before payment
const kycCheck = await fetch('/api/sdk-test/attestations/verify-kyc', {
  method: 'POST',
  body: JSON.stringify({ wallet_address: wallet.publicKey.toString() })
});

// Use Kora for fee abstraction
const koraResult = await fetch('/api/sdk-test/kora/sign-and-send', {
  method: 'POST',
  body: JSON.stringify({ transaction_base64: txBase64 })
});
```

---

## Troubleshooting

### Endpoints Return 404
- ✅ Check backend is running
- ✅ Check routes are registered (should see log messages)
- ✅ Check SDK is enabled in `.env`

### Services Not Enabled
- ✅ Check `ENABLE_KORA_SDK=true` in `.env`
- ✅ Check `ENABLE_ATTESTATIONS_SDK=true` in `.env`
- ✅ Restart backend after changing `.env`

### Kora Errors
- ✅ Check `KORA_PRIVATE_KEY` is set
- ✅ Check wallet is funded
- ✅ Check `kora-cli` is installed

### Attestations Errors
- ✅ Check `ATTESTATIONS_PROGRAM_ID_DEVNET` is set
- ✅ Check program ID is correct
- ✅ Check RPC endpoint is accessible

---

**Status**: ✅ All integrations verified and ready!

