# 🧪 Mock Payment Testing Guide

**Purpose:** Test the complete payment + smart contract flow without requiring users to have USDC

---

## How It Works

### Mock Payment Mode (`PAYMENT_MODE=mock`)

**What happens:**
1. ✅ User clicks "Pay to Participate"
2. ✅ Frontend simulates wallet transaction (2 second delay, no wallet popup)
3. ✅ Backend generates mock payment signature
4. ✅ **Smart contracts ARE called on devnet** (real contract execution)
5. ✅ User receives free questions
6. ✅ All contract state is updated on devnet blockchain

**What's skipped:**
- ❌ No wallet signature required
- ❌ No USDC balance check
- ❌ No real token transfer

---

## Setup

### 1. Enable Mock Payment Mode

Edit `.env`:
```bash
# Payment Mode - set to "mock" for testing
PAYMENT_MODE=mock

# Use devnet for testing
SOLANA_NETWORK=devnet
```

### 2. Restart Backend

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate
python3 apps/backend/main.py
```

---

## Testing Flow

### User Experience

**Step 1: Connect Wallet**
- User connects wallet normally
- No funds required

**Step 2: Click "Pay to Participate"**
- Sees message: "🧪 TEST MODE: Simulating payment (no real funds will be charged)"
- No wallet popup appears
- 2 second simulated delay
- Message: "✅ Mock transaction complete: MOCK_1234..."

**Step 3: Backend Processing**
- Mock signature is verified
- **Devnet smart contract is called** (real execution!)
- Free questions are granted
- Message: "✅ Payment successful! You can now participate."

**Step 4: User Can Participate**
- User has free questions
- Can send messages
- All features work normally

---

## What Gets Tested

### ✅ Tested (Same as Production)
- Smart contract execution on devnet
- Fund distribution logic (60/20/10/10 split)
- Lottery entry recording
- Database transactions
- Free question granting
- User state management
- Contract PDA interactions
- Token account logic

### ⚠️ Not Tested (Mocked)
- Actual USDC transfer
- Wallet signing
- Transaction fees
- User's token balance

---

## Backend Logs

### Mock Mode Indicators

```
🧪 Using MOCK payment mode - no real transactions
🧪 Creating MOCK transaction: $10.0 for Ega2R4...
🧪 TEST MODE: This is a simulated payment...
🧪 MOCK verifying transaction: MOCK_1730...
🧪 MOCK PAYMENT SUCCESS: Granting 10 free questions
🔗 Triggering DEVNET smart contract for mock payment
✅ Devnet smart contract executed: ABC123...
```

### Real Mode Indicators

```
💰 Using REAL payment mode - actual blockchain transactions
💰 REAL payment verification
```

---

## API Response Differences

### Mock Mode Response

```json
{
  "success": true,
  "transaction": {
    "recipient": "MockTreasury111...",
    "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "from_ata": "...",
    "to_ata": "...",
    "units": 10000000,
    "amount_usd": 10.0
  },
  "warning": "🧪 TEST MODE: This is a simulated payment. No real funds will be transferred. You'll receive free questions for testing.",
  "message": "Mock transaction details ready (TEST MODE)",
  "is_mock": true
}
```

### Real Mode Response

```json
{
  "success": true,
  "transaction": {
    "recipient": "7BKoaQPx7euCSdyJgzJ...",
    "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "from_ata": "...",
    "to_ata": "...",
    "units": 10000000,
    "amount_usd": 10.0
  },
  "warning": null,
  "message": "Transaction details ready for signing",
  "is_mock": false
}
```

---

## Switching to Production

### When Ready for Mainnet

1. **Update `.env`:**
   ```bash
   PAYMENT_MODE=real
   SOLANA_NETWORK=mainnet-beta
   ```

2. **Restart Backend:**
   ```bash
   # Kill and restart
   lsof -ti:8000 | xargs kill -9
   python3 apps/backend/main.py
   ```

3. **Deploy Frontend with Environment:**
   ```bash
   # Set environment variable in Vercel/deployment
   NEXT_PUBLIC_PAYMENT_MODE=real
   ```

4. **Verify Logs:**
   - Should see: `💰 Using REAL payment mode`
   - Should NOT see: `🧪 MOCK`

---

## Testing Checklist

### Before Switching to Real Mode

- [ ] Mock payment flow works end-to-end
- [ ] Devnet smart contracts execute successfully
- [ ] Free questions are granted correctly
- [ ] Database entries are created
- [ ] User state updates properly
- [ ] Error handling works (try invalid amounts)
- [ ] Frontend shows correct test mode messages
- [ ] Backend logs show smart contract execution

### Before Going to Mainnet

- [ ] Test with small real payment on devnet
- [ ] Verify actual USDC transfer works
- [ ] Test with real wallet signatures
- [ ] Verify treasury wallet receives funds
- [ ] Check gas fees are acceptable
- [ ] Test error cases with real blockchain
- [ ] Verify refund logic (if applicable)
- [ ] Load test with multiple users

---

## Troubleshooting

### "Smart contract failed" in mock mode

**Problem:** Mock payment succeeds but contract execution fails

**Solution:**
1. Check devnet is accessible
2. Verify program ID in `.env`
3. Check backend has authority keys
4. Look for specific error in logs

### Mock mode not activating

**Problem:** Still seeing wallet popups

**Solution:**
1. Verify `.env` has `PAYMENT_MODE=mock`
2. Restart backend
3. Check logs for "🧪 Using MOCK payment mode"
4. Clear browser cache and hard refresh

### Questions not being granted

**Problem:** Payment succeeds but no questions granted

**Solution:**
1. Check `free_question_service` logs
2. Verify user exists in database
3. Check wallet address matches
4. Look for database errors in logs

---

## Cost Analysis

### Mock Mode (Testing)
- **User cost:** $0 (no real payments)
- **Devnet transactions:** Free (devnet SOL is free)
- **Testing cost:** $0

### Real Mode (Production)
- **User cost:** $10+ in USDC
- **Transaction fees:** ~$0.00025 SOL per transaction
- **Your cost:** Gas fees for contract execution

---

## Key Files

```
src/services/mock_payment_service.py    # Mock payment logic
apps/backend/main.py                     # Payment endpoint (lines 1368-1532)
frontend/src/components/BountyChatInterface.tsx  # Frontend payment flow
.env                                     # Configuration (PAYMENT_MODE)
```

---

## Summary

**Mock Mode = Perfect for Testing**
- No USDC needed
- No wallet signatures
- Still tests smart contracts on devnet
- Fast iteration
- Free for developers and testers

**Real Mode = Production**
- Requires USDC
- Real wallet signatures
- Actual blockchain transactions
- User pays gas fees
- Production-ready

**Switch by changing ONE environment variable:** `PAYMENT_MODE=mock` → `PAYMENT_MODE=real`

---

**Status:** ✅ Ready to test the full flow without requiring users to have USDC!

