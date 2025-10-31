# Contract V2 README - Build, Test, and Migration Guide

## Overview

This directory contains the enhanced smart contract implementation (v2) with Phase 1 and Phase 2 features:
- **Phase 1**: 4-way revenue split (60/20/10/10), per-bounty tracking, Ed25519 signature verification
- **Phase 2**: On-chain price escalation, buyback automation primitive, staking skeleton

The v2 contract is **isolated** from the existing v1 contract and will not break existing backend functionality.

---

## Directory Structure

```
programs/
├── billions-bounty/          # Existing v1 contract (unchanged)
└── billions-bounty-v2/       # New v2 contract (Phase 1-2)
    ├── src/
    │   └── lib.rs            # Main program with Phase 1-2 features
    ├── tests/
    │   └── phase1_phase2.spec.ts  # Comprehensive test suite
    ├── Cargo.toml
    ├── Anchor.toml
    └── package.json

programs/
└── staking-v2/               # Staking contract skeleton
    ├── src/
    │   └── lib.rs            # Staking program skeleton
    └── Cargo.toml

src/services/
└── contract_adapter_v2.py    # Backend adapter (feature flag controlled)
```

---

## Prerequisites

### Required Software
- Rust 1.70+
- Solana CLI 1.17+
- Anchor Framework 0.28.0
- Node.js 16+
- Python 3.9+ (for backend adapter)

### Installation
```bash
# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/v1.17.0/install)"

# Install Anchor
npm install -g @coral-xyz/anchor-cli

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

---

## Building the Contracts

### Build V2 Program
```bash
cd programs/billions-bounty-v2
anchor build
```

This will:
- Compile the Rust program
- Generate TypeScript types
- Create IDL file in `target/idl/`

### Build Staking V2 Program (Optional)
```bash
cd programs/staking-v2
anchor build
```

---

## Testing

### Run Anchor Integration Tests
```bash
cd programs/billions-bounty-v2
anchor test
```

This will:
- Start a local Solana validator
- Deploy the program
- Run all tests in `tests/phase1_phase2.spec.ts`
- Test Phase 1 features (4-way split, per-bounty tracking, signature verification)
- Test Phase 2 features (price escalation, buyback)

### Run Python Backend Tests
```bash
# From project root
pytest tests/integration/test_contract_v2_adapter.py -v
```

These tests verify:
- Feature flag behavior (defaults to disabled)
- No regression when flag is disabled
- Adapter methods work when flag is enabled

---

## Feature Flag Configuration

The v2 contract is controlled by a feature flag to ensure non-breaking integration.

### Enable V2 Contract (Development)
```bash
# In .env file
USE_CONTRACT_V2=true
LOTTERY_PROGRAM_ID_V2=B1LL10N5B0UNTYv211111111111111111111111111111111

# Wallet addresses for 4-way split
BOUNTY_POOL_WALLET=<your_bounty_pool_wallet>
OPERATIONAL_WALLET=<your_operational_wallet>
BUYBACK_WALLET=<your_buyback_wallet>
STAKING_WALLET=<your_staking_wallet>
```

### Disable V2 Contract (Default)
## IDL Extraction and Clients

Extract IDL for v2 and store it for clients:

```bash
cd programs/billions-bounty-v2
anchor idl extract -o target/idl/billions_bounty_v2.json HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm
```

Commit the IDL (and generated types if used) to ensure stable integration across services.

Reference the integration plan:
`docs/development/INTEGRATION_V2_PLAN.md`

```bash
# In .env file (or omit entirely)
USE_CONTRACT_V2=false
```

When disabled:
- Backend continues using existing v1 contract
- No changes to existing functionality
- `contract_adapter_v2.py` returns `None` when accessed

---

## Phase 1 Features

### 1. 4-Way Revenue Split (60/20/10/10)
- **60%** to bounty pool wallet
- **20%** to operational wallet
- **10%** to buyback wallet
- **10%** to staking wallet

**Contract Method**: `process_entry_payment_v2`

### 2. Per-Bounty Tracking
- Each bounty has its own PDA account
- Tracks `current_pool` and `total_entries` per bounty
- Supports multiple concurrent bounties

**Contract Methods**: `initialize_bounty`, `process_entry_payment_v2`

### 3. Ed25519 Signature Verification
- Full Ed25519 signature verification for AI decisions
- Anti-replay protection using nonce accounts
- Backend authority public key stored on-chain

**Contract Method**: `process_ai_decision_v2`

---

## Phase 2 Features

### 1. On-Chain Price Escalation
- Formula: `base_price * (1.0078 ^ total_entries)`
- Enforced in `process_entry_payment_v2`
- Prevents underpayment

### 2. Buyback Automation Primitive
- Tracks buyback allocations
- `execute_buyback` method for manual/cron execution
- Events emitted for monitoring

**Contract Method**: `execute_buyback`

### 3. Staking Skeleton
- Basic staking/unstaking functionality
- Reward distribution skeleton
- Full implementation to be added later

**Contract**: `programs/staking-v2/`

---

## Deployment (Local Testing Only)

### Deploy to Local Validator
```bash
# Start local validator
solana-test-validator

# In another terminal, deploy v2 program
cd programs/billions-bounty-v2
anchor deploy --provider.cluster localnet
```

### Deploy to Devnet (After Testing)
```bash
# Configure for devnet
solana config set --url devnet

# Get SOL for deployment fees
solana airdrop 2

# Deploy
cd programs/billions-bounty-v2
anchor deploy --provider.cluster devnet
```

**Note**: Update `LOTTERY_PROGRAM_ID_V2` in `.env` with the deployed program ID.

---

## Backend Integration

### Using the Adapter

```python
from src.services.contract_adapter_v2 import get_contract_adapter_v2

# Get adapter (returns None if feature flag is disabled)
adapter = get_contract_adapter_v2()

if adapter:
    # Use v2 contract
    result = await adapter.process_entry_payment_v2(
        bounty_id=1,
        entry_amount=10_000_000,  # 10 USDC (6 decimals)
        user_keypair=user_keypair,
    )
else:
    # Fall back to existing v1 contract
    from src.services import smart_contract_service
    result = await smart_contract_service.process_entry_payment(...)
```

### Migration Path

1. **Phase A**: Deploy v2 contract to devnet, test thoroughly
2. **Phase B**: Enable feature flag in non-production environment
3. **Phase C**: Run both v1 and v2 in parallel, compare results
4. **Phase D**: Switch to v2 as default in production
5. **Phase E**: Deprecate v1 contract

---

## Testing Checklist

Before deploying to devnet/mainnet:

- [ ] Contracts compile without errors (`anchor build`)
- [ ] All Anchor tests pass (`anchor test`)
- [ ] Python adapter tests pass (`pytest tests/integration/test_contract_v2_adapter.py`)
- [ ] Feature flag works correctly (test with `USE_CONTRACT_V2=false` and `true`)
- [ ] No regression in existing backend functionality when flag is disabled
- [ ] Wallet addresses configured correctly in `.env`
- [ ] Program ID updated after deployment

---

## Troubleshooting

### Build Errors
```bash
# Clean and rebuild
cd programs/billions-bounty-v2
anchor clean
anchor build
```

### Test Failures
```bash
# Check local validator is running
solana-test-validator

# Run tests with verbose output
anchor test -- --verbose
```

### Backend Integration Issues
```bash
# Verify feature flag
echo $USE_CONTRACT_V2

# Check Python adapter logs
tail -f logs/backend.log | grep ContractAdapterV2
```

---

## Security Considerations

1. **Ed25519 Verification**: Backend authority key must be kept secure
2. **Wallet Addresses**: Verify all 4 wallet addresses are correct before deployment
3. **Program Upgrade**: Plan for program upgrades without breaking existing state
4. **Access Control**: Authority-only functions must be properly protected

---

## Next Steps

1. **Complete Implementation**: Finish full Anchor instruction building in `contract_adapter_v2.py`
2. **Add More Tests**: Edge cases, overflow scenarios, security tests
3. **Monitoring**: Add logging and monitoring for v2 contract events
4. **Documentation**: Update API documentation with v2 endpoints

---

## Related Files

- Migration Plan: `SMART_CONTRACT_MIGRATION_PLAN.md`
- Deployment Guide: `docs/deployment/SMART_CONTRACT_DEPLOYMENT.md`
- Demo Guide: `SMART_CONTRACT_DEMO_GUIDE.md`

---

**Last Updated**: October 2025  
**Status**: Phase 1-2 Implementation Complete, Ready for Testing

