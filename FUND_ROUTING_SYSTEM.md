# Fund Routing System Documentation

## 🎯 Overview

The Billions project includes a comprehensive automated fund routing system that handles both MoonPay payments and direct wallet payments, ensuring proper fund segregation and automated processing.

## 🏗️ Architecture

### Fund Flow Design

```
MoonPay Payments:
User Payment (USD) → MoonPay → USDC → Deposit Wallet → Auto-Route → Jackpot Wallet

Direct Wallet Payments:
User USDC Payment → Jackpot Wallet (Direct)
```

### Wallet Configuration

- **Deposit Wallet**: Receives USDC from MoonPay payments
- **Jackpot Wallet**: Stores the actual prize pool funds  
- **Treasury Wallet**: Legacy compatibility (points to jackpot wallet)

## 🔧 Key Components

### 1. Fund Routing Service (`src/fund_routing_service.py`)

**Purpose**: Manages automated fund routing from deposit to jackpot wallet

**Key Features**:
- Automatic USDC SPL token transfers
- Payment completion processing
- Error handling and retry logic
- Manual override capabilities
- Comprehensive logging

**Main Methods**:
- `process_payment_completion()` - Process completed payments and route funds
- `_record_deposit()` - Record fund deposits in database
- `_route_funds()` - Route USDC from deposit to jackpot wallet
- `get_fund_status()` - Get current fund status and routing information
- `manual_route_funds()` - Manually trigger fund routing

### 2. Database Models

#### FundDeposit Model
```python
class FundDeposit(Base):
    __tablename__ = "fund_deposits"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    transaction_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    wallet_address: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    amount_usd: Mapped[float] = mapped_column(Float)
    amount_usdc: Mapped[float] = mapped_column(Float)
    payment_method: Mapped[str] = mapped_column(String(50))  # 'moonpay', 'wallet'
    deposit_wallet: Mapped[str] = mapped_column(String(255), nullable=False)
    target_wallet: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    routed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
```

#### FundTransfer Model
```python
class FundTransfer(Base):
    __tablename__ = "fund_transfers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    deposit_id: Mapped[int] = mapped_column(Integer, ForeignKey("fund_deposits.id"))
    from_wallet: Mapped[str] = mapped_column(String(255), nullable=False)
    to_wallet: Mapped[str] = mapped_column(String(255), nullable=False)
    amount_usdc: Mapped[float] = mapped_column(Float)
    transaction_signature: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
```

### 3. Enhanced MoonPay Integration

**Configuration**:
- **Currency Code**: `usdc_sol` (USDC on Solana)
- **Payment Methods**: Apple Pay, PayPal only
- **Credit Card**: Disabled
- **Target Wallet**: Deposit wallet address

**Key Changes**:
- MoonPay payments go to deposit wallet instead of user wallet
- Webhook triggers automatic fund routing
- USDC delivered directly (no manual conversion needed)

### 4. API Endpoints

#### Fund Management Endpoints

**GET /api/funds/status**
- Returns current fund status and routing information
- Shows deposit wallet, jackpot wallet, and recent activity

**POST /api/funds/route/{deposit_id}**
- Manually trigger fund routing for a specific deposit
- Admin override for failed automatic routing

**GET /api/funds/deposits**
- List all fund deposits with pagination
- Shows deposit details, amounts, and status

**GET /api/funds/transfers**
- List all fund transfers with pagination
- Shows transfer details and transaction signatures

## ⚙️ Configuration

### Environment Variables

```bash
# Fund Routing Configuration
DEPOSIT_WALLET_ADDRESS=your_deposit_wallet_address_here
JACKPOT_WALLET_ADDRESS=your_jackpot_wallet_address_here
DEPOSIT_WALLET_PRIVATE_KEY=your_deposit_wallet_private_key_here

# Fund Routing Settings
AUTO_FUND_ROUTING=true
MIN_ROUTING_AMOUNT=1.0
ROUTING_DELAY_SECONDS=30
```

### MoonPay Configuration

```bash
# MoonPay Settings
MOONPAY_API_KEY=your_moonpay_api_key
MOONPAY_SECRET_KEY=your_moonpay_secret_key
MOONPAY_WEBHOOK_URL=https://yourdomain.com/api/moonpay/webhook
```

## 🔄 Payment Processing Flow

### MoonPay Payments

1. **User Initiates Payment**
   - User selects Apple Pay or PayPal
   - Payment amount in USD

2. **MoonPay Processing**
   - MoonPay converts USD to USDC
   - USDC delivered to deposit wallet
   - Payment completion webhook sent

3. **Fund Routing**
   - Webhook triggers fund routing service
   - Automatic transfer from deposit to jackpot wallet
   - Payment recorded in database

4. **Completion**
   - Funds available in jackpot wallet
   - Prize pool updated
   - User can participate in bounty

### Direct Wallet Payments

1. **User Initiates Payment**
   - User connects wallet
   - Selects USDC payment

2. **Direct Transfer**
   - USDC transferred directly to jackpot wallet
   - No additional routing required

3. **Completion**
   - Payment recorded for tracking
   - Prize pool updated
   - User can participate in bounty

## 🛡️ Security Features

### Fund Segregation
- **Separate Wallets**: Clean separation between deposit and jackpot funds
- **Automated Routing**: No manual intervention required
- **Audit Trail**: Complete transaction history

### Error Handling
- **Retry Logic**: Automatic retry for failed transfers
- **Error Logging**: Comprehensive error tracking
- **Manual Override**: Admin can manually trigger routing

### Monitoring
- **Real-time Status**: API endpoints for fund monitoring
- **Transaction History**: Complete audit trail
- **Error Tracking**: Detailed error logging

## 🔧 Technical Implementation

### USDC SPL Token Support

**Token Standard**: SPL token program
**Mint Address**: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
**Decimals**: 6 (standard USDC precision)
**Transfer Method**: SPL token transfer instructions

### Database Schema

```sql
-- Fund deposits tracking
CREATE TABLE fund_deposits (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(255) NOT NULL,
    wallet_address VARCHAR(255) NOT NULL,
    amount_usd FLOAT NOT NULL,
    amount_usdc FLOAT NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    deposit_wallet VARCHAR(255) NOT NULL,
    target_wallet VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    routed_at TIMESTAMP NULL,
    extra_data TEXT
);

-- Fund transfers tracking
CREATE TABLE fund_transfers (
    id SERIAL PRIMARY KEY,
    deposit_id INTEGER REFERENCES fund_deposits(id),
    from_wallet VARCHAR(255) NOT NULL,
    to_wallet VARCHAR(255) NOT NULL,
    amount_usdc FLOAT NOT NULL,
    transaction_signature VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP NULL,
    error_message TEXT
);
```

## 📊 Monitoring & Management

### Fund Status Dashboard

**Real-time Information**:
- Deposit wallet balance
- Jackpot wallet balance
- Pending transfers count
- Recent activity log

**Admin Controls**:
- Manual fund routing
- Error resolution
- Status monitoring

### API Response Examples

#### Fund Status Response
```json
{
  "deposit_wallet": "ABC123...",
  "jackpot_wallet": "XYZ789...",
  "auto_routing_enabled": true,
  "recent_deposits": [
    {
      "id": 1,
      "amount_usdc": 100.0,
      "status": "routed",
      "created_at": "2024-12-19T10:30:00Z"
    }
  ],
  "pending_routing": 0,
  "pending_amount": 0.0,
  "total_recent_deposits": 100.0
}
```

#### Deposit List Response
```json
{
  "deposits": [
    {
      "id": 1,
      "transaction_id": "bounty_123_1703001000",
      "wallet_address": "ABC123...",
      "amount_usd": 100.0,
      "amount_usdc": 100.0,
      "payment_method": "moonpay",
      "status": "routed",
      "created_at": "2024-12-19T10:30:00Z",
      "routed_at": "2024-12-19T10:30:30Z"
    }
  ],
  "total": 1
}
```

## 🚀 Setup Instructions

### 1. Environment Configuration

Add the following to your `.env` file:

```bash
# Fund Routing Configuration
DEPOSIT_WALLET_ADDRESS=your_deposit_wallet_address_here
JACKPOT_WALLET_ADDRESS=your_jackpot_wallet_address_here
DEPOSIT_WALLET_PRIVATE_KEY=your_deposit_wallet_private_key_here

# Fund Routing Settings
AUTO_FUND_ROUTING=true
MIN_ROUTING_AMOUNT=1.0
ROUTING_DELAY_SECONDS=30
```

### 2. Database Migration

Run database migrations to create the fund routing tables:

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
alembic upgrade head
```

### 3. Testing

Test the fund routing system:

```bash
# Test fund status endpoint
curl http://localhost:8000/api/funds/status

# Test manual routing (replace {deposit_id} with actual ID)
curl -X POST http://localhost:8000/api/funds/route/1
```

## 🔍 Troubleshooting

### Common Issues

**1. Fund Routing Not Working**
- Check environment variables are set correctly
- Verify deposit wallet private key is valid
- Check database connection

**2. MoonPay Webhook Not Triggering**
- Verify webhook URL is correct
- Check MoonPay webhook configuration
- Verify webhook signature validation

**3. Database Errors**
- Run database migrations
- Check database connection
- Verify table creation

### Debug Mode

Enable debug logging by setting:

```bash
LOG_LEVEL=DEBUG
```

## 📈 Future Enhancements

### Planned Features
- **Multi-token Support**: Support for additional SPL tokens
- **Advanced Routing**: Smart routing based on wallet balances
- **Analytics**: Detailed fund flow analytics
- **Alerts**: Real-time notifications for fund events

### Scalability Considerations
- **Batch Processing**: Process multiple transfers efficiently
- **Rate Limiting**: Prevent excessive transfer attempts
- **Load Balancing**: Handle high-volume fund routing

## 📚 Related Documentation

- [Development Notes](DEVELOPMENT_NOTES.md) - Complete development context
- [Development Checklist](DEVELOPMENT_CHECKLIST.md) - Implementation checklist
- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [Database Schema](DATABASE_SCHEMA.md) - Database design documentation

---

**Last Updated**: December 19, 2024
**Version**: 1.0.0
**Status**: Production Ready
