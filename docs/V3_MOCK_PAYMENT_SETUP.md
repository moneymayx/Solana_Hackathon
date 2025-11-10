# V3 Payment Testing Modes

## Overview

V3 supports **three payment modes** for different testing scenarios:
1. **Mock Mode** (`mock`) - UI testing only, no contract calls
2. **Test Contract Mode** (`test_contract`) - Tests actual contract execution using backend's funded wallet
3. **Real Mode** (default) - User pays with their own wallet and USDC

This allows you to test the smart contract without requiring users to have USDC!

## Payment Modes

### Mode 1: Mock (`mock`) - UI Testing Only

When `NEXT_PUBLIC_PAYMENT_MODE=mock`:
1. ✅ V3 payment processor detects mock mode
2. ✅ Skips blockchain transaction **completely**
3. ✅ Generates mock transaction signature
4. ✅ Returns success without real payment
5. ✅ No wallet signature required
6. ✅ No USDC balance check
7. ❌ **Contract is NOT called** (pure UI testing)

### Mode 2: Test Contract (`test_contract`) - Contract Testing ⭐ **RECOMMENDED**

When `NEXT_PUBLIC_PAYMENT_MODE=test_contract`:
1. ✅ Frontend calls backend API (`/api/v3/payment/test`)
2. ✅ Backend uses its own funded wallet to pay
3. ✅ **Contract IS called on devnet** (real execution!)
4. ✅ Transaction is sent and confirmed on-chain
5. ✅ Returns real transaction signature
6. ✅ No user USDC required (backend pays)
7. ✅ Tests actual contract logic and state changes

### Mode 3: Real (default) - Production

When `NEXT_PUBLIC_PAYMENT_MODE` is not set or `real`:
1. ✅ User's wallet must have USDC
2. ✅ User signs transaction
3. ✅ Contract executes with user's payment
4. ✅ Production-ready flow

## Setup

### Option 1: Mock Mode (UI Testing)

Add to `frontend/.env.local`:
```bash
NEXT_PUBLIC_PAYMENT_MODE=mock
```

### Option 2: Test Contract Mode (Contract Testing) ⭐ **RECOMMENDED**

Add to `frontend/.env.local`:
```bash
NEXT_PUBLIC_PAYMENT_MODE=test_contract
NEXT_PUBLIC_API_URL=http://localhost:8000  # Or your backend URL
```

**Backend Requirements:**
- Backend must have a funded wallet at `~/.config/solana/id.json` (or set `BACKEND_WALLET_KEYPAIR_PATH`)
- Backend wallet needs USDC for test payments
- Backend must have `USE_CONTRACT_V3=true` set

### Option 3: Real Mode (Production)

Don't set `NEXT_PUBLIC_PAYMENT_MODE` or set it to `real`.

## Usage

### Testing V3 Payments

1. **Set environment variable:**
   ```bash
   # In frontend/.env.local
   NEXT_PUBLIC_PAYMENT_MODE=mock
   ```

2. **Restart dev server:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test payment:**
   - Navigate to `/test-v3` or use `PaymentMethodSelector`
   - Connect wallet (any wallet works, no funds needed)
   - Click "Pay" button
   - See mock transaction signature (e.g., `MOCK_V3_1234...`)
   - No real funds charged

## Mock Transaction Format

Mock signatures follow this format:
```
MOCK_V3_{timestamp}_{random}
```

Example: `MOCK_V3_1704067200000_a1b2c3d`

## What Gets Tested

### Mock Mode (`mock`)
- ✅ Payment flow logic
- ✅ Component rendering
- ✅ Error handling
- ✅ Success callbacks
- ✅ UI state management
- ❌ Contract execution

### Test Contract Mode (`test_contract`) ⭐
- ✅ All of Mock Mode, PLUS:
- ✅ **Actual smart contract execution on devnet**
- ✅ Transaction building and sending
- ✅ Contract state changes (lottery entries, etc.)
- ✅ PDA creation and updates
- ✅ Token account interactions
- ✅ Transaction confirmation
- ✅ Real transaction signatures

### Real Mode (default)
- ✅ Everything in Test Contract Mode
- ✅ User wallet signing
- ✅ User USDC balance checks

## Switching to Real Payments

To test with real blockchain transactions:

1. **Remove or change environment variable:**
   ```bash
   # In frontend/.env.local
   NEXT_PUBLIC_PAYMENT_MODE=real
   # OR remove the variable entirely
   ```

2. **Restart dev server**

3. **Ensure user has:**
   - Connected Solana wallet
   - USDC token account
   - Sufficient USDC balance
   - SOL for transaction fees

## Error Handling

If you see errors about missing token accounts or insufficient balance:
- Check `NEXT_PUBLIC_PAYMENT_MODE` is set to `mock`
- Ensure environment variable is loaded (restart dev server)
- Check browser console for mock mode detection logs

## Comparison: V2 vs V3 Mock Mode

| Feature | V2 | V3 |
|---------|----|----|
| Environment Variable | `PAYMENT_MODE` (backend) | `NEXT_PUBLIC_PAYMENT_MODE` (frontend) |
| Mock Signature Format | `MOCK_{timestamp}_{random}` | `MOCK_V3_{timestamp}_{random}` |
| Transaction Building | Skipped | Skipped |
| Wallet Signing | Skipped | Skipped |
| Blockchain Call | Skipped | Skipped |

Both work similarly, but V3 checks the environment variable directly in the frontend payment processor.

## Troubleshooting

### Mock mode not working

1. **Check environment variable:**
   ```bash
   # In browser console
   console.log(process.env.NEXT_PUBLIC_PAYMENT_MODE)
   # Should output: "mock"
   ```

2. **Verify it's set before build:**
   - Next.js embeds `NEXT_PUBLIC_*` vars at build time
   - Restart dev server after changing env vars
   - Check `.env.local` file syntax

3. **Check console logs:**
   - Should see: "🧪 MOCK PAYMENT MODE - Simulating V3 transaction..."
   - If not, mock mode isn't being detected

### Real payment fails in mock mode

If you want real payments but get mock transactions:
- Remove `NEXT_PUBLIC_PAYMENT_MODE=mock` from `.env.local`
- Restart dev server
- Clear browser cache if needed

## Notes

- Mock mode is intended for **development and testing only**
- Never enable mock mode in production
- Mock transactions don't affect on-chain state
- Mock signatures won't verify on blockchain explorers
- Use real payments to test actual smart contract integration

