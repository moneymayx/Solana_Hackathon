# User Experience Flow Documentation

## Overview

This document outlines the complete user experience flow for the Billions Bounty platform, covering authentication, payment processing, referral systems, and database tracking mechanisms.

## Table of Contents

1. [Authentication & Session Management](#authentication--session-management)
2. [Direct Access Flow](#direct-access-flow)
3. [Referral Flow](#referral-flow)
4. [Payment System](#payment-system)
5. [Database Tracking](#database-tracking)
6. [Security & Anti-Abuse](#security--anti-abuse)
7. [API Endpoints](#api-endpoints)

---

## Authentication & Session Management

### Hybrid Authentication System

The platform uses a strategic hybrid authentication approach that balances user acquisition with conversion:

- **Anonymous Access**: Users get 2 free questions without any registration
- **Session-Based Tracking**: Unique `session_id` stored in browser cookies for anonymous users
- **Email Authentication**: Required after 2 free questions to continue
- **Wallet Integration**: Optional Solana wallet connection for enhanced features
- **Device Fingerprinting**: IP address and user agent tracking for security
- **KYC Compliance**: Email signup enables MoonPay integration for payments

### User Record Structure

```python
class User:
    id: int                    # Primary key
    session_id: str           # Unique session identifier
    ip_address: str           # User's IP address
    user_agent: str           # Browser information
    created_at: datetime      # Account creation timestamp
    last_active: datetime     # Last activity timestamp
    total_attempts: int       # Number of interactions
    total_cost: float         # Total money spent
    is_active: bool           # Account status
    
    # Authentication fields
    email: str                # Required for registered users
    password_hash: str        # Password storage
    is_verified: bool         # Email verification status
    
    # Free question tracking
    anonymous_free_questions_used: int      # 0-2 for anonymous users
    has_used_anonymous_questions: bool      # Prevents return anonymous access
    
    # Wallet integration fields
    wallet_address: str       # Connected Solana wallet
    wallet_connected_at: datetime  # Wallet connection time
    wallet_signature: str     # Wallet signature for verification
    display_name: str         # Optional display name
    
    # KYC fields (for MoonPay compliance)
    full_name: str            # From KYC verification
    date_of_birth: datetime   # From KYC verification
    phone_number: str         # From KYC verification
    address: str              # From KYC verification
    kyc_status: str           # pending, verified, rejected
    kyc_provider: str         # moonpay, manual
    kyc_reference_id: str     # MoonPay transaction ID
```

---

## Direct Access Flow

### Step 1: Initial Landing

1. **Age Verification**: Users must be 18+ to access the platform
2. **Research Consent**: Users agree to participate in AI security research
3. **Session Creation**: System generates unique session ID and creates anonymous user record
4. **Cookie Storage**: Session ID stored in browser cookies for persistence

### Step 2: Anonymous Free Questions

1. **2 Free Questions**: Users can ask 2 questions without any registration
2. **Question Tracking**: System tracks `anonymous_free_questions_used` and `has_used_anonymous_questions`
3. **No Payment Required**: Questions are completely free for anonymous users
4. **Session Persistence**: Questions tracked across browser sessions

### Step 3: Signup Gate

1. **Signup Required**: After 2 free questions, user must create account
2. **Email Registration**: User provides email and password
3. **Referral Prompt**: "Before you pay, share your referral link to get 5 free questions per signup"
4. **Account Creation**: System creates registered user account

### Step 4: Wallet Connection (Optional)

1. **Wallet Detection**: System detects available Solana wallets (Phantom, etc.)
2. **Connection Request**: User can connect their wallet for enhanced features
3. **Blacklist Check**: System verifies wallet isn't blacklisted due to previous wins
4. **Database Update**: Wallet address stored in user record

### Step 5: Payment Processing

1. **Entry Fee**: $10 USD required for each interaction after free questions
2. **Payment Methods**:
   - **MoonPay Integration**: Apple Pay/PayPal → USDC conversion (requires KYC)
   - **Direct Wallet Payment**: USDC transfer to smart contract
3. **Fund Distribution**: $8 to research fund, $2 to operational costs

### Step 6: Return User Logic

1. **Anonymous Return**: If user returns after using anonymous questions, they see notification
2. **Options**: Sign up, refer people, or pay for questions
3. **No More Anonymous Access**: System prevents additional anonymous questions

---

## Referral Flow

### Step 1: Referral Code Detection

1. **URL Parameter**: User visits with `?ref=REFCODE` parameter
2. **Code Validation**: System validates referral code exists and is active
3. **Signup Required**: Referred users must create account before getting free questions
4. **Relationship Tracking**: Referral relationship stored in database

### Step 2: Referral Processing

1. **Signup with Referral**: User creates account with referral code
2. **Dual Benefits**: Both referrer and referee get 5 free questions
3. **Database Records**: Referral relationship and free question allocation tracked
4. **Prevention**: Users can't be referred multiple times

### Step 3: Free Question Usage

1. **Question Tracking**: System tracks remaining free questions from referrals
2. **Automatic Deduction**: Each interaction consumes one free question
3. **Payment Transition**: After free questions exhausted, normal $10 payment required
4. **More Referrals**: Only way to get more free questions is to refer others

### Step 4: Referral Restrictions

1. **One-Time Referral**: Users can only be referred once
2. **Signup Required**: Must have account to receive referral benefits
3. **Referrer Rewards**: 5 free questions per successful referral
4. **Viral Growth**: Encourages users to share referral links

### Referral Database Structure

```python
class ReferralCode:
    id: int
    user_id: int                    # Referrer's user ID
    referral_code: str              # Unique 6-character code
    created_at: datetime
    is_active: bool
    total_uses: int                 # Number of successful referrals
    total_free_questions_earned: int

class Referral:
    id: int
    referrer_id: int               # Who made the referral
    referee_id: int                # Who was referred
    referral_code_id: int          # Which code was used
    created_at: datetime
    is_valid: bool

class FreeQuestions:
    id: int
    user_id: int
    free_questions_remaining: int
    total_earned: int
    last_used: datetime
```

---

## Payment System

### MoonPay Integration

**Purpose**: Convert fiat currency (USD) to USDC cryptocurrency

```python
def create_buy_url(
    currency_code: str,           # "usdc_sol" (USDC on Solana)
    base_currency_amount: float,  # $10.00 USD
    wallet_address: str,          # User's wallet address
    payment_methods: list         # ["apple_pay", "paypal"]
) -> dict:
    # Returns MoonPay payment URL
    # USDC sent directly to user's wallet
```

**Features**:
- Apple Pay and PayPal support
- Direct USDC delivery to user's wallet
- No credit card manual entry
- Secure webhook verification

### Smart Contract Integration

**Purpose**: Process USDC payments for platform access

```rust
pub fn process_entry_payment(
    entry_amount: u64,        // $10 USDC
    user_wallet: Pubkey,      // User's wallet address
) -> Result<()> {
    // $8 goes to research fund
    // $2 goes to operational costs
    // Funds locked until interaction complete
}
```

### Payment Transaction Tracking

```python
class PaymentTransaction:
    id: int
    user_id: int
    payment_method: str           # 'wallet' or 'moonpay'
    payment_type: str             # 'query_payment' or 'deposit'
    amount_usd: float
    amount_crypto: float
    crypto_currency: str          # 'USDC'
    tx_signature: str             # Blockchain transaction hash
    moonpay_tx_id: str            # MoonPay transaction ID
    status: str                   # pending, confirmed, failed
    from_wallet: str
    to_wallet: str
    created_at: datetime
    confirmed_at: datetime
```

---

## Database Tracking

### User Activity Tracking

The system maintains comprehensive records of user behavior:

1. **Session Management**: Unique session IDs with IP and user agent tracking
2. **Wallet Connections**: Solana wallet addresses and connection timestamps
3. **Payment History**: All transactions with blockchain verification
4. **Interaction Logs**: Chat messages and AI responses
5. **Referral Activity**: Referral codes, uses, and free question allocations

### Conversation Tracking

```python
class Conversation:
    id: int
    user_id: int
    message_type: str             # 'user' or 'assistant'
    content: str                  # Message content
    model_used: str               # AI model used
    tokens_used: int              # Token consumption
    created_at: datetime
```

### Attack Attempt Tracking

```python
class AttackAttempt:
    id: int
    user_id: int
    attempt_type: str             # 'potential_manipulation', 'successful_manipulation'
    message_content: str
    ai_response: str
    success: bool
    threat_score: float
    additional_data: str          # JSON metadata
    created_at: datetime
```

---

## Security & Anti-Abuse

### Winner Tracking System

**Purpose**: Prevent users from creating multiple accounts after winning

1. **Wallet Blacklisting**: Winner wallets and connected wallets are blacklisted
2. **Connection Analysis**: System tracks wallet funding sources and transfers
3. **Prevention**: Blacklisted wallets cannot create new accounts

```python
class Winner:
    id: int
    user_id: int
    wallet_address: str
    prize_amount: float
    token: str
    transaction_hash: str
    created_at: datetime

class ConnectedWallet:
    id: int
    winner_id: int
    wallet_address: str
    connection_type: str          # 'direct_transfer', 'funding_source'
    is_blacklisted: bool
    discovered_at: datetime
```

### Rate Limiting

1. **Transfer Cooldown**: 1-minute cooldown between transfers per user
2. **Session Monitoring**: IP and user agent tracking for suspicious activity
3. **Blacklist Detection**: Phrase-based blacklisting system

### Security Events

```python
class SecurityEvent:
    id: int
    user_id: int
    event_type: str               # 'phrase_blacklisted', 'suspicious_activity'
    severity: str                 # 'low', 'medium', 'high', 'critical'
    description: str
    additional_data: str          # JSON metadata
    created_at: datetime
```

---

## Free Question System

### Anonymous Free Questions

**Purpose**: Reduce friction for new users while encouraging signups

- **2 Free Questions**: Anonymous users get exactly 2 questions without registration
- **Session Tracking**: Questions tracked via `anonymous_free_questions_used` and `has_used_anonymous_questions`
- **One-Time Access**: Users can't get additional anonymous questions after using their 2
- **Signup Gate**: After 2 questions, user must create account to continue

### Referral Free Questions

**Purpose**: Drive viral growth through referral rewards

- **5 Free Questions**: Both referrer and referee get 5 questions per successful referral
- **Signup Required**: Must have account to receive referral benefits
- **One-Time Referral**: Users can only be referred once
- **Referrer Rewards**: 5 free questions for each person who uses your referral code

### Free Question Database Structure

```python
class FreeQuestions:
    id: int
    user_id: int
    source: str                  # 'referral_bonus', 'referral_signup', 'anonymous'
    referral_id: int             # Links to specific referral
    questions_earned: int        # 5 for referrals, 2 for anonymous
    questions_used: int          # Questions consumed
    questions_remaining: int     # Available questions
    created_at: datetime
    last_used: datetime
    expires_at: datetime         # Optional expiration
```

### Business Logic

1. **Anonymous Users**: 2 questions maximum, tracked per session
2. **Referral Users**: 5 questions per successful referral
3. **Referrer Rewards**: 5 questions when someone uses their code
4. **Prevention**: Users can't be referred multiple times
5. **Conversion**: Free questions encourage signups and referrals

---

## API Endpoints

### Authentication Endpoints

- `POST /api/auth/signup` - User registration with optional referral code
- `POST /api/auth/login` - User login
- `POST /api/wallet/connect` - Connect Solana wallet
- `GET /api/user/profile/{wallet_address}` - Get user profile
- `GET /api/user/eligibility` - Get user's question eligibility status
- `GET /api/conversation/history` - Get conversation history

### Payment Endpoints

- `POST /api/payment/create` - Create payment request
- `POST /api/payment/verify` - Verify transaction
- `POST /api/moonpay/webhook` - MoonPay webhook handler
- `GET /api/transaction/status/{tx_id}` - Get transaction status

### Referral Endpoints

- `GET /api/referral/code/{user_id}` - Get user's referral code
- `POST /api/referral/process` - Process referral signup
- `GET /api/referral/stats/{user_id}` - Get referral statistics

### Bounty/Research Endpoints

- `GET /api/bounty/status` - Get current research fund status
- `POST /api/chat` - Send message to AI agent
- `GET /api/prize-pool` - Get prize pool information

---

## Key User Experience Principles

1. **No Registration Required**: Users can start immediately with session tracking
2. **Optional Wallet Connection**: Enhanced features available but not mandatory
3. **Referral Benefits**: Free questions for both referrer and referee
4. **Transparent Payments**: Clear breakdown of $10 entry fee allocation
5. **Session Persistence**: Users can return using same session ID
6. **Comprehensive Tracking**: All activities logged for research purposes
7. **Security Focus**: Anti-abuse measures prevent system exploitation
8. **Research Orientation**: Platform designed for AI security research

---

## Technical Implementation Notes

- **Database**: SQLAlchemy with async support
- **Blockchain**: Solana integration for USDC transactions
- **Payments**: MoonPay for fiat-to-crypto conversion
- **Session Management**: Cookie-based with database persistence
- **Security**: Multi-layered approach with wallet blacklisting
- **Tracking**: Comprehensive logging for research analysis

This documentation provides a complete overview of the user experience flow without including game mechanics or AI personality details.
