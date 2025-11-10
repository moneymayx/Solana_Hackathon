# SDK Integration - Next Steps

## 🎯 Immediate Action Items

### Priority 1: Find SAS Program ID (CRITICAL BLOCKER)

**Why**: Cannot query attestations without the program ID

**Steps**:
1. **Run discovery script**:
   ```bash
   python scripts/sdk/find_attestations_program.py --network devnet
   ```

2. **Manual search**:
   - Visit: https://launch.solana.com/docs/attestations
   - Check GitHub: Search for "solana-foundation/attestations"
   - Search Solana Explorer: https://explorer.solana.com (search "attestations")
   - Look for program deployment transactions

3. **Once found, update `.env`**:
   ```bash
   ATTESTATIONS_PROGRAM_ID_DEVNET=<found_devnet_id>
   ATTESTATIONS_PROGRAM_ID_MAINNET=<found_mainnet_id>
   ```

4. **Test**:
   ```bash
   # Enable attestations
   ENABLE_ATTESTATIONS_SDK=true
   
   # Test endpoint
   curl http://localhost:8000/api/sdk-test/attestations/verify-kyc \
     -H "Content-Type: application/json" \
     -d '{"wallet_address": "test_wallet"}'
   ```

---

### Priority 2: Set Up and Test Kora

**Why**: Need to verify JSON-RPC API format and fee abstraction works

**Steps**:
1. **Install Kora CLI**:
   ```bash
   cargo install kora-cli
   ```

2. **Run Kora server**:
   ```bash
   kora rpc
   # Runs on http://localhost:8080 by default
   ```

3. **Test connection**:
   ```bash
   python scripts/sdk/test_kora_setup.py --url http://localhost:8080
   ```

4. **Configure environment**:
   ```bash
   ENABLE_KORA_SDK=true
   KORA_RPC_URL=http://localhost:8080
   KORA_API_KEY=<if_required>
   ```

5. **Test JSON-RPC methods**:
   - Call `/api/sdk-test/kora/config` to get server config
   - Try `estimateTransactionFee` with a test transaction
   - Document actual request/response formats

6. **Integration test**:
   - Build a V2 payment transaction
   - Send to Kora for fee abstraction
   - Verify fees paid in USDC instead of SOL

---

### Priority 3: Understand Attestation Account Structure

**Why**: Need to parse account data to extract KYC information

**Steps**:
1. **Find example attestation accounts**:
   - Query known wallets with attestations
   - Look for accounts owned by SAS program

2. **Query and decode**:
   ```python
   # Example using Solana RPC
   account_info = client.get_account_info(attestation_pda)
   account_data = account_info.value.data
   # Parse account data structure
   ```

3. **Document structure**:
   - What fields contain KYC info?
   - How is schema referenced?
   - How is credential referenced?

4. **Update service**:
   - Implement account data parsing
   - Extract KYC fields (name, DOB, country, etc.)
   - Update `verify_kyc_attestation` method

---

### Priority 4: Research Solana Pay Transaction Requests

**Why**: Verify if Transaction Requests can handle custom instructions

**Steps**:
1. **Read specification**:
   - Review: https://docs.solanapay.com/core/transaction-request
   - Check for custom instruction support

2. **Test with custom instruction**:
   - Create Transaction Request with V2 instruction
   - Test with Phantom/Solflare wallet
   - Verify if it works

3. **Document findings**:
   - Update compatibility assessment
   - Note if hybrid approach is possible

---

## 📋 Testing Checklist

### Kora Testing
- [ ] Kora server running locally
- [ ] Connection test successful
- [ ] `getConfig` method works
- [ ] `signTransaction` tested with sample transaction
- [ ] `signAndSendTransaction` tested end-to-end
- [ ] Fee abstraction verified (USDC instead of SOL)
- [ ] Integration with V2 payment flow tested

### Attestations Testing
- [ ] SAS program ID found and configured
- [ ] Can query attestation accounts
- [ ] PDA derivation verified
- [ ] Account data structure understood
- [ ] KYC attestation parsing works
- [ ] Geographic attestation parsing works
- [ ] Integration with payment flow (KYC check before payment)

### Solana Pay Testing
- [ ] Transaction Request spec reviewed
- [ ] Custom instruction support tested
- [ ] Compatibility with V2 contract verified

---

## 🔧 Utility Scripts

### Find Attestations Program ID
```bash
python scripts/sdk/find_attestations_program.py --network devnet
python scripts/sdk/find_attestations_program.py --network mainnet
```

### Test Kora Setup
```bash
python scripts/sdk/test_kora_setup.py --url http://localhost:8080
```

---

## 📚 Research Resources

### Kora
- Documentation: https://launch.solana.com/docs/kora
- GitHub: Search for "solana-foundation/kora"
- JSON-RPC 2.0 spec: Standard JSON-RPC protocol

### Attestations
- Documentation: https://launch.solana.com/docs/attestations
- GitHub: Search for "solana-foundation/attestations"
- SAS library: `sas-lib` (JavaScript/TypeScript examples)

### Solana Pay
- Documentation: https://launch.solana.com/docs/solana-pay
- Specification: https://docs.solanapay.com
- Transaction Request spec: Detailed format documentation

---

## 🚀 Once Critical Items Complete

After SAS program ID is found and Kora is tested:

1. **Update Services**:
   - Replace placeholder program ID
   - Update account parsing logic
   - Implement fee abstraction integration

2. **Create POCs**:
   - Kora POC: USDC fee payment
   - Attestations POC: KYC verification before payment

3. **Integration**:
   - Add KYC check to payment flow
   - Add fee abstraction option to frontend
   - Test end-to-end flows

---

**Last Updated**: After creating utility scripts and documentation

