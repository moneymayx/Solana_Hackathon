# Solana Pay Transaction Request - Research Update

## Research Findings

### Transaction Request Specification

Based on Solana Pay specification review:

**Transaction Requests** support:
- ✅ Custom instructions (via `account` metadata)
- ✅ Multiple accounts
- ✅ Account metadata (for PDAs, program IDs, etc.)
- ⚠️ Requires wallet to build transaction interactively

### Compatibility with V2 Contract

**Key Finding**: Transaction Requests CAN include custom instructions, BUT:

1. **Account Metadata Required**:
   - Transaction Requests use `account` metadata to specify accounts
   - PDAs can be included in metadata
   - Program IDs can be specified

2. **Interactive Building**:
   - Wallet receives transaction request URL
   - Wallet builds transaction based on metadata
   - User approves and signs

3. **Limitation**:
   - Wallet must support building custom instructions
   - Not all wallets may support this
   - Requires specific URL format

### Recommended Approach

**Hybrid Method** (Most Compatible):

1. **Backend Handler Pattern**:
   ```
   User clicks payment → Generate Solana Pay URL
   → Wallet opens URL → Wallet calls backend handler
   → Backend builds V2 transaction → Returns to wallet
   → User signs and sends
   ```

2. **Transaction Request Format**:
   ```
   solana:?transaction=<backend_handler_url>
   &label=Billions Bounty Entry
   &message=Payment for bounty entry
   ```

3. **Backend Handler**:
   - Receives transaction request
   - Builds V2 custom instruction
   - Returns transaction in correct format
   - Wallet signs and sends

### Conclusion

**V2 Contract Compatibility**: ⚠️ **PARTIALLY COMPATIBLE**

- Transaction Requests can technically support custom instructions
- Requires wallet support for transaction building
- Backend handler pattern is most reliable
- May not work with all wallets

**Recommendation**: 
- Keep custom implementation for primary payment flow
- Solana Pay can be used for simple transfers (donations, merch)
- Transaction Request handler pattern could work but needs testing
- Not recommended as primary payment method for V2 contract

---

## Next Steps

1. **Test Transaction Request Handler**:
   - Create backend handler endpoint
   - Build V2 transaction in handler
   - Test with Phantom/Solflare
   - Verify compatibility

2. **Document Wallet Support**:
   - Which wallets support Transaction Requests?
   - Which wallets can build custom instructions?
   - Test compatibility matrix

3. **Decide Integration Approach**:
   - Use Solana Pay for simple transfers only
   - Or implement handler pattern for V2 payments
   - Or keep custom implementation

---

**Status**: Research complete - Solana Pay Transaction Requests are technically possible but not ideal for V2 contract. Keep custom implementation.

