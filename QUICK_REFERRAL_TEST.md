# Quick Referral System Test

## 🚀 Test Now

### Prerequisites
✅ Backend running on port 8000  
✅ Frontend starting on port 3000

### Test Flow

#### Step 1: Generate Referral Code (User A)
1. Open browser: http://localhost:3000
2. Go to any bounty: http://localhost:3000/bounty/1
3. Connect your Solana wallet
4. You'll have 2 free questions
5. Ask 2 questions (use them up)
6. Click "Refer Someone for 5 Free Questions"
7. Enter email: `test@example.com`
8. Copy the referral code: `billionsbounty.com/test`

#### Step 2: Share the Referral Link
Create this URL with your referral code:
```
http://localhost:3000/bounty/1?ref=billionsbounty.com/test
```

#### Step 3: Use Referral Code (User B)
1. Open a new browser window (or incognito)
2. Go to the referral link above
3. Connect a different wallet (or use a different browser)
4. You should see "🎁 You've been referred! Get 5 Free Questions" box below the chat
5. Enter your email address
6. Click "Claim 5 Questions"

#### Step 4: Verify
- User B should now have 7 questions total (2 initial + 5 referral)
- User A should receive 5 bonus questions
- Both users can continue chatting

### Expected Behavior

✅ **Referral code in URL** → Shows claim box  
✅ **Wallet connected** → Can enter email  
✅ **Email entered** → Can click claim button  
✅ **Claim successful** → Both users get 5 questions  
✅ **Page refreshes** → Shows updated question count  
✅ **After questions used** → Shows "Pay $10" and "Refer Someone" buttons  

### Troubleshooting

**Issue**: Referral box doesn't show
- Check URL has `?ref=` parameter
- Check frontend console for errors

**Issue**: Claim button disabled
- Make sure wallet is connected
- Make sure email is entered

**Issue**: Backend errors
- Check backend console on port 8000
- Verify backend restarted after code changes

**Issue**: Questions not updating
- Check network tab for API calls
- Verify API returns success response

## 🧪 Manual API Testing

### Test Backend Directly

```bash
# 1. Check User A's questions (before referral)
curl http://localhost:8000/api/free-questions/USER_A_WALLET

# 2. Check User B's questions (before referral)
curl http://localhost:8000/api/free-questions/USER_B_WALLET

# 3. Use referral code (User B uses User A's code)
curl -X POST http://localhost:8000/api/referral/use-code \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "USER_B_WALLET",
    "referral_code": "billionsbounty.com/test",
    "email": "userb@example.com"
  }'

# 4. Check User A's questions (should have 5 more)
curl http://localhost:8000/api/free-questions/USER_A_WALLET

# 5. Check User B's questions (should have 7 total)
curl http://localhost:8000/api/free-questions/USER_B_WALLET
```

## 📋 Success Criteria

- [ ] User A generates referral code
- [ ] User B clicks referral link
- [ ] Referral claim box appears
- [ ] Both users connect wallets
- [ ] Both users can claim questions
- [ ] Question counts update correctly
- [ ] Both users can continue chatting
- [ ] After questions exhausted, both buttons appear

## 🎯 What to Test Next

If everything works:
1. ✅ Referral flow is complete
2. Next: Test payment flow
3. Next: Test winner detection
4. Next: Test bounty pool updates

If something doesn't work:
1. Check browser console for errors
2. Check backend logs for errors
3. Verify database is connected
4. Test API endpoints manually
