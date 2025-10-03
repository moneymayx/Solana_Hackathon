# Payment Flow System Documentation

## 🎯 **Overview**

The Billions Bounty platform now uses a streamlined payment flow that eliminates private key storage while maintaining full autonomous operation. This new architecture provides enhanced security and simplified fund management.

## 🏗️ **Architecture Overview**

### **New Payment Flow**
```
User Payment Journey:
1. Connect Wallet → 2. Buy USDC (MoonPay) → 3. Pay Smart Contract → 4. Play Lottery
```

### **Key Components**
- **MoonPay Integration**: Fiat-to-crypto on-ramp (Apple Pay/PayPal → USDC)
- **Payment Flow Service**: Manages the complete payment process
- **Smart Contract Integration**: Direct USDC payments to lottery contract
- **No Private Keys**: System operates without storing any private keys

## 🔧 **Core Services**

### **1. Payment Flow Service (`src/payment_flow_service.py`)**

**Purpose**: Manages the complete payment flow from MoonPay to smart contract

**Key Methods**:
- `create_payment_request()` - Create MoonPay payment URL for USDC purchase
- `process_payment_completion()` - Handle completed MoonPay payments
- `process_lottery_entry_payment()` - Process lottery entry payments via smart contract

**Features**:
- Direct USDC delivery to user wallets
- Automatic lottery entry enablement
- Smart contract integration
- Comprehensive error handling

### **2. MoonPay Service (Updated)**

**Changes Made**:
- USDC sent directly to user's wallet (not deposit wallet)
- Eliminates need for fund routing service
- Simplified payment flow

**Configuration**:
```python
# MoonPay sends USDC directly to user
wallet_address=wallet_address,  # User's wallet, not deposit wallet
currency_code="usdc_sol",       # USDC on Solana
payment_methods=["apple_pay", "paypal"]  # No credit cards
```

### **3. Smart Contract Service**

**Integration**:
- Direct USDC payments from users
- Autonomous fund management
- No intermediate wallet routing

## 💳 **Payment Flow Details**

### **Step 1: User Initiates Payment**

```python
# User requests payment
POST /api/moonpay/create-payment
{
    "wallet_address": "user_wallet_address",
    "amount_usd": 10.0
}

# Response
{
    "success": true,
    "payment_url": "https://buy.moonpay.com/...",
    "transaction_id": "bounty_123_1703001000",
    "payment_methods": ["apple_pay", "paypal"]
}
```

### **Step 2: MoonPay Processing**

1. **User pays with Apple Pay/PayPal**
2. **MoonPay converts USD to USDC**
3. **USDC sent directly to user's wallet**
4. **Webhook notification sent to backend**

### **Step 3: Payment Completion**

```python
# Webhook processes payment
POST /api/moonpay/webhook
{
    "data": {
        "transaction_id": "bounty_123_1703001000",
        "wallet_address": "user_wallet_address",
        "base_currency_amount": 10.0,
        "quote_currency_amount": 10.0,
        "status": "completed"
    }
}

# System response
{
    "success": true,
    "message": "USDC sent to user wallet - lottery entry enabled",
    "lottery_enabled": true
}
```

### **Step 4: Lottery Entry Payment**

```python
# User pays lottery entry
POST /api/payment/create
{
    "payment_method": "wallet",
    "amount_usd": 10.0,
    "wallet_address": "user_wallet_address"
}

# Smart contract processes payment
{
    "success": true,
    "message": "Lottery entry processed successfully!",
    "transaction_signature": "abc123...",
    "funds_locked": true
}
```

## 🔐 **Security Benefits**

### **Eliminated Risks**
- ❌ **No Private Key Storage**: System doesn't store any private keys
- ❌ **No Fund Routing**: Eliminates intermediate wallet complexity
- ❌ **No Manual Transfers**: All payments handled by smart contracts

### **Enhanced Security**
- ✅ **User Control**: Users maintain control of their USDC until payment
- ✅ **Direct Payments**: No intermediate wallet vulnerabilities
- ✅ **Simplified Architecture**: Fewer attack vectors
- ✅ **Transparent Process**: All transactions on-chain

## 📊 **Database Schema**

### **Payment Transactions Table**
```sql
CREATE TABLE payment_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    payment_method VARCHAR(50) NOT NULL,  -- 'moonpay', 'wallet'
    payment_type VARCHAR(50) NOT NULL,    -- 'usdc_purchase', 'lottery_entry'
    amount_usd FLOAT NOT NULL,
    amount_crypto FLOAT NOT NULL,
    crypto_currency VARCHAR(10) NOT NULL, -- 'USDC'
    tx_signature VARCHAR(255),
    moonpay_tx_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    from_wallet VARCHAR(255),
    to_wallet VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP NULL,
    extra_data TEXT
);
```

## ⚙️ **Configuration**

### **Environment Variables (Updated)**

```bash
# Core API
ANTHROPIC_API_KEY=your_claude_api_key

# Database
DATABASE_URL=sqlite+aiosqlite:///./billions.db

# Solana Smart Contracts
SOLANA_RPC_ENDPOINT=https://api.mainnet-beta.solana.com
LOTTERY_PROGRAM_ID=DAgzfNPpc3i2EttgxfRtSN4SXQ4CwXQYjStmgrnw3BYh

# WalletConnect
WALLETCONNECT_PROJECT_ID=your_project_id

# MoonPay Integration
MOONPAY_API_KEY=your_moonpay_api_key
MOONPAY_SECRET_KEY=your_moonpay_secret_key
MOONPAY_BASE_URL=https://api.moonpay.com

# Frontend
FRONTEND_URL=http://localhost:3000
```

### **Removed Variables**
```bash
# These are no longer needed:
# DEPOSIT_WALLET_ADDRESS=  # ❌ Removed
# JACKPOT_WALLET_ADDRESS=  # ❌ Removed  
# DEPOSIT_WALLET_PRIVATE_KEY=  # ❌ Removed
# AUTO_FUND_ROUTING=  # ❌ Removed
# MIN_ROUTING_AMOUNT=  # ❌ Removed
# ROUTING_DELAY_SECONDS=  # ❌ Removed
```

## 🚀 **API Endpoints**

### **Payment Creation**
```bash
POST /api/moonpay/create-payment
# Creates MoonPay payment URL for USDC purchase

POST /api/payment/create
# Processes lottery entry payment via smart contract
```

### **Payment Processing**
```bash
POST /api/moonpay/webhook
# Handles MoonPay payment completion webhooks

POST /api/payment/verify
# Verifies payment transactions
```

### **Status & Monitoring**
```bash
GET /api/lottery/status
# Get current lottery status from smart contract

GET /api/payment/rates
# Get current exchange rates
```

## 🔄 **Migration from Fund Routing**

### **What Changed**
1. **Eliminated Fund Routing Service**: No longer needed
2. **Direct MoonPay Integration**: USDC sent to user wallets
3. **Simplified Payment Flow**: Fewer steps, more secure
4. **Removed Private Keys**: No private key storage required

### **Backward Compatibility**
- **Database**: Existing payment records preserved
- **API**: New endpoints added, old ones deprecated
- **Smart Contracts**: No changes to contract logic

## 📈 **Benefits Summary**

### **Security Improvements**
- **Eliminated Private Key Risk**: No private keys stored anywhere
- **Reduced Attack Surface**: Fewer components to secure
- **User Control**: Users maintain control of their funds

### **Operational Benefits**
- **Simplified Architecture**: Easier to maintain and debug
- **Cost Reduction**: No fund routing fees
- **Better UX**: Direct payments, fewer steps

### **Development Benefits**
- **Easier Testing**: Simpler payment flow
- **Better Monitoring**: Clear transaction paths
- **Reduced Complexity**: Fewer moving parts

## 🧪 **Testing**

### **Test Payment Flow**
```bash
# 1. Create payment request
curl -X POST "http://localhost:8000/api/moonpay/create-payment" \
     -H "Content-Type: application/json" \
     -d '{"wallet_address": "test_wallet", "amount_usd": 10.0}'

# 2. Simulate webhook (in test environment)
curl -X POST "http://localhost:8000/api/moonpay/webhook" \
     -H "Content-Type: application/json" \
     -d '{"data": {"status": "completed", "wallet_address": "test_wallet"}}'

# 3. Process lottery entry
curl -X POST "http://localhost:8000/api/payment/create" \
     -H "Content-Type: application/json" \
     -d '{"payment_method": "wallet", "amount_usd": 10.0, "wallet_address": "test_wallet"}'
```

## 📚 **Related Documentation**

- [Wallet Architecture & Fund Flow](WALLET_AND_FUND_FLOW.md) - Updated fund flow diagrams
- [Smart Contract Deployment](SMART_CONTRACT_DEPLOYMENT.md) - Contract deployment guide
- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [Security Guide](SECURITY_GUIDE.md) - Security best practices

---

**Last Updated**: December 19, 2024  
**Version**: 2.0.0  
**Status**: Production Ready  
**Migration**: Complete - Fund routing system removed
