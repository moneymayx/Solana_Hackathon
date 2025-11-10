# Kora Integration Research - Payment Flow Analysis

## Current Payment Flow Analysis

### Frontend Payment Flow (V2)

**Location**: `frontend/src/lib/v2/paymentProcessor.ts`

**Current Process**:
1. User selects amount (USDC)
2. Frontend builds custom instruction:
   - Instruction discriminator: `process_entry_payment_v2`
   - Data: `bounty_id (u64)` + `entry_amount (u64)`
   - Accounts: PDAs, user, 4 token accounts, program IDs
3. Transaction created with instruction
4. User signs transaction (must have SOL for fees)
5. Transaction sent to network
6. Confirmation awaited

**Critical Point for Kora**:
- Line 239: `transaction.feePayer = userWallet;`
- **This is where Kora can help** - Kora can be the fee payer instead

## Kora Integration Points

### Option 1: Replace Fee Payer (Recommended)
**Where**: Before sending transaction to network

**Current Code**:
```typescript
transaction.feePayer = userWallet;  // User must have SOL
const signedTransaction = await signTransaction(transaction);
const signature = await connection.sendRawTransaction(...);
```

**With Kora**:
```typescript
// Option A: Let Kora sign and send (fee abstraction)
const base64Transaction = transaction.serialize().toString('base64');
const koraResult = await kora.signAndSendTransaction({
  transaction: base64Transaction,
  feeToken: "USDC"
});

// Option B: Get signed transaction from Kora, then send
const signedFromKora = await kora.signTransaction({
  transaction: base64Transaction
});
// Then send signed transaction
```

### Option 2: Backend Integration

**Where**: `src/services/v2/payment_processor.py` or create new service

**Current Flow**: Frontend builds and sends transaction
**With Kora**: Backend could build transaction, send to Kora for fee abstraction

## Research Needed

### JSON-RPC Method Details

**signTransaction**:
- ✅ Method name: `signTransaction`
- ❓ Parameter format: `{ transaction: string }` or `{ transaction: base64 }`?
- ❓ Transaction format: Base64-encoded Transaction object?
- ❓ Response format: `{ transaction: signed_base64 }`?

**signAndSendTransaction**:
- ✅ Method name: `signAndSendTransaction`
- ❓ Parameter format: Same as signTransaction?
- ❓ Response format: `{ signature: string }`?

**estimateTransactionFee**:
- ✅ Method name: `estimateTransactionFee`
- ❓ Parameters: `{ transaction: base64, feeToken?: string }`?
- ❓ Response: `{ feeAmount: number, feeToken: string, estimatedUSD?: number }`?

### Configuration Research

**Kora Server Setup**:
- Default port: 8080
- Configuration file format?
- How to configure fee tokens (USDC)?
- Authentication requirements?
- Network configuration (devnet/mainnet)?

**Transaction Handling**:
- Does Kora modify the transaction before signing?
- Can Kora handle transactions with multiple instructions?
- Does Kora validate transactions before signing?
- Error handling for invalid transactions?

## Integration Testing Plan

### Test Case 1: Basic Fee Abstraction
1. Build V2 payment transaction (current flow)
2. Convert to base64
3. Send to Kora `signTransaction` method
4. Get signed transaction back
5. Send signed transaction to network
6. Verify fees were paid in USDC (not SOL)

### Test Case 2: Sign and Send
1. Build V2 payment transaction
2. Send to Kora `signAndSendTransaction`
3. Verify transaction sent and fees abstracted

### Test Case 3: Fee Estimation
1. Build transaction
2. Call `estimateTransactionFee` with USDC
3. Display fee estimate to user before signing

## Questions to Answer

1. **Transaction Format**: Does Kora expect base64-encoded Transaction object?
2. **Multiple Instructions**: Can transaction have multiple instructions?
3. **Fee Token Configuration**: How to configure which tokens Kora accepts fees in?
4. **Error Responses**: What errors does Kora return and how to handle?
5. **Network Support**: Does Kora work on devnet for testing?

---

**Status**: Architecture understood, needs API detail research and testing

