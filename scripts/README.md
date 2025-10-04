# Scripts Organization

This directory contains organized scripts for the Billions Bounty project, categorized by their current status and purpose.

## Directory Structure

### `/obsolete/` - Scripts Replaced by Smart Contracts
These scripts are **NO LONGER NEEDED** as their functionality has been fully migrated to smart contracts:

- `initialize_lottery.py` - Lottery initialization (replaced by smart contract)
- `initialize_lottery_correct.py` - Corrected lottery initialization (replaced by smart contract)
- `test_entry_payment.py` - Entry payment testing (replaced by smart contract)
- `test_winner_selection.py` - Winner selection testing (replaced by smart contract)

**Status**: ❌ **OBSOLETE** - Functionality moved to smart contract

### `/testing/` - Active Testing Scripts
These scripts are still useful for testing the smart contract functionality:

- `test_comprehensive.py` - Comprehensive smart contract testing
- `test_simple.py` - Simple smart contract testing

**Status**: ✅ **ACTIVE** - Use for testing smart contract functionality

### `/utilities/` - Utility Scripts
General utility scripts that are still needed:

- (To be organized)

**Status**: ✅ **ACTIVE** - General utilities

### `/smart_contract/` - Smart Contract Management
Scripts for managing smart contract deployment and operations:

- (To be organized)

**Status**: ✅ **ACTIVE** - Smart contract management

## Migration Summary

### ✅ **Fully Migrated to Smart Contracts:**
1. **Lottery Initialization** - `initialize_lottery` function
2. **Entry Payment Processing** - `process_entry_payment` function
3. **Fund Locking** - Automatic fund locking
4. **Winner Selection** - `select_winner` function
5. **AI Decision Processing** - `process_ai_decision` function
6. **Fund Distribution** - 80% research fund, 20% operational fee
7. **Emergency Recovery** - `emergency_recovery` function

### 🔄 **Backend Services Status:**
- ✅ **KEEP**: `smart_contract_service.py` - Interface to smart contract
- ✅ **KEEP**: `ai_decision_integration.py` - AI decision processing
- ✅ **KEEP**: `payment_flow_service.py` - MoonPay integration (simplified)
- ✅ **KEEP**: `wallet_service.py` - Wallet connection
- ✅ **KEEP**: `ai_agent.py` - AI personality
- ✅ **KEEP**: `database.py` - Database management
- ❌ **OBSOLETE**: `fund_routing_service.py` - Moved to smart contract
- ❌ **OBSOLETE**: `bounty_service.py` - Moved to smart contract

## Usage

### For Testing Smart Contract:
```bash
cd scripts/testing
python test_comprehensive.py
python test_simple.py
```

### For Smart Contract Management:
```bash
cd scripts/smart_contract
# Use deployment and monitoring scripts
```

## Notes

- All lottery functionality is now handled by the smart contract
- Backend services now focus on AI processing, database management, and user interface
- Fund management is completely autonomous through smart contracts
- No manual fund transfers or lottery management needed
