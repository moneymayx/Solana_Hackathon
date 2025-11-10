# V3 Payment Mode Setup

## Overview

V3 payments support three modes:

1. **Mock Mode** (`NEXT_PUBLIC_PAYMENT_MODE=mock`): UI testing only, no blockchain interaction
2. **Test Contract Mode** (`NEXT_PUBLIC_PAYMENT_MODE=test_contract`): Backend pays, real contract execution
3. **Real Mode** (unset or `NEXT_PUBLIC_PAYMENT_MODE=real`): User pays with their wallet

## Current Configuration

The frontend `.env.local` file has been configured with:
```bash
NEXT_PUBLIC_PAYMENT_MODE=test_contract
```

## What Each Mode Does

### Mock Mode (`mock`)
- Frontend simulates transaction (2 second delay)
- Generates mock transaction signature
- **No blockchain call**
- **No contract execution**
- Useful for UI/UX testing without any backend

### Test Contract Mode (`test_contract`)
- Frontend calls backend API: `POST /api/v3/payment/test`
- Backend uses its own funded wallet to pay
- **Real contract execution on devnet**
- Returns real transaction signature
- **No user USDC required**
- Useful for testing contract logic without user funds

### Real Mode (default/unset)
- User's wallet signs and sends transaction
- **Real USDC transfer required**
- **Production flow**
- User must have USDC in their wallet

## Required Setup for Test Contract Mode

### Frontend `.env.local`
```bash
NEXT_PUBLIC_PAYMENT_MODE=test_contract
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend Requirements
1. Backend server running on port 8000
2. Backend wallet keypair: `~/.config/solana/id.json` (or set `BACKEND_WALLET_KEYPAIR_PATH`)
3. Backend wallet needs USDC on devnet for testing
4. V3 lottery initialized on devnet

### Restart Required
⚠️ **Important**: Next.js embeds environment variables at build time. After changing `.env.local`:
1. Stop the frontend dev server
2. Restart with `npm run dev`
3. Hard refresh the browser (Cmd+Shift+R / Ctrl+Shift+R)

## Verification

When `test_contract` mode is active, you should see in the browser console:
```
🧪 TEST CONTRACT MODE - Calling V3 contract via backend (contract WILL execute on devnet)
```

If you see:
```
🔄 Processing V3 entry payment: Amount 10000000 smallest units
```

Then the mode is not being detected. Check:
1. `.env.local` has `NEXT_PUBLIC_PAYMENT_MODE=test_contract`
2. Frontend server was restarted after adding the variable
3. Browser cache cleared / hard refresh

## Troubleshooting

### Error: "Attempt to debit an account but found no record of a prior credit"
**Cause**: Payment mode is not set, so it's trying real payment mode but user doesn't have USDC.
**Fix**: Set `NEXT_PUBLIC_PAYMENT_MODE=test_contract` and restart frontend server.

### Error: "Failed to call contract via backend"
**Cause**: Backend server not running or endpoint not available.
**Fix**: Start backend with `python3 -m uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000`

### Error: "Backend wallet keypair not found"
**Cause**: Backend wallet keypair missing.
**Fix**: Ensure `~/.config/solana/id.json` exists or set `BACKEND_WALLET_KEYPAIR_PATH`

### Error: "Insufficient funds"
**Cause**: Backend wallet doesn't have USDC on devnet.
**Fix**: Fund the backend wallet with devnet USDC.




