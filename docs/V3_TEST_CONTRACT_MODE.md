# V3 Test Contract Mode - Testing Smart Contract Without User Funds

## Quick Start

**Frontend `.env.local`:**
```bash
NEXT_PUBLIC_PAYMENT_MODE=test_contract
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend `.env`:**
```bash
USE_CONTRACT_V3=true
LOTTERY_PROGRAM_ID_V3=52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov
BACKEND_WALLET_KEYPAIR_PATH=~/.config/solana/id.json  # Optional, defaults to Solana CLI wallet
```

**Restart both frontend and backend, then test payments!**

## How It Works

1. **User clicks "Pay"** in the frontend
2. **Frontend detects `test_contract` mode** and calls backend API instead of building transaction
3. **Backend receives request** at `/api/v3/payment/test`
4. **Backend uses its own wallet** (with USDC) to build and send the V3 payment transaction
5. **Contract executes on devnet** (real blockchain transaction!)
6. **Backend returns transaction signature** to frontend
7. **User sees success** with real transaction link

## Key Benefits

✅ **Tests actual contract** - Real on-chain execution  
✅ **No user funds needed** - Backend pays  
✅ **Real transaction signatures** - Can verify on explorer  
✅ **Tests contract state** - Lottery entries, PDAs, etc. all update  
✅ **Same flow as production** - Just backend pays instead of user  

## Backend Requirements

The backend wallet (`~/.config/solana/id.json` by default) must have:
- **SOL** for transaction fees (~0.0005 SOL per transaction)
- **USDC** for test payments (amount depends on what you're testing)

### Checking Backend Wallet

```bash
# Check SOL balance
solana balance --url devnet

# Check USDC balance (if you have spl-token installed)
spl-token balance <USDC_MINT> --owner ~/.config/solana/id.json --url devnet
```

### Funding Backend Wallet

```bash
# Get SOL from devnet faucet
solana airdrop 1 --url devnet

# For USDC, you'll need to:
# 1. Use a devnet USDC faucet, OR
# 2. Transfer from another wallet that has devnet USDC
```

## API Endpoint

**POST** `/api/v3/payment/test`

**Request:**
```json
{
  "user_wallet": "UserWalletAddress...",
  "entry_amount": 10000000,
  "amount_usdc": 10.0,
  "entry_nonce": 1
}
```

**Response:**
```json
{
  "success": true,
  "transaction_signature": "5KQz...",
  "message": "🧪 TEST: V3 contract executed using backend wallet...",
  "lottery_pda": "HsZZAW2hPyeewapZEGrNJWgnHKc1mQU34oLuBXJUSV2x",
  "entry_pda": "...",
  "amount_usdc": 10.0,
  "is_test": true,
  "entry_nonce": 1,
  "explorer_url": "https://explorer.solana.com/tx/..."
}
```

## Comparison: Mock vs Test Contract vs Real

| Feature | Mock | Test Contract | Real |
|---------|------|---------------|------|
| UI Testing | ✅ | ✅ | ✅ |
| Contract Execution | ❌ | ✅ | ✅ |
| User USDC Needed | ❌ | ❌ | ✅ |
| User Signs Transaction | ❌ | ❌ | ✅ |
| Real Transaction | ❌ | ✅ | ✅ |
| Contract State Changes | ❌ | ✅ | ✅ |
| Explorer Link | Fake | Real | Real |

## Entry Nonce Tracking (Multiple Payments Per Wallet)

- The backend maintains a per-wallet nonce in the database table `v3_entry_nonce_tracker`
- Each test payment increments the nonce and passes it to the contract
- The updated contract uses `[b"entry", lottery, signer, entry_nonce]` seeds so every entry is unique
- Frontend stores the latest nonce in `localStorage` to stay in sync with the backend

### Database Migration

1. Ensure the new model is migrated: run `alembic revision --autogenerate -m "Add V3 entry nonce tracker"` (or create the table manually if using SQLite)
2. Apply the migration: `alembic upgrade head`
3. Existing environments should backfill any wallets that already entered before this update

## Troubleshooting

### "Backend wallet keypair not found"
- Ensure `~/.config/solana/id.json` exists
- Or set `BACKEND_WALLET_KEYPAIR_PATH` env var

### "Insufficient funds"
- Backend wallet needs SOL for fees
- Backend wallet needs USDC for test payments
- Check balances and fund if needed

### "V3 contract adapter not available"
- Set `USE_CONTRACT_V3=true` in backend `.env`
- Restart backend server
- Check logs for adapter initialization

### "Transaction failed"
- Check backend logs for detailed error
- Verify lottery is initialized
- Ensure backend wallet has sufficient USDC
- Check devnet RPC endpoint is accessible

## Production Note

⚠️ **Never enable `test_contract` mode in production!**

This mode allows the backend to pay on behalf of users, which is only for testing. In production, users must sign and pay their own transactions.




