# SDK Integration TODO Status

## ✅ Completed Tasks

### Implementation Structure
- ✅ Created SDK service directory structure
- ✅ Created test API routers for all 4 SDKs
- ✅ Integrated routers into main.py
- ✅ Created test files structure
- ✅ Updated documentation

### Architecture Corrections
- ✅ Fixed Kora: Changed from REST API to JSON-RPC 2.0 ✅
- ✅ Fixed Attestations: Changed to on-chain program queries ✅
- ✅ Updated Solana Pay: Following official transfer request spec ✅
- ✅ Updated CommerceKit: Clarified frontend SDK nature ✅

## ⏳ Research Tasks (NOT DONE YET)

### 1. Kora SDK Research ⏳

**Status**: Architecture understood, API details needed

**What Needs Research**:
- [ ] **Exact JSON-RPC method signatures**
  - Parameter formats for `signTransaction`
  - Parameter formats for `signAndSendTransaction`
  - Parameter formats for `estimateTransactionFee`
  - Transaction encoding (base64? other format?)
  
- [ ] **Response format structures**
  - What does `signTransaction` return?
  - What does `signAndSendTransaction` return?
  - Error response formats
  
- [ ] **Configuration details**
  - How to configure fee tokens (USDC)?
  - Authentication methods (API key vs HMAC)?
  - Network configuration (devnet/mainnet)?
  
- [ ] **Integration testing**
  - Test with actual Kora server
  - Verify transaction encoding works
  - Test fee abstraction end-to-end

**Action Items**:
1. Review Kora GitHub for examples
2. Set up local Kora server and test
3. Document exact request/response formats
4. Create integration test

**Priority**: HIGH (needed for testing)

---

### 2. Attestations SDK Research ⏳

**Status**: Architecture understood, CRITICAL gaps

**What Needs Research**:
- [ ] **CRITICAL: SAS Program ID** ⚠️
  - Find actual Solana Attestations Service program ID
  - May differ for devnet vs mainnet
  - Current placeholder: `SASProgram111111111111111111111111111111`
  - **BLOCKER**: Cannot query attestations without this
  
- [ ] **PDA Seed Structure**
  - Current assumption: `[b"attestation", wallet, credential?, schema?]`
  - Need to verify actual seed structure from docs/examples
  - Verify PDA derivation is correct
  
- [ ] **Account Data Structure**
  - How to deserialize attestation account data
  - What fields contain KYC information (name, DOB, country)?
  - Account layout and field positions
  - Data encoding format
  
- [ ] **Schema Pubkeys**
  - Standard KYC schema address
  - Standard geographic schema address
  - Standard accreditation schema address
  - How to find/use schemas
  
- [ ] **Credential Authorities**
  - Which credentials are trusted for KYC?
  - How to verify credential authority?
  - Public credential authorities list?

**Action Items**:
1. **URGENT**: Find SAS program ID from official sources
2. Review `sas-lib` examples for program ID and structure
3. Query example attestation accounts on-chain
4. Analyze account data structure
5. Document schema pubkeys

**Priority**: HIGH (program ID is blocker)

---

### 3. Solana Pay Research ⏳

**Status**: Transfer requests done, Transaction Requests need research

**What Needs Research**:
- [ ] **Transaction Request Specification**
  - Can Transaction Requests include custom program instructions?
  - Can they specify PDA accounts?
  - Can they handle multi-recipient payments?
  - Account ordering flexibility?
  
- [ ] **Hybrid Approach Feasibility**
  - Can we use Transaction Request URL but build custom instruction?
  - How do wallets handle this pattern?
  - Backend handler implementation

**Action Items**:
1. Read full Transaction Request specification
2. Test Transaction Request with custom instruction
3. Evaluate hybrid approach

**Priority**: MEDIUM (likely won't work, but should verify)

---

### 4. CommerceKit Research ✅

**Status**: Evaluation complete

**Assessment**: NOT compatible with V2 contract
- Frontend SDK (JavaScript/TypeScript)
- Cannot handle custom instructions
- Cannot support multi-recipient splits
- **Recommendation**: DO NOT INTEGRATE

**No Further Research Needed**

---

## 🎯 Immediate Next Steps

### Priority 1: Find SAS Program ID
1. Check official Solana Attestations documentation
2. Search Solana Explorer for deployed program
3. Review `sas-lib` examples/GitHub
4. Update `ATTESTATIONS_PROGRAM_ID` in service

### Priority 2: Test Kora Integration
1. Install Kora CLI: `cargo install kora-cli`
2. Run local Kora server
3. Test JSON-RPC calls
4. Document actual request/response formats

### Priority 3: Understand Attestation Account Structure
1. Find example attestation accounts on-chain
2. Query and decode account data
3. Document structure
4. Implement parsing

---

## 📝 Research Notes to Add

As research is conducted, update:
- `RESEARCH_KORA_INTEGRATION.md` with API details
- `RESEARCH_ATTESTATIONS_INTEGRATION.md` with program ID and account structure
- `RESEARCH_SOLANA_PAY_COMPATIBILITY.md` with Transaction Request findings

---

**Last Updated**: After structure implementation, before detailed research

