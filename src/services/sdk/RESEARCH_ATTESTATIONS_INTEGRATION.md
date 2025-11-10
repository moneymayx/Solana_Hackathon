# Attestations Integration Research - KYC Flow Analysis

## Current KYC Flow Analysis

### Existing KYC Service

**Location**: `src/services/kyc_service.py`

**Current Process**:
1. MoonPay webhook sends KYC data
2. Service extracts KYC information:
   - Full name
   - Date of birth
   - Phone number
   - Address
   - KYC status
3. Updates User model with KYC fields
4. Stores KYC provider as "moonpay"
5. User can then use platform with verified status

**User Model KYC Fields**:
```python
full_name: str
date_of_birth: datetime
phone_number: str
address: str
kyc_status: str  # pending, verified, rejected
kyc_provider: str  # moonpay, manual
kyc_reference_id: str  # MoonPay transaction ID
```

## Attestations Integration Points

### Replacement Strategy

**Option 1: Check Attestations Before Payment**
- Before allowing payment, check wallet for KYC attestation
- If verified, proceed with payment
- If not verified, show KYC required message

**Option 2: Background Verification**
- Check attestations when user connects wallet
- Update User.kyc_status based on attestation
- Store kyc_provider as "attestations"

### Integration Location

**Current Payment Flow**: `apps/backend/main.py` -> `/api/payment/create`
- Before creating payment, check KYC status
- Could add attestation check here

**Current KYC Service**: `src/services/kyc_service.py`
- Could add `verify_attestation_kyc()` method
- Integrate with existing KYC workflow

## Research Needed

### CRITICAL: SAS Program ID

**Status**: ⚠️ NEEDS TO BE FOUND

**Where to Find**:
1. Official Solana Attestations documentation
2. GitHub repository: https://github.com/solana-foundation/attestations
3. Solana Explorer: Search for deployed program
4. `sas-lib` examples: May contain program ID references

**Expected Format**: Base58 pubkey (44 characters)

**Network Differences**: May have different IDs for devnet vs mainnet

### Account Structure Research

**PDA Derivation**:
- ❓ Actual seed structure: `[b"attestation", wallet]` or different?
- ❓ Do credentials affect PDA derivation?
- ❓ Do schemas affect PDA derivation?
- ❓ Multiple attestations per wallet - how to query all?

**Account Data Layout**:
- ❓ Account size and structure
- ❓ How is credential stored?
- ❓ How is schema stored?
- ❓ Where is actual KYC data (name, DOB, country)?
- ❓ How to deserialize account data?

### Schema Research

**Standard Schemas Needed**:
1. **KYC Schema**:
   - What fields does it contain?
   - Schema pubkey address?
   - Which credential authorities issue KYC attestations?

2. **Geographic Schema**:
   - How is country information stored?
   - Schema pubkey address?

3. **Accreditation Schema**:
   - What types of accreditation are supported?
   - Schema pubkey address?

### Credential Research

**Credential Authorities**:
- ❓ Who are trusted credential authorities for KYC?
- ❓ Do we need to whitelist specific credentials?
- ❓ Can we trust any credential or need verification?
- ❓ How to find credential pubkeys?

## Integration Testing Plan

### Test Case 1: Query Existing Attestation
1. Find a wallet with known KYC attestation (testnet)
2. Query SAS program for attestation account
3. Parse account data
4. Extract KYC information
5. Verify against known data

### Test Case 2: Integration with Payment Flow
1. User attempts payment
2. Check wallet for KYC attestation
3. If verified, allow payment
4. If not verified, show KYC required message

### Test Case 3: Geographic Restrictions
1. Check wallet for geographic attestation
2. Verify country matches allowed list
3. Block or allow based on geographic status

## Questions to Answer

1. **Program ID**: What is the actual SAS program ID?
2. **Account Structure**: How to parse attestation account data?
3. **Schema IDs**: What are standard schema pubkeys?
4. **Credential Trust**: Which credentials should we trust?
5. **Multiple Attestations**: How to query all attestations for a wallet?

## Alternative Approaches

### If Program ID Not Found:
1. Use Solana Explorer to search for attestation programs
2. Look for example attestations on-chain
3. Reverse engineer PDA derivation from existing accounts
4. Contact Solana Foundation for official program ID

### If Account Structure Unknown:
1. Query example attestation accounts
2. Decode base64 account data
3. Analyze structure
4. Document findings

---

**Status**: Architecture understood, CRITICAL gaps: Program ID and account structure

