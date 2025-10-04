# Obsolete Backend Services

This directory contains backend services that have been **FULLY REPLACED** by smart contract functionality.

## ⚠️ **DO NOT USE** - These services are obsolete

### `fund_routing_service.py` - ❌ OBSOLETE
**Original Purpose**: Automated fund routing from deposit wallet to jackpot wallet

**Replaced By**: Smart contract `process_entry_payment` function
- Funds are now automatically locked in smart contract
- No manual fund routing needed
- Autonomous fund management

**Migration Status**: ✅ **COMPLETE** - All functionality moved to smart contract

### `bounty_service.py` - ❌ OBSOLETE  
**Original Purpose**: Research fund management and lottery logic

**Replaced By**: Smart contract lottery system
- Research fund floor ($10,000) enforced by smart contract
- Entry fee processing handled by smart contract
- Fund distribution (80% research, 20% operational) automated
- Rollover logic implemented in smart contract

**Migration Status**: ✅ **COMPLETE** - All functionality moved to smart contract

## What Changed

### Before (Backend-Controlled):
- Backend services managed fund transfers
- Manual fund routing between wallets
- Backend-controlled lottery logic
- Centralized fund management

### After (Smart Contract-Controlled):
- Smart contract handles all fund transfers
- Automatic fund locking on entry
- Autonomous lottery operations
- Decentralized fund management

## Current Architecture

### ✅ **Active Backend Services:**
- `smart_contract_service.py` - Interface to smart contract
- `ai_decision_integration.py` - AI decision processing
- `payment_flow_service.py` - MoonPay integration (simplified)
- `wallet_service.py` - Wallet connection
- `ai_agent.py` - AI personality
- `database.py` - Database management

### ✅ **Smart Contract Functions:**
- `initialize_lottery` - Initialize lottery system
- `process_entry_payment` - Process entry and lock funds
- `select_winner` - Select winner autonomously
- `process_ai_decision` - Process AI decisions and payouts
- `emergency_recovery` - Emergency fund recovery

## Benefits of Migration

1. **Autonomous Operations**: No human intervention needed
2. **Tamper-Proof**: Smart contract logic cannot be manipulated
3. **Transparent**: All operations are on-chain and verifiable
4. **Secure**: Funds are locked in smart contract
5. **Efficient**: No backend processing for fund management

## Cleanup Recommendations

These files can be safely deleted after confirming all functionality is working:

```bash
# After thorough testing, these can be removed:
rm src/obsolete/fund_routing_service.py
rm src/obsolete/bounty_service.py
```

## Notes

- All lottery functionality is now handled by the smart contract
- Backend services focus on AI processing and user interface
- Fund management is completely autonomous
- No manual intervention needed for lottery operations
