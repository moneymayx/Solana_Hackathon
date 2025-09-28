# Exchange Address Configuration Guide

## Current Status

**⚠️ IMPORTANT**: Most exchange addresses in the system are currently **PLACEHOLDERS** and need to be replaced with real addresses.

### Real Addresses (Verified)
- **Binance**: `9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM`, `5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9`

### Placeholder Addresses (Need Real Ones)
- **Coinbase**: Currently using placeholder addresses
- **Kraken**: Currently using placeholder addresses  
- **Bybit**: Currently using placeholder addresses
- **Robinhood**: Currently using placeholder addresses
- **Moonshot**: Currently using placeholder addresses
- **Crypto.com**: Currently using placeholder addresses
- **Gemini**: Currently using placeholder addresses
- **MEXC**: Currently using placeholder addresses

## How to Obtain Real Exchange Addresses

### Method 1: Exchange Support
Contact each exchange's support team directly:
- **Coinbase**: support.coinbase.com
- **Kraken**: support.kraken.com
- **Bybit**: support.bybit.com
- **Robinhood**: support.robinhood.com
- **Crypto.com**: support.crypto.com
- **Gemini**: support.gemini.com
- **MEXC**: support.mexc.com

### Method 2: Exchange Documentation
Check official exchange documentation for:
- Solana network support pages
- Deposit address lists
- API documentation
- Developer resources

### Method 3: Blockchain Analysis
1. **Solana Explorer**: Use solscan.io or solana.fm
2. **Search for known exchange transactions**: Look for large, regular transactions
3. **Cross-reference with exchange announcements**: Match addresses with official announcements

### Method 4: Community Resources
- **Solana Discord**: Check #exchanges channel
- **Reddit**: r/solana, r/cryptocurrency
- **Twitter**: Follow exchange official accounts for announcements

## Updating Exchange Addresses

### Using the API
```python
# Add new exchange addresses
winner_tracking_service.add_exchange_addresses("coinbase", [
    "RealCoinbaseAddress111111111111111111111111111111",
    "RealCoinbaseAddress222222222222222222222222222222"
])

# Remove old addresses
winner_tracking_service.remove_exchange_addresses("coinbase", [
    "CoinbaseWallet1111111111111111111111111111111"
])
```

### Direct Code Update
Edit `src/winner_tracking_service.py` and update the `known_exchanges` dictionary.

## Verification Process

### 1. Test with Known Transactions
- Send a small test transaction from the exchange
- Verify the address appears in the transaction
- Confirm it's not blacklisted by the system

### 2. Monitor Exchange Activity
- Watch for regular, large transactions
- Look for patterns typical of exchange operations
- Cross-reference with exchange announcements

### 3. Community Verification
- Ask in Solana community channels
- Check with other developers
- Verify against multiple sources

## Important Notes

### Address Format
- Solana addresses are 32-44 characters long
- Use base58 encoding
- Always verify address format before adding

### Security Considerations
- **Never use addresses from unofficial sources**
- **Always verify through multiple channels**
- **Test with small amounts first**
- **Keep addresses updated regularly**

### Maintenance
- Exchange addresses can change
- Set up monitoring for address updates
- Regular review of exchange announcements
- Community feedback integration

## Current Exchange List

```python
exchanges = [
    "binance",      # ✅ Has real addresses
    "coinbase",     # ❌ Needs real addresses
    "kraken",       # ❌ Needs real addresses
    "bybit",        # ❌ Needs real addresses
    "robinhood",    # ❌ Needs real addresses
    "moonshot",     # ❌ Needs real addresses
    "crypto_com",   # ❌ Needs real addresses
    "gemini",       # ❌ Needs real addresses
    "mexc"          # ❌ Needs real addresses
]
```

## Testing

After updating addresses, run the test suite:
```bash
python test_winner_tracking.py
```

This will verify that:
- Exchange addresses are properly recognized
- Legitimate exchange transactions are not blacklisted
- The system correctly distinguishes between exchange and non-exchange funding

## Support

If you need help obtaining real exchange addresses or have questions about the verification process, please:
1. Check the Solana community resources
2. Contact exchange support teams
3. Review this guide for additional methods
