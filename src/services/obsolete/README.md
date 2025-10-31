# Deprecated Services Directory

**Status**: ⚠️ **NOT IN USE**  
**Purpose**: Archive for deprecated backend fund routing code

---

## ⚠️ Important Notice

**All fund routing now happens on-chain via V2 smart contracts.**

This directory contains legacy code that is **NOT used in production**. It is kept for:
- Reference purposes
- Rollback scenarios
- Historical context

---

## Active Code Locations

**✅ Active Payment Processing**:
- `../v2/payment_processor.py` - V2 payment processor
- `../smart_contract_service.py` - Main service (uses V2 when enabled)

**✅ Active Smart Contracts**:
- `../../programs/billions-bounty-v2/` - V2 smart contract

---

## Migration Notes

All payment and fund routing logic has been moved to:
1. **V2 Smart Contracts** (`programs/billions-bounty-v2/`)
2. **V2 Backend Integration** (`../v2/payment_processor.py`)

See [ARCHITECTURE.md](../../ARCHITECTURE.md) for system architecture.

---

**This code is deprecated and should not be used for new development.**

