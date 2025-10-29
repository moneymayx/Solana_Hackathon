# 🎨 Mock NFT Verification - Testing Guide

**Date:** October 29, 2025  
**Status:** ✅ **FULLY OPERATIONAL**  
**Integration:** Works with existing Mock Payment System

---

## 🎯 Overview

Mock NFT verification allows users to test the "Verify NFT for 5 Free Questions" feature without owning any real NFTs. It uses the same `PAYMENT_MODE=mock` setting as the payment system.

---

## 🚀 How It Works

### Mock Mode (`PAYMENT_MODE=mock`)
- ✅ User clicks "Verify NFT for 5 Free Questions"
- ✅ Backend checks `PAYMENT_MODE` environment variable
- ✅ If `mock`, user always "has" an NFT
- ✅ 5 free questions granted automatically
- ✅ No blockchain calls needed
- ✅ No Solana RPC rate limiting issues

### Real Mode (`PAYMENT_MODE=real`)
- User clicks "Verify NFT"
- Backend makes real Solana RPC calls
- Checks actual NFT ownership on-chain
- Grants questions only if real NFT owned

---

## 📡 API Endpoints

### 1. Check NFT Status
```bash
GET /api/nft/status/{wallet_address}
```

**Mock Response:**
```json
{
  "success": true,
  "has_nft": true,
  "nft_count": 1,
  "eligible_nfts": [
    {
      "mint": "MOCK_NFT_11111111111111111111111111111",
      "name": "Test NFT #1",
      "collection": "Billions Bounty Test Collection",
      "is_mock": true
    }
  ],
  "is_mock": true,
  "message": "🎨 TEST MODE: Mock NFT detected. In production, this would verify real NFTs."
}
```

### 2. Verify NFT and Grant Questions
```bash
POST /api/nft/verify
Content-Type: application/json

{
  "wallet_address": "Ega2R4wj89CMogco9r4HUvrGG4aNnXQD9aDYM6JcZr7G"
}
```

**Mock Response:**
```json
{
  "success": true,
  "verified": true,
  "has_nft": true,
  "questions_granted": 5,
  "nft_info": {
    "mint": "MOCK_NFT_11111111111111111111111111111",
    "name": "Test NFT #1",
    "collection": "Billions Bounty Test Collection",
    "is_mock": true
  },
  "is_mock": true,
  "message": "🎨 TEST: NFT verified! Granted 5 free questions (no real NFT required)"
}
```

---

## 🧪 Testing Steps

### 1. Ensure Mock Mode is Enabled
```bash
# In .env file
PAYMENT_MODE=mock
```

### 2. Start Backend
```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate
python3 apps/backend/main.py
```

### 3. Test in Browser
1. Navigate to bounty page
2. Connect wallet (any wallet, no NFTs needed)
3. Click **"Verify NFT for 5 Free Questions"** button
4. See: "🎨 TEST MODE: Mock NFT detected"
5. Get 5 free questions automatically
6. Start chatting with AI

---

## 📊 User Experience Flow

### Mock Mode (Current)
```
User clicks "Verify NFT"
  → Backend checks PAYMENT_MODE=mock
  → Always returns "NFT found"
  → Grants 5 free questions
  → No blockchain calls
  → No RPC rate limits
  → Instant response
```

### Real Mode (Production)
```
User clicks "Verify NFT"
  → Backend calls Solana RPC
  → Checks wallet for eligible NFTs
  → Verifies collection/mint address
  → Grants questions only if NFT owned
  → May hit RPC rate limits
```

---

## 🔧 Configuration

### Environment Variable
```bash
# Single variable controls both payment AND NFT mocking
PAYMENT_MODE=mock   # Mock mode for both
PAYMENT_MODE=real   # Real mode for both
```

### Why Share the Same Variable?
- Simplifies configuration
- Consistent testing behavior
- Easy to switch modes
- No confusion between different mock states

---

## 🎨 What Gets Tested

### ✅ With Mock NFT
- NFT verification flow
- Free question granting (5 questions)
- Database record creation
- User eligibility updates
- Frontend UI feedback
- Error handling

### ⚠️ Not Tested (Mock Mode)
- Real NFT ownership check
- Solana RPC calls
- Collection verification
- Mint address validation
- On-chain metadata fetching

---

## 🔄 Integration with Mock Payment

Both systems use the same `PAYMENT_MODE` variable:

| Feature | Mock Mode | Real Mode |
|---------|-----------|-----------|
| Payment | ✅ No USDC needed | 💰 Real USDC required |
| NFT | ✅ No NFT needed | 🎨 Real NFT required |
| Smart Contract | ✅ Devnet simulation | 💎 Mainnet execution |
| Free Questions | ✅ Auto-granted | 💵 Payment-based |

---

## 📝 Backend Logs

### Mock NFT Mode
```
🎨 Mock NFT Service initialized
🎨 Using MOCK NFT mode - no real NFTs required
🎨 MOCK NFT verification for Ega2R4wj89CMogco9r4HUvrGG4aNnXQD9aDYM6JcZr7G
✅ Granted 5 free questions for mock NFT
```

### Real NFT Mode
```
💎 REAL NFT verification
Calling Solana RPC...
Checking NFT ownership on-chain...
```

---

## 🐛 Fixes Applied

### Issue 1: Missing NFT Endpoint
- **Problem:** Frontend calling `/api/nft/status/{wallet}` → 404 error
- **Solution:** Created endpoint that checks `PAYMENT_MODE`
- **Result:** Endpoint now returns mock NFT data in test mode

### Issue 2: Solana RPC Rate Limiting
- **Problem:** Frontend hitting public RPC → 403 Forbidden
- **Solution:** Mock mode bypasses RPC calls entirely
- **Result:** No more rate limit errors in testing

### Issue 3: No Mock NFT Service
- **Problem:** No way to test NFT flow without owning NFTs
- **Solution:** Created `mock_nft_service.py` similar to `mock_payment_service.py`
- **Result:** Complete NFT testing without blockchain

---

## 🎯 Testing Checklist

- [ ] Backend running with `PAYMENT_MODE=mock`
- [ ] Frontend running on `localhost:3000`
- [ ] Can see "Verify NFT for 5 Free Questions" button
- [ ] Click button shows mock NFT detected
- [ ] 5 free questions granted
- [ ] No 404 errors for `/api/nft/status`
- [ ] No 403 RPC errors
- [ ] Can participate after NFT verification

---

## 🚦 Switching Modes

### To Test Mode (Mock NFTs)
```bash
# .env
PAYMENT_MODE=mock

# Restart backend
lsof -ti:8000 | xargs kill -9
python3 apps/backend/main.py
```

### To Production Mode (Real NFTs)
```bash
# .env
PAYMENT_MODE=real

# Restart backend
lsof -ti:8000 | xargs kill -9
python3 apps/backend/main.py
```

---

## 📈 Free Questions Summary

| Method | Questions Granted | Mock Mode Works? |
|--------|-------------------|------------------|
| Mock Payment | 10 questions | ✅ Yes |
| Mock NFT | 5 questions | ✅ Yes |
| Referral | 5 questions | ✅ Yes (if implemented) |
| **Total Possible** | **20+ questions** | ✅ All stackable |

---

## 🎉 Summary

**Mock NFT verification is now fully operational!**

You can:
- ✅ Test NFT verification without owning NFTs
- ✅ Get 5 free questions instantly
- ✅ Avoid Solana RPC rate limiting
- ✅ Test complete user flow
- ✅ Switch to real NFTs anytime

**Both mock payment AND mock NFT use the same `PAYMENT_MODE` variable!**

---

**Questions? Check the logs or test the endpoints directly!**

```bash
# Test NFT status
curl http://localhost:8000/api/nft/status/YOUR_WALLET

# Test NFT verification
curl -X POST -H "Content-Type: application/json" \
  -d '{"wallet_address":"YOUR_WALLET"}' \
  http://localhost:8000/api/nft/verify
```

**Happy Testing! 🎨**

