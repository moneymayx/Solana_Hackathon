# SDK Implementation Status

This document tracks the current implementation status and what still needs to be done for each SDK.

## Overview

Both SDKs have been corrected based on official documentation:
- **Kora**: Now correctly implemented as JSON-RPC 2.0 server client
- **Attestations**: Now correctly implemented as on-chain program query service

---

## ✅ Kora SDK - Fee Abstraction

### Status: **Structure Complete - Needs Testing**

### What's Done
- ✅ JSON-RPC 2.0 client implementation
- ✅ Methods: `signTransaction`, `signAndSendTransaction`, `estimateTransactionFee`
- ✅ Service class with proper error handling
- ✅ Test API endpoints at `/api/sdk-test/kora/*`
- ✅ Integration into main.py

### What's Needed
- ⏳ **Run Kora Server**: Need to install and run `kora rpc` locally or deploy to Railway
- ⏳ **Test Integration**: Verify JSON-RPC calls work with actual Kora server
- ⏳ **Get API Keys**: If authentication is required
- ⏳ **Parse Responses**: Handle actual response formats from Kora server

### Next Steps
1. Install Kora CLI: `cargo install kora-cli`
2. Run Kora server: `kora rpc` (or deploy)
3. Test endpoints: Verify fee abstraction works
4. Integrate into payment flow: Replace SOL fee requirement with USDC

**Documentation**: https://launch.solana.com/docs/kora

---

## ✅ Attestations SDK - KYC Replacement

### Status: **Structure Complete - Needs Program ID & Data Parsing**

### Architecture: On-Chain Program (SAS)

### What's Done
- ✅ On-chain program query implementation
- ✅ PDA derivation for attestation accounts
- ✅ RPC calls to query attestation accounts
- ✅ Methods: `verify_kyc_attestation`, `verify_geographic_attestation`, `get_attestations_by_schema`
- ✅ Service class with proper error handling
- ✅ Test API endpoints at `/api/sdk-test/attestations/*`

### What's Needed
- ⚠️ **Get SAS Program ID**: Need actual Solana Attestations Service program ID (currently placeholder)
- ⏳ **Understand Account Structure**: Need to parse account data to extract KYC/geographic info
- ⏳ **Get Schema IDs**: Need schema pubkeys for KYC, geographic, accreditation schemas
- ⏳ **Test with Real Attestations**: Verify with wallets that have actual attestations
- ⏳ **Parse Account Data**: Implement parsing of base64 account data into structured format

### Next Steps
1. **Find SAS Program ID**: 
   - Check official Solana Attestations documentation
   - May be different for devnet vs mainnet
   - Update `ATTESTATIONS_PROGRAM_ID` in `.env`

2. **Understand Account Layout**:
   - Review SAS account structure documentation
   - Implement deserialization of account data
   - Extract KYC fields, country codes, etc.

3. **Get Schema Pubkeys**:
   - Identify standard KYC schema
   - Identify geographic schema
   - Update service to use correct schemas

4. **Test Integration**:
   - Query wallets with known attestations
   - Verify parsing works correctly
   - Replace MoonPay KYC with attestation checks

**Documentation**: https://launch.solana.com/docs/attestations
**Library Reference**: `sas-lib` (JS/TS) - We're implementing Python equivalent

---

## ✅ Solana Pay SDK - Standardized Payments

### Status: **Implementation Complete - Not Compatible with V2 Contract**

### What's Done
- ✅ Transfer request URL implementation following official spec
- ✅ Proper URL encoding and parameter handling
- ✅ V2 compatibility assessment
- ✅ Test endpoints created

### Assessment
- ✅ **Compatible**: Simple transfer payments
- ❌ **Not Compatible**: V2 contract requires custom instructions with PDAs
- **Recommendation**: Use Solana Pay for simple payment flows, keep custom instructions for V2 contract

### Implementation Details
- Follows official spec: `solana:<recipient>?amount=<amount>&label=<label>&message=<message>&spl-token=<mint>`
- Reference: https://launch.solana.com/docs/solana-pay

---

## ✅ CommerceKit SDK - Drop-in Payments

### Status: **Evaluation Complete - NOT Recommended**

### What's Done
- ✅ Detailed compatibility evaluation
- ✅ Assessment of V2 contract requirements vs CommerceKit capabilities
- ✅ Integration recommendation provided

### Assessment Result
- ❌ **NOT COMPATIBLE** with V2 contract requirements
- **Key Issues**:
  - CommerceKit is a **FRONTEND SDK** (JavaScript/TypeScript)
  - Cannot handle custom program instructions
  - Cannot support multi-recipient splits (4-way)
  - No PDA account handling
- **Recommendation**: DO NOT INTEGRATE for V2 contract payments
- **Alternative**: Keep custom payment implementation; CommerceKit could be used for other simple payment types

### Implementation Details
- Evaluation service created for backend assessment
- CommerceKit would need frontend integration (not backend)
- Documentation: https://launch.solana.com/docs/commerce-kit

---

## Critical TODOs

### High Priority
1. **Get Kora Server Running**: Required to test fee abstraction
   - Install: `cargo install kora-cli`
   - Run: `kora rpc` (local) or deploy to Railway
2. **Find SAS Program ID**: Required for attestations to work
   - Get actual Solana Attestations Service program ID
   - May differ for devnet vs mainnet
   - Update `ATTESTATIONS_PROGRAM_ID` environment variable
3. **Understand SAS Account Structure**: Required to parse attestation data
   - Review SAS account layout documentation
   - Implement deserialization of account data
   - Extract KYC fields, country codes, etc.

### Medium Priority
4. **Test Kora Integration**: Verify fee abstraction works end-to-end
   - Test JSON-RPC calls with running Kora server
   - Verify USDC fee payment works
5. **Implement Account Data Parsing**: Extract KYC/geographic info from attestations
   - Parse base64 account data
   - Extract structured attestation information
6. **Get Schema Pubkeys**: Identify standard schemas for KYC, geographic checks
   - Find standard KYC schema pubkey
   - Find geographic schema pubkey

### Completed ✅
7. ✅ **Solana Pay Implementation**: Transfer request URL complete
8. ✅ **CommerceKit Evaluation**: Assessment complete - NOT recommended for V2 contract

---

## Environment Variables Needed

```bash
# Kora (JSON-RPC Server)
ENABLE_KORA_SDK=true
KORA_RPC_URL=http://localhost:8080  # Or deployed Kora server URL
KORA_API_KEY=optional_if_required

# Attestations (On-Chain Program)
ENABLE_ATTESTATIONS_SDK=true
ATTESTATIONS_PROGRAM_ID=SAS_program_id_here  # ⚠️ NEEDS TO BE FOUND
SOLANA_RPC_ENDPOINT=https://api.devnet.solana.com
```

---

## Notes

- **Kora**: Must run server separately - not a hosted service
- **Attestations**: No Python SDK available - we query program directly
- **Both**: Correct architecture now, need real IDs and testing
- **Integration**: Both ready for testing once prerequisites are met

---

**Last Updated**: After fixing both SDKs based on official documentation

