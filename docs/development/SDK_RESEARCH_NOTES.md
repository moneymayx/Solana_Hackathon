# SDK Research Notes - Implementation Details

This document tracks research findings and implementation details needed for each SDK.

## 🔍 Research Tasks Status

### ✅ Kora SDK Research

**Status**: Basic structure done, needs specific API details

**Findings**:
- Architecture: JSON-RPC 2.0 server (self-hosted)
- Installation: `cargo install kora-cli`
- Methods needed: `signTransaction`, `signAndSendTransaction`, `estimateTransactionFee`
- Documentation: https://launch.solana.com/docs/kora

**What Still Needs Research**:
- ⏳ Exact JSON-RPC method parameter formats
- ⏳ Transaction encoding format (base64 vs other)
- ⏳ Fee token configuration options
- ⏳ Authentication method details (API key vs HMAC)
- ⏳ Response format structures
- ⏳ Error code meanings
- ⏳ Configuration options for Kora server

**Action Items**:
1. Review Kora GitHub repository for examples
2. Test actual JSON-RPC calls with running server
3. Document exact request/response formats
4. Implement proper transaction encoding

---

### ✅ Attestations SDK Research

**Status**: Structure done, needs program ID and account structure

**Findings**:
- Architecture: On-chain Solana program (SAS)
- Uses PDAs to store attestations
- Structure: Credentials → Schemas → Attestations
- Library: `sas-lib` (JavaScript/TypeScript) - no Python SDK
- Documentation: https://launch.solana.com/docs/attestations

**What Still Needs Research**:
- ⚠️ **CRITICAL**: Actual SAS program ID (devnet and mainnet)
  - Current placeholder: `SASProgram111111111111111111111111111111`
  - Need to find official program address
- ⏳ PDA seed structure for attestation accounts
  - Current assumption: `[b"attestation", wallet, credential?, schema?]`
  - Need to verify actual seed structure from docs
- ⏳ Account data structure (deserialization)
  - How to parse base64 account data
  - What fields contain KYC information
  - What fields contain geographic data
- ⏳ Schema pubkeys for standard schemas
  - KYC schema address
  - Geographic schema address
  - Accreditation schema address
- ⏳ Credential authority pubkeys
  - Which credentials are trusted for KYC?
  - How to find credential authorities

**Action Items**:
1. **Find SAS Program ID** - Check official GitHub or documentation
2. **Understand Account Layout** - Review SAS program account structure
3. **Get Schema Examples** - Find standard schema pubkeys
4. **Implement Account Parsing** - Deserialize attestation data

**Research Sources**:
- Official docs: https://launch.solana.com/docs/attestations
- GitHub: https://github.com/solana-foundation/attestations (if exists)
- Program explorer: Search for "attestations" or "SAS" on Solana Explorer

---

### ✅ Solana Pay Research

**Status**: Transfer request URL implemented, compatibility assessed

**Findings**:
- Format: `solana:<recipient>?amount=<amount>&label=<label>&message=<message>&spl-token=<mint>`
- Supports: Transfer requests (simple) and Transaction requests (interactive)
- Documentation: https://launch.solana.com/docs/solana-pay
- Specification: https://docs.solanapay.com

**Compatibility Assessment**:
- ✅ Transfer Requests: Simple payments (compatible but not for V2 contract)
- ❌ Transaction Requests: May support custom instructions but need verification
- ❌ V2 Contract: Requires custom instruction with PDAs (not compatible)

**What Still Needs Research**:
- ⏳ Transaction Request specification details
  - Can Transaction Requests include custom program instructions?
  - Can they handle multiple recipients?
  - Can they include PDA accounts?
- ⏳ Hybrid approach feasibility
  - Use Solana Pay URL format but build custom instruction
  - Check if wallets can handle this

**Action Items**:
1. Review Solana Pay Transaction Request spec in detail
2. Test if Transaction Requests can include custom instructions
3. Evaluate hybrid approach (URL + custom instruction builder)

---

### ✅ CommerceKit Research

**Status**: Evaluation complete - NOT recommended

**Findings**:
- Frontend SDK (JavaScript/TypeScript)
- Package: `@solana-commerce/kit`
- Components: PaymentButton, headless primitives
- Documentation: https://launch.solana.com/docs/commerce-kit

**Compatibility Assessment**:
- ❌ Cannot handle custom program instructions
- ❌ Cannot support multi-recipient splits
- ❌ No PDA account support
- ✅ Good for simple token transfers
- ✅ Good for UI components

**Recommendation**: DO NOT INTEGRATE for V2 contract payments

**What's Known**:
- CommerceKit uses standard SPL token transfer instructions
- PaymentButton is designed for single merchant → customer payments
- Headless primitives could be used but still wouldn't support custom instructions
- Could potentially be used for other payment types (donations, merch)

**Action Items**:
- ✅ Assessment complete
- No further research needed (confirmed incompatible)

---

## 🔬 Current Implementation Gaps

### High Priority Gaps

1. **Kora**:
   - ⏳ Need actual JSON-RPC request/response examples
   - ⏳ Need to test with running server
   - ⏳ Need to verify transaction encoding format

2. **Attestations**:
   - ⚠️ **CRITICAL**: Need actual SAS program ID
   - ⏳ Need account data structure documentation
   - ⏳ Need schema pubkey examples
   - ⏳ Need PDA seed structure verification

### Medium Priority Gaps

3. **Solana Pay**:
   - ⏳ Verify Transaction Request compatibility
   - ⏳ Test custom instruction support

---

## 📚 Research Sources to Check

### Kora
- GitHub: https://github.com/solana-foundation/kora
- Documentation: https://launch.solana.com/docs/kora
- JSON-RPC API reference in docs

### Attestations
- Documentation: https://launch.solana.com/docs/attestations
- GitHub: Search for "solana-attestation-service" or "sas"
- Solana Explorer: Search for "attestations" program
- Example implementations using `sas-lib`

### Solana Pay
- Documentation: https://launch.solana.com/docs/solana-pay
- Specification: https://docs.solanapay.com
- Transaction Request spec details

### CommerceKit
- Documentation: https://launch.solana.com/docs/commerce-kit
- GitHub: Search for "@solana-commerce"
- Package details on npm

---

## 🎯 Next Research Steps

1. **Find SAS Program ID**: 
   - Search Solana Explorer for deployed attestations program
   - Check official GitHub repository
   - Review `sas-lib` examples for program ID references

2. **Test Kora JSON-RPC**:
   - Set up local Kora server
   - Make test JSON-RPC calls
   - Document actual request/response formats
   - Verify transaction encoding

3. **Research Attestations Account Structure**:
   - Find example attestation accounts on-chain
   - Parse account data to understand structure
   - Document field meanings

4. **Verify Solana Pay Transaction Requests**:
   - Review Transaction Request specification
   - Test if custom instructions are supported
   - Evaluate hybrid approach

---

**Last Updated**: After initial implementation - research phase ongoing

