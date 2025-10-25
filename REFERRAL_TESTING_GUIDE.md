# Referral System Testing Guide

## Current Implementation Status

### ✅ Completed
1. **User gets initial 2 free questions** - Working
2. **Referral code generation** - Email input creates `billionsbounty.com/{email_prefix}` codes
3. **Referral button appears** - Shows after 2 free questions are used
4. **Email collection** - Both payment and referral flows collect email
5. **IP address restriction** - Prevents multiple wallets from same IP
6. **Referral code persistence** - Existing codes are remembered

### 🔄 Partially Implemented
1. **Referral code usage** - Backend endpoint exists but needs:
   - Email collection on referral link click
   - Automatic crediting of 5 questions to both users
   - Proper state updates

### ❌ Not Yet Implemented
1. **URL parameter detection** - Referral codes passed via `?ref=` parameter
2. **Landing page email collection** - When user clicks referral link
3. **Automatic question crediting** - When referral code is used
4. **Sender receives questions** - When someone uses their code

## Testing the Current System

### Test 1: Basic Free Questions
1. Connect wallet on bounty page
2. Should have 2 free questions
3. Ask 2 questions
4. Should see "Refer Someone" button appear

### Test 2: Generate Referral Code
1. Click "Refer Someone" button
2. Enter email (e.g., `test@example.com`)
3. Should generate code: `billionsbounty.com/test`
4. Copy the code

### Test 3: Use Referral Code (Manual Testing Needed)
Currently requires manual testing via API:

```bash
curl -X POST http://localhost:8000/api/referral/use-code \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "RECEIVER_WALLET_ADDRESS",
    "referral_code": "billionsbounty.com/test"
  }'
```

## What Needs to Be Implemented

### Frontend Changes Needed

1. **Add URL Parameter Detection in Bounty Page**
```typescript
// In page.tsx
const searchParams = useSearchParams()
const referralCode = searchParams.get('ref')
```

2. **Show Email Collection Box**
```typescript
{referralCode && !referralProcessed && (
  <div className="email-collection-box">
    <h3>You've been referred! Enter email to claim 5 free questions</h3>
    <input type="email" />
    <button>Claim Questions</button>
  </div>
)}
```

3. **Update BountyChatInterface**
```typescript
// When questions are used up, show:
- "Pay $10" button
- "Refer Someone" button
```

### Backend Changes Needed

1. **Update `/api/referral/use-code` endpoint**
   - Accept email parameter
   - Give 5 questions to receiver
   - Find sender's wallet by email
   - Give 5 questions to sender
   - Return success with question counts

2. **Email to Wallet Lookup**
   - Query `FreeQuestionUsage` table
   - Find record with matching email prefix
   - Return wallet address of referrer

## Testing Plan

### Scenario 1: New User with Referral
1. User A generates referral code
2. User B clicks referral link: `http://localhost:3000/bounty/1?ref=billionsbounty.com/test`
3. User B sees email collection box
4. User B enters email and clicks "Claim"
5. Both users get 5 questions
6. User B can ask 5 questions
7. After 5 questions, User B sees "Pay $10" or "Refer Someone"

### Scenario 2: Referral Chain
1. User A refers User B
2. User B uses questions, then refers User C
3. User C gets 5 questions from B
4. User B gets 5 bonus questions from C
5. All questions count down properly

## Manual Testing Commands

```bash
# 1. Check User A's questions
curl http://localhost:8000/api/free-questions/USER_A_WALLET

# 2. Check User B's questions (before referral)
curl http://localhost:8000/api/free-questions/USER_B_WALLET

# 3. Use referral code (manually)
curl -X POST http://localhost:8000/api/referral/use-code \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "USER_B_WALLET",
    "referral_code": "billionsbounty.com/test"
  }'

# 4. Check User A's questions (should have 5 more)
curl http://localhost:8000/api/free-questions/USER_A_WALLET

# 5. Check User B's questions (should have 7: 2 original + 5 referral)
curl http://localhost:8000/api/free-questions/USER_B_WALLET
```

## Next Steps

1. ✅ Finish frontend URL parameter detection
2. ✅ Add email collection UI to bounty page
3. ✅ Update backend to handle referral email + automatic crediting
4. ✅ Test full referral flow end-to-end
5. ✅ Verify sender receives questions
6. ✅ Test edge cases (same email, expired codes, etc.)

## Notes

- The backend endpoint `/api/referral/use-code` currently exists but needs modification to accept email and credit both users
- The email collection UI needs to be added to the bounty page for when referral codes are detected
- IP restrictions prevent abuse but may need adjustment for legitimate use cases
