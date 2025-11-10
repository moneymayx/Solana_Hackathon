# SDK Integration Setup Guide

This document describes how to set up and test the new Solana SDK integrations in parallel to the main codebase.

## Overview

SDK services are being developed in parallel (similar to V2 smart contract integration) to test functionality before merging into production. All SDK work is:

- **Backend only** (initially)
- **Isolated** via `/api/sdk-test/` endpoints
- **Feature-flagged** via environment variables
- **Local development** (no git push during hackathon)

## Directory Structure

```
Billions_Bounty/
├── src/services/sdk/          # SDK service implementations
│   ├── kora_service.py
│   ├── attestations_service.py
│   ├── solana_pay_service.py
│   └── commercekit_service.py
├── src/api/sdk/               # SDK test API endpoints
│   ├── kora_router.py
│   ├── attestations_router.py
│   └── app_integration.py
└── tests/sdk/                 # SDK integration tests
    ├── test_kora.py
    └── test_attestations.py
```

## Environment Variables

Add these to your `.env` file to enable SDK features:

```bash
# Kora SDK - Fee Abstraction (JSON-RPC 2.0 Server)
ENABLE_KORA_SDK=true
KORA_RPC_URL=http://localhost:8080  # Kora JSON-RPC server endpoint
KORA_API_KEY=optional_api_key_here  # Optional authentication
# Note: You need to run a Kora server locally or deploy one
# Install: cargo install kora-cli
# Run: kora rpc [OPTIONS]

# Attestations SDK - KYC Replacement (On-Chain Program)
ENABLE_ATTESTATIONS_SDK=true
ATTESTATIONS_PROGRAM_ID=SAS_program_id_here  # Solana Attestations Service program ID
# Note: Attestations is an on-chain program, queries via RPC
# Library: sas-lib (JS/TS) - We query program directly in Python

# Solana Pay SDK (when ready)
ENABLE_SOLANA_PAY_SDK=false

# CommerceKit SDK (when ready)
ENABLE_COMMERCEKIT_SDK=false
```

## Testing Endpoints

Once enabled, SDK test endpoints are available at:

### Kora Endpoints (JSON-RPC based)
- `GET /api/sdk-test/kora/status` - Check if Kora is enabled and configured
- `GET /api/sdk-test/kora/config` - Get Kora server configuration
- `POST /api/sdk-test/kora/sign-transaction` - Sign transaction (fee abstraction)
- `POST /api/sdk-test/kora/sign-and-send` - Sign and send transaction
- `POST /api/sdk-test/kora/estimate-fee` - Estimate fee cost in token
- `GET /api/sdk-test/kora/supported-tokens` - List supported fee tokens

### Attestations Endpoints (On-Chain Program)
- `GET /api/sdk-test/attestations/status` - Check if Attestations is enabled
- `POST /api/sdk-test/attestations/verify-kyc` - Verify KYC attestation
- `POST /api/sdk-test/attestations/verify-geographic` - Verify geographic attestation
- `POST /api/sdk-test/attestations/verify-accreditation` - Verify accreditation
- `GET /api/sdk-test/attestations/all/{wallet_address}` - Get all attestations

### Solana Pay Endpoints
- `GET /api/sdk-test/solana-pay/status` - Check if Solana Pay is enabled
- `POST /api/sdk-test/solana-pay/create-transfer-request` - Create transfer request URL
- `POST /api/sdk-test/solana-pay/verify-payment` - Verify payment transaction
- `GET /api/sdk-test/solana-pay/v2-compatibility` - Check V2 contract compatibility

### CommerceKit Endpoints (Evaluation Only)
- `GET /api/sdk-test/commercekit/status` - Check if CommerceKit evaluation is enabled
- `POST /api/sdk-test/commercekit/evaluate-compatibility` - Evaluate V2 contract compatibility
- `GET /api/sdk-test/commercekit/recommendation` - Get integration recommendation

## Testing

### 1. Start Backend Server

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate  # Activate virtual environment
cd apps/backend
uvicorn main:app --reload --port 8000
```

### 2. Check SDK Status

```bash
# Check Kora status
curl http://localhost:8000/api/sdk-test/kora/status

# Check Attestations status
curl http://localhost:8000/api/sdk-test/attestations/status
```

### 3. Test Kora Fee Abstraction

**Prerequisites**: You need a Kora server running (see setup below)

```bash
# Check Kora status
curl http://localhost:8000/api/sdk-test/kora/status

# Get Kora server config
curl http://localhost:8000/api/sdk-test/kora/config

# Get supported tokens
curl http://localhost:8000/api/sdk-test/kora/supported-tokens

# Estimate fee (requires base64-encoded transaction)
curl -X POST http://localhost:8000/api/sdk-test/kora/estimate-fee \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_base64": "base64_transaction_here",
    "fee_token": "USDC"
  }'
```

**Setting up Kora Server:**

1. Install Kora CLI:
   ```bash
   cargo install kora-cli
   ```

2. Run Kora server locally:
   ```bash
   kora rpc --help  # See options
   kora rpc  # Runs on http://localhost:8080 by default
   ```

3. Or deploy to Railway/Docker (see Kora docs)

### 4. Test Attestations KYC

```bash
# Verify KYC attestation
curl -X POST http://localhost:8000/api/sdk-test/attestations/verify-kyc \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "your_wallet_address_here"
  }'

# Get all attestations for a wallet
curl http://localhost:8000/api/sdk-test/attestations/all/your_wallet_address_here
```

### 5. Test Solana Pay Transfer Requests

```bash
# Create a transfer request URL
curl -X POST http://localhost:8000/api/sdk-test/solana-pay/create-transfer-request \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "recipient_wallet_address",
    "amount": 0.01,
    "label": "Coffee Shop",
    "message": "Grande Latte"
  }'

# Check V2 compatibility
curl http://localhost:8000/api/sdk-test/solana-pay/v2-compatibility
```

### 6. Evaluate CommerceKit Compatibility

```bash
# Get compatibility assessment
curl -X POST http://localhost:8000/api/sdk-test/commercekit/evaluate-compatibility \
  -H "Content-Type: application/json" \
  -d '{}'

# Get integration recommendation
curl http://localhost:8000/api/sdk-test/commercekit/recommendation
```

## Development Workflow

1. **Enable SDK**: Set environment variable for the SDK you want to test
2. **Develop**: Make changes to SDK services in `src/services/sdk/`
3. **Test**: Use test endpoints at `/api/sdk-test/` to validate functionality
4. **Integrate**: Once validated, integrate into production services
5. **Merge**: After hackathon, merge SDK services into main codebase

## Current Implementation Status

### ✅ Completed
- [x] SDK directory structure
- [x] Kora service skeleton
- [x] Attestations service skeleton
- [x] Test API routers
- [x] Integration into main.py
- [x] Basic tests

### 🔄 In Progress
- [ ] Kora API integration (actual API calls)
- [ ] Attestations on-chain verification (RPC queries)
- [ ] Solana Pay compatibility check
- [ ] CommerceKit evaluation

### ⏳ Planned
- [ ] Production integration (when SDKs validated)
- [ ] Frontend integration (after backend validation)
- [ ] Documentation updates

## Next Steps

1. **Get API Keys**: Obtain Kora API key and Attestations program ID
2. **Implement API Calls**: Complete actual API integrations in service classes
3. **Test End-to-End**: Validate full payment flow with Kora fee abstraction
4. **Test KYC**: Validate Attestations can replace MoonPay KYC
5. **Evaluate Others**: Assess Solana Pay and CommerceKit compatibility

## Notes

- All SDK endpoints are **isolated** from production code
- Services are **disabled by default** (must enable via env vars)
- No modifications to existing payment flows until validated
- Follows same pattern as V2 smart contract parallel development

## Troubleshooting

### SDK endpoints not available
- Check that environment variables are set correctly
- Verify router is included in main.py (should be automatic)
- Check logs for SDK router registration messages

### API calls failing
- Verify API keys are correct
- Check network connectivity
- Review service logs for detailed error messages

### Services disabled
- Check `ENABLE_*_SDK=true` in environment variables
- Verify service initialization in service class constructors

