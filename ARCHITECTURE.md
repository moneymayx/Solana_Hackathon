# Billions Bounty - Architecture Overview

**Last Updated**: October 31, 2025  
**Current Status**: V2 Smart Contracts (Devnet) - Production Ready

---

## 🏗️ System Architecture

### Active Code Path (V2 Smart Contracts)

**Current Production System**: The platform operates on **Solana Smart Contracts (V2)** for all payment and fund management operations. The backend serves as an API layer and does NOT handle fund routing.

```
┌─────────────────┐
│   User Wallet   │
└────────┬────────┘
         │ USDC Transfer
         ▼
┌─────────────────────────────────────┐
│   V2 Smart Contract (Solana)       │
│   Program ID: HDAfSw1n9o9iZyn...   │
│                                     │
│   • 4-way fund split (60/20/10/10) │
│   • Price escalation               │
│   • Per-bounty tracking            │
│   • Buyback primitive              │
│   • Autonomous execution           │
└─────────────────────────────────────┘
         │
         ├──► 60% Bounty Pool
         ├──► 20% Operational
         ├──► 10% Buyback
         └──► 10% Staking

┌─────────────────┐
│  Backend API    │  ← Only provides API endpoints, AI decisions, user data
│  (FastAPI)      │     Does NOT handle fund routing
└─────────────────┘
```

### Legacy Code Path (V1 - Deprecated)

**Note**: The V1 backend fund routing code exists but is **NOT in use**. All payments flow through V2 smart contracts.

**Location of Deprecated Code**:
- `src/services/obsolete/` - Old fund routing service
- Legacy payment handlers in `src/services/` (if any)
- V1 smart contract references (kept for backward compatibility)

**How to Identify Active vs Inactive Code**:
1. ✅ **Active**: Files in `src/services/v2/` or references to `USE_CONTRACT_V2=true`
2. ❌ **Inactive**: Files in `src/services/obsolete/` or old payment services
3. ✅ **Active**: Smart contracts in `programs/billions-bounty-v2/`
4. ❌ **Inactive**: Old contracts in `programs/billions-bounty/` (if exists)

---

## 📁 Directory Structure

### Smart Contracts (Active)
```
programs/billions-bounty-v2/
├── src/lib.rs              # V2 contract source
├── Anchor.toml            # V2 contract config
├── scripts/
│   ├── init_v2_raw.ts     # Initialization script
│   └── test_v2_raw_payment.ts  # Payment test
└── tests/                 # Contract tests
```

**Program ID**: `HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm` (Devnet)

### Backend Services (Active)
```
src/services/
├── v2/                    # ✅ V2 Integration (ACTIVE)
│   ├── payment_processor.py    # Raw instruction processor
│   └── contract_service.py    # V2 contract adapter
├── smart_contract_service.py  # ✅ Main service (uses V2 when flag set)
└── obsolete/              # ❌ Deprecated code
    └── fund_routing_service.py
```

### API Endpoints (Active)
```
src/api/
├── v2_payment_router.py   # ✅ V2 payment endpoints
└── (other routers...)     # Standard API endpoints
```

### Frontend (Active)
```
frontend/
├── src/lib/v2/           # ✅ V2 payment processor
│   └── paymentProcessor.ts
└── src/components/
    └── V2PaymentButton.tsx  # ✅ V2 payment component
```

---

## 🔀 Feature Flag System

### Environment Variables

**Backend** (DigitalOcean):
```bash
USE_CONTRACT_V2=true              # Master switch
LOTTERY_PROGRAM_ID_V2=HDAfSw...  # V2 program ID
V2_GLOBAL_PDA=BursCahsMxKji...   # V2 Global PDA
V2_BOUNTY_1_PDA=2J455GTdBfce...  # V2 Bounty PDA
V2_USDC_MINT=JBJctjHYUCMBhQ...   # USDC mint
V2_BOUNTY_POOL_WALLET=CaCqZ...   # Destination wallets
V2_OPERATIONAL_WALLET=46efq...
V2_BUYBACK_WALLET=7iVPm...
V2_STAKING_WALLET=Fzj8p...
```

**Frontend** (Vercel):
```bash
NEXT_PUBLIC_USE_CONTRACT_V2=true
NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V2=HDAfSw...
# ... other V2 config
```

### Code Switching Logic

**Backend** (`src/services/smart_contract_service.py`):
```python
use_v2 = os.getenv("USE_CONTRACT_V2", "false").lower() == "true"

if use_v2:
    self.program_id = Pubkey.from_string(os.getenv("LOTTERY_PROGRAM_ID_V2"))
    logger.info("🆕 Using V2 smart contract")
else:
    self.program_id = Pubkey.from_string(os.getenv("LOTTERY_PROGRAM_ID"))
    logger.info("📌 Using V1 smart contract")
```

**Frontend** (`frontend/src/lib/v2/paymentProcessor.ts`):
- Always uses V2 contract configuration
- Wallet adapter handles transactions

---

## 🔍 How to Identify Active Code

### ✅ Active Code Indicators

1. **File Paths**:
   - `src/services/v2/` - Always active when V2 is enabled
   - `src/api/v2_payment_router.py` - V2 API endpoints
   - `programs/billions-bounty-v2/` - Active smart contract

2. **Environment Variables**:
   - `USE_CONTRACT_V2=true` - Indicates V2 is active
   - Variables starting with `V2_` - V2 configuration

3. **Code Comments**:
   - Look for `# V2` or `# Active` comments
   - Check for `TODO` comments indicating incomplete features

4. **Logging**:
   - Logs show "🆕 Using V2 smart contract" when V2 is active
   - Logs show "📌 Using V1 smart contract" when V1 is active

### ❌ Inactive Code Indicators

1. **File Paths**:
   - `src/services/obsolete/` - Deprecated code
   - Files with `_old`, `_deprecated`, `_backup` suffixes

2. **Environment Variables**:
   - `USE_CONTRACT_V2=false` - V2 disabled
   - Missing `V2_*` variables

3. **Git Branches**:
   - `main` - Production (may have both V1 and V2)
   - `staging-v2` - V2 testing branch

---

## 📋 Smart Contract Location

**Active Smart Contracts**:
- **Location**: `programs/billions-bounty-v2/`
- **Network**: Solana Devnet
- **Program ID**: `HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`
- **Deployment**: See `docs/deployment/V2_DEPLOYMENT_SUMMARY.md`

**Why Backend Code Isn't Used for Payments**:
- All fund routing happens **on-chain** via smart contracts
- Backend only provides:
  - API endpoints for frontend
  - AI decision processing
  - User data management
  - Database operations
- **No private keys stored** - Users sign transactions directly

---

## 🚀 Production Readiness Checklist

### Code Organization
- [x] V2 code in dedicated directories (`src/services/v2/`, `programs/billions-bounty-v2/`)
- [x] Deprecated code in `obsolete/` directories
- [x] Clear feature flag system
- [ ] Documentation updated (this file)

### Git Strategy
- [x] Branch `staging-v2` for V2 development
- [x] Main branch stable
- [ ] Merge strategy documented
- [ ] Tag releases appropriately

### Testing
- [x] Integration tests for V2
- [x] V1 compatibility verified
- [x] Frontend builds successfully
- [x] Backend imports successfully

### Documentation
- [x] Architecture overview (this file)
- [x] Integration guides
- [x] Deployment documentation
- [ ] Production deployment guide

---

## 📚 Quick Reference

### Where is the Payment Logic?
- **Smart Contracts**: `programs/billions-bounty-v2/src/lib.rs`
- **Backend Adapter**: `src/services/v2/payment_processor.py`
- **Frontend Adapter**: `frontend/src/lib/v2/paymentProcessor.ts`

### How to Switch V1 ↔ V2?
- Set `USE_CONTRACT_V2=true` (backend) or `NEXT_PUBLIC_USE_CONTRACT_V2=true` (frontend)
- Restart services
- No code changes needed

### Where are Smart Contracts?
- **Location**: `programs/billions-bounty-v2/`
- **Network**: Devnet
- **Explorer**: https://explorer.solana.com/address/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm?cluster=devnet

---

## 🔗 Related Documentation

- **Integration Guide**: `V2_INTEGRATION_COMPLETE.md`
- **Deployment**: `docs/deployment/V2_DEPLOYMENT_SUMMARY.md`
- **Testing**: `V2_INTEGRATION_TEST_REPORT.md`
- **Migration Plan**: `SMART_CONTRACT_MIGRATION_PLAN.md`



