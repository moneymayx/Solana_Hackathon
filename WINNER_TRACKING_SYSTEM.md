# Winner Tracking System

## Overview

The Winner Tracking System is a sophisticated anti-fraud mechanism designed to prevent jackpot winners from creating new wallets to continue playing the bounty. Once someone wins a jackpot, they and all wallets connected to them are permanently blacklisted from participating.

## Key Features

### 🏆 Winner Recording
- Automatically records all jackpot winners
- Stores wallet address, prize amount, token type, and transaction hash
- Activates tracking system after first jackpot win

### 🔗 Wallet Connection Tracking
- **Direct Transfers**: Tracks wallets that received funds from winner's wallet
- **Funding Source Analysis**: Identifies wallets funded by the same source as winners
- **Sender Connections**: Tracks wallets that sent funds to winners (potential accomplices)

### 🚫 Dynamic Blacklisting
- Winner's wallet is immediately blacklisted
- All connected wallets are automatically blacklisted
- New wallets sharing funding sources with winners are blacklisted
- Blacklist persists across all future attempts

### 🔍 Wallet Verification
- All wallet connections are verified before allowing participation
- Real-time blacklist checking during wallet connection
- Prevents blacklisted wallets from accessing the system

## Database Schema

### Winner Table
```sql
CREATE TABLE winners (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    wallet_address VARCHAR(255) NOT NULL,
    prize_amount FLOAT NOT NULL,
    token VARCHAR(10) NOT NULL,
    transaction_hash VARCHAR(255),
    won_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### ConnectedWallet Table
```sql
CREATE TABLE connected_wallets (
    id INTEGER PRIMARY KEY,
    winner_id INTEGER REFERENCES winners(id),
    wallet_address VARCHAR(255) NOT NULL,
    connection_type VARCHAR(50) NOT NULL,
    connection_details TEXT,
    discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_blacklisted BOOLEAN DEFAULT TRUE
);
```

### WalletFundingSource Table
```sql
CREATE TABLE wallet_funding_sources (
    id INTEGER PRIMARY KEY,
    wallet_address VARCHAR(255) NOT NULL,
    funding_source VARCHAR(255) NOT NULL,
    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_funding_amount FLOAT DEFAULT 0.0,
    transaction_count INTEGER DEFAULT 0
);
```

## API Endpoints

### Winner Management
- `GET /api/winners/list` - Get list of all winners
- `GET /api/winners/stats` - Get winner tracking statistics
- `GET /api/winners/connected-wallets/{winner_id}` - Get wallets connected to a winner

### Wallet Verification
- `POST /api/winners/check-wallet` - Check if wallet is blacklisted
- `POST /api/winners/record-funding` - Record wallet funding source

### System Control
- `POST /api/winners/activate-tracking` - Manually activate tracking (for testing)

## How It Works

### 1. Winner Detection
When a user wins a jackpot:
1. AI agent records the winner in the database
2. Winner tracking system is activated (if first win)
3. Winner's wallet is immediately blacklisted
4. System begins tracking wallet connections

### 2. Connection Tracking
The system tracks three types of connections:

#### Direct Transfers
- Monitors outgoing transactions from winner's wallet
- Identifies recipient addresses
- Adds them to connected wallets list

#### Funding Source Analysis
- Records where each wallet gets its funds
- Identifies wallets funded by same sources as winners
- Blacklists wallets with shared funding sources

#### Sender Connections
- Tracks incoming transactions to winner's wallet
- Identifies potential accomplices
- Adds sender wallets to blacklist

### 3. Wallet Verification
Before allowing any wallet to connect:
1. Check if wallet is a direct winner
2. Check if wallet is connected to any winner
3. Check if wallet shares funding sources with winners
4. Reject wallet if any connection is found

## Testing

### Test Script
Run the test script to verify the system works:

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
python test_winner_tracking.py
```

### Test Scenarios
1. **Initial State**: System starts inactive
2. **Winner Recording**: First winner activates system
3. **Direct Blacklisting**: Winner's wallet is blacklisted
4. **Funding Source Tracking**: Records wallet funding sources
5. **Shared Source Detection**: Blacklists wallets with shared funding
6. **Clean Wallet Verification**: Allows unrelated wallets

## Security Considerations

### Exchange Address Detection
The system includes known exchange addresses to identify centralized funding sources:
- Binance hot/cold wallets
- Coinbase addresses
- Kraken addresses
- FTX addresses

### Connection Types
- `direct_transfer`: Wallet received funds from winner
- `funding_source`: Wallet shares funding source with winner
- `exchange_connected`: Wallet funded by same exchange as winner

### False Positive Prevention
- Only blacklists wallets with clear connections to winners
- Maintains detailed connection logs for manual review
- Allows for manual pardon system (is_active flag)

## Production Deployment

### Activation
The system activates automatically after the first jackpot win. No manual intervention required.

### Monitoring
- Monitor `/api/winners/stats` for system health
- Check `/api/winners/list` for recent winners
- Review connected wallets for each winner

### Maintenance
- Regular cleanup of old funding source records
- Manual review of connection patterns
- Potential pardon system for false positives

## Example Usage

### Check if wallet is blacklisted
```python
import requests

response = requests.post("http://localhost:8000/api/winners/check-wallet", 
                        json={"wallet_address": "Wallet123456789"})
print(response.json())
# {"blacklisted": true, "reason": "Direct winner", "type": "winner"}
```

### Record wallet funding
```python
response = requests.post("http://localhost:8000/api/winners/record-funding",
                        json={
                            "wallet_address": "NewWallet987654321",
                            "funding_source": "ExchangeABC123",
                            "amount": 500.0
                        })
```

### Get winner statistics
```python
response = requests.get("http://localhost:8000/api/winners/stats")
print(response.json())
# {
#   "total_winners": 5,
#   "total_blacklisted_wallets": 23,
#   "recent_winners_30d": 3,
#   "total_prize_money": 50000.0,
#   "tracking_active": true
# }
```

## Future Enhancements

### Advanced Transaction Analysis
- Implement full Solana transaction history analysis
- Add support for more complex connection patterns
- Include cross-chain transaction tracking

### Machine Learning
- Use ML to detect suspicious wallet patterns
- Identify potential winner alt accounts
- Improve connection detection accuracy

### Real-time Monitoring
- WebSocket updates for new blacklisted wallets
- Real-time alerts for suspicious activity
- Dashboard for monitoring system health

## Conclusion

The Winner Tracking System provides a robust defense against winner fraud while maintaining a smooth user experience for legitimate players. The system is designed to be both effective and fair, with built-in mechanisms to prevent false positives and allow for manual review when necessary.
