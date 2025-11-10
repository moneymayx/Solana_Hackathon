# What is a KYC Attestation?

## 🎯 Quick Answer

A **KYC Attestation** is a verifiable, on-chain record that proves a wallet address has completed Know Your Customer (KYC) verification, **without sharing the user's personal information** with you.

Think of it like a driver's license that's stored on the blockchain: You can verify it's valid without seeing the person's name, address, or photo.

---

## 📚 Breaking It Down

### Part 1: What is KYC?

**KYC = "Know Your Customer"**

It's a legal requirement for financial services to verify:
- ✅ Identity: Who is this person?
- ✅ Location: Where are they from?
- ✅ Legality: Are they allowed to use this service?

**Traditional KYC Process:**
```
1. User provides: Name, Address, Date of Birth, ID Number
2. User uploads: ID Document, Selfie
3. Third-party (MoonPay, etc.) verifies:
   - Documents are real
   - Person matches photo
   - Person is in allowed country
4. Result: "Verified" or "Not Verified"
```

**Problem**: This requires sharing personal data, is expensive ($20-50 per verification), and is slow (10-15 minutes).

---

### Part 2: What is an Attestation?

An **Attestation** is a **verifiable claim** stored on the blockchain.

Think of it like a digital certificate or badge that says:
- ✅ "This wallet belongs to a verified person"
- ✅ "This person is from the United States"
- ✅ "This person is an accredited investor"
- ✅ "This person is 18+ years old"

**Key Features:**
- 🔒 **Privacy-Preserving**: The claim is verified, but personal details aren't revealed
- 🔗 **On-Chain**: Stored permanently on Solana blockchain
- ✅ **Reusable**: Once verified, works across any platform
- 🌐 **Decentralized**: No single company controls it

---

### Part 3: What is a KYC Attestation?

A **KYC Attestation** combines both:

> **A verifiable, on-chain record that proves a wallet address has completed KYC verification, without sharing personal information.**

---

## 🔍 How It Works (Step by Step)

### Step 1: User Gets Verified

```
User → Attestation Provider (e.g., Civic, Persona, etc.)
  ↓
User provides: Name, Address, ID, Documents
  ↓
Provider verifies: Identity, Location, Age
  ↓
Provider creates: Attestation record on-chain
  ↓
Attestation links: Wallet Address ↔ "Verified Person"
```

**What's stored on-chain:**
```
Wallet: ABC123...
Attestation Type: KYC
Status: Verified
Provider: Civic
Timestamp: 2025-01-01
Signature: [cryptographic proof]
```

**What's NOT stored:**
```
❌ User's name
❌ User's address  
❌ User's ID number
❌ User's photo
```

Only the **claim** is stored, not the **data**.

---

### Step 2: Your Platform Checks Verification

When a user wants to use your platform:

```python
# Your code (using Attestations SDK)
result = await attestations_service.verify_kyc_attestation(
    wallet_address="ABC123..."
)

# Response:
{
    "success": True,
    "wallet_address": "ABC123...",
    "kyc_verified": True,  # ✅ User is verified
    "attestation_account": "XYZ789...",  # On-chain attestation account
    "provider": "attestations"  # Which system verified
}
```

**What happens behind the scenes:**
1. ✅ SDK queries Solana blockchain
2. ✅ Finds attestation account for that wallet
3. ✅ Verifies attestation is valid (cryptographic proof)
4. ✅ Returns: "Yes, this wallet is verified" or "No, not verified"

**You never see:**
- User's personal information
- Where they're from (unless you check geographic attestation)
- Any private data

You only see: ✅ "Verified" or ❌ "Not Verified"

---

## 🆚 KYC Attestation vs. Traditional KYC

### Traditional KYC (MoonPay, etc.)

```
┌─────────────────────────────────────┐
│ Your Platform                        │
│                                      │
│ "User wants to pay"                 │
│ → Redirects to MoonPay               │
│                                      │
│ ┌───────────────────────────────┐  │
│ │ MoonPay (External)             │  │
│ │ • User enters: Name            │  │
│ │ • User enters: Address        │  │
│ │ • User enters: ID Number      │  │
│ │ • User uploads: ID Photo      │  │
│ │ • User uploads: Selfie        │  │
│ │                                │  │
│ │ MoonPay has ALL user data     │  │
│ │ You pay: $20-50 per user      │  │
│ │ Time: 10-15 minutes           │  │
│ └───────────────────────────────┘  │
│                                      │
│ ← User returns (maybe)               │
│ ← MoonPay sends you: "Verified"     │
│                                      │
│ You now have user's personal data   │
│ (privacy/compliance concerns)       │
└─────────────────────────────────────┘
```

**Problems:**
- ❌ Slow (10-15 minutes)
- ❌ Expensive ($20-50 per user)
- ❌ Privacy concerns (third-party has all data)
- ❌ Not reusable (must verify again on each platform)
- ❌ User leaves your platform

---

### KYC Attestation (Attestations SDK)

```
┌─────────────────────────────────────┐
│ Your Platform                        │
│                                      │
│ "User wants to pay"                 │
│ → Queries blockchain: "Is wallet    │
│    ABC123... verified?"              │
│                                      │
│ Blockchain Response:                  │
│ ✅ "Yes, verified by Civic"         │
│                                      │
│ → User can proceed                   │
│                                      │
│ Time: < 1 second                     │
│ Cost: $0 (just a query)              │
│ Privacy: No personal data shared     │
└─────────────────────────────────────┘
```

**Benefits:**
- ✅ Instant (< 1 second)
- ✅ Free ($0)
- ✅ Privacy-preserving (no personal data)
- ✅ Reusable (works on any platform)
- ✅ User stays on your platform

---

## 🏗️ Technical Details

### How It's Stored on Solana

**Attestation Account Structure:**
```
Account: [Program Derived Address (PDA)]
├── Wallet Address: ABC123...
├── Credential Type: "KYC"
├── Schema: "identity_verification"
├── Provider: "Civic" (or other)
├── Status: "verified"
├── Timestamp: 2025-01-01 12:00:00
└── Signature: [cryptographic proof]
```

**Storage:**
- Stored on Solana blockchain
- Accessible via RPC query
- Cannot be forged (cryptographic signatures)
- Permanent (unless revoked by provider)

---

### How Verification Works

```python
# Simplified flow
def verify_kyc_attestation(wallet_address):
    # 1. Derive PDA (Program Derived Address) for this wallet's attestation
    pda = derive_attestation_address(wallet_address, "KYC")
    
    # 2. Query blockchain for attestation account
    account_data = query_blockchain(pda)
    
    # 3. Check if account exists (user is verified)
    if account_data exists:
        # 4. Verify cryptographic signature (attestation is valid)
        if signature_is_valid(account_data):
            return "✅ Verified"
        else:
            return "❌ Invalid attestation"
    else:
        return "❌ No attestation found"
```

**Key Points:**
- ✅ **On-chain**: Query Solana blockchain directly
- ✅ **Cryptographic**: Uses digital signatures (can't be faked)
- ✅ **Fast**: Single blockchain query (< 1 second)
- ✅ **Free**: No cost to query (just RPC call)

---

## 💡 Real-World Analogy

Think of a **KYC Attestation** like a **driver's license stored on the blockchain**:

### Traditional KYC (Driver's License Check)
```
Cop: "Can I see your driver's license?"
You: *Hands over physical license*
Cop: *Reads: Name, Address, DOB, License Number*
Cop: "Okay, you're verified to drive."
Cop: Now has ALL your personal information
```

### KYC Attestation (Blockchain License)
```
Platform: "Is this wallet verified?"
Blockchain: *Checks on-chain attestation*
Blockchain: "✅ Yes, wallet ABC123... is verified by Civic"
Platform: "Great, user can proceed."
Platform: Doesn't know name, address, or any personal info
```

**Benefits:**
- You can verify the license is valid
- You don't see personal information
- User keeps privacy
- Works across platforms (reusable)

---

## 🌍 Types of Attestations

The Attestations SDK supports various types:

### 1. KYC Attestation
```
Wallet: ABC123...
Attestation: "Identity Verified"
Use Case: Proves user is a real person
```

### 2. Geographic Attestation
```
Wallet: ABC123...
Attestation: "Located in United States"
Use Case: Restrict by country (compliance)
```

### 3. Accreditation Attestation
```
Wallet: ABC123...
Attestation: "Accredited Investor"
Use Case: Access to investment products
```

### 4. Age Verification Attestation
```
Wallet: ABC123...
Attestation: "18+ Years Old"
Use Case: Age-restricted services
```

**All work the same way**: On-chain, privacy-preserving, verifiable claims.

---

## 🔐 Privacy & Security

### What's Private

**You DON'T see:**
- ❌ User's name
- ❌ User's address
- ❌ User's ID number
- ❌ User's photo
- ❌ User's documents

**You DO see:**
- ✅ Wallet address
- ✅ Verification status (Yes/No)
- ✅ Provider (who verified them)
- ✅ Timestamp (when verified)

### How It's Secure

**Cryptographic Security:**
- Attestations use digital signatures
- Cannot be forged or tampered with
- Verifiable by anyone (transparent)
- Permanent (stored on blockchain)

**Privacy by Design:**
- Personal data never shared
- Only verification status revealed
- User controls their data
- Complies with privacy regulations

---

## 💰 Cost Comparison

### Traditional KYC (MoonPay, etc.)

| Component | Cost | Who Pays |
|-----------|------|----------|
| KYC Verification | $20-50 | You (per user) |
| Re-verification | $20-50 | You (if session expires) |
| **Total** | **$20-50 per user** | You |

### KYC Attestation (Attestations SDK)

| Component | Cost | Who Pays |
|-----------|------|----------|
| Query Blockchain | $0 | Free |
| First-Time Attestation | ~$0.001 | User (one-time, reusable) |
| **Total** | **$0-0.001 per user** | User (or subsidized) |

**Savings**: $20-50 per user (99%+ reduction)

---

## ✅ Benefits Summary

### For Users:

✅ **Privacy**: Don't share personal info with every platform
✅ **Speed**: Instant verification (< 1 second)
✅ **Reusable**: One attestation works everywhere
✅ **Control**: User owns their verification status

### For Your Platform:

✅ **Cost**: $0 vs $20-50 per user
✅ **Speed**: Instant vs 10-15 minutes
✅ **Privacy**: No personal data collection (compliance friendly)
✅ **Scalability**: Works for unlimited users

---

## 🚀 How to Use It (In Your Code)

### Check if User Has KYC Attestation

```python
from src.services.sdk.attestations_service import attestations_service

# Check KYC
result = await attestations_service.verify_kyc_attestation(
    wallet_address="ABC123..."
)

if result.get("kyc_verified"):
    # ✅ User is verified - allow payment
    allow_payment()
else:
    # ❌ User not verified - show message
    show_message("Get verified at [provider link]")
```

### Check Geographic Restrictions

```python
# Check if user is in allowed country
result = await attestations_service.verify_geographic_attestation(
    wallet_address="ABC123...",
    allowed_countries=["US", "CA", "GB"]
)

if result.get("country_verified"):
    # ✅ User is in allowed country
    allow_access()
else:
    # ❌ User not in allowed country
    show_restriction_message()
```

---

## 📝 Summary

**KYC Attestation** = **Verifiable, on-chain proof that a wallet is KYC-verified, without revealing personal information**

**Key Points:**
- ✅ Stored on Solana blockchain
- ✅ Privacy-preserving (no personal data shared)
- ✅ Instant verification (< 1 second)
- ✅ Free to query ($0)
- ✅ Reusable across platforms
- ✅ Cryptographically secure

**Think of it as**: A blockchain driver's license that proves you're verified without showing your personal details.

---

**This is what enables the instant, free KYC checks in your payment flow!** 🚀

