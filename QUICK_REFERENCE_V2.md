# V2 Quick Reference - For Repository Visitors

**Last Updated**: October 31, 2025

---

## 🎯 Is Backend Code Used for Payments?

**NO** - All fund routing happens **on-chain via Solana smart contracts**. The backend only provides:
- API endpoints for frontend
- AI decision processing
- User data management
- Database operations

**No private keys are stored** - Users sign transactions directly from their wallets.

---

## 📍 Where Are Smart Contracts?

**Location**: `programs/billions-bounty-v2/`

**Program ID**: `HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm` (Devnet)

**Network**: Solana Devnet

**Explorer**: https://explorer.solana.com/address/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm?cluster=devnet

---

## ✅ What's Active?

| Component | Location | Status |
|-----------|----------|--------|
| Smart Contracts | `programs/billions-bounty-v2/` | ✅ Active |
| Backend Processor | `src/services/v2/payment_processor.py` | ✅ Active |
| API Endpoints | `src/api/v2_payment_router.py` | ✅ Active |
| Frontend Processor | `frontend/src/lib/v2/paymentProcessor.ts` | ✅ Active |
| React Component | `frontend/src/components/V2PaymentButton.tsx` | ✅ Active |

---

## ❌ What's Deprecated?

| Component | Location | Status |
|-----------|----------|--------|
| Old Fund Routing | `src/services/obsolete/` | ❌ Not Used |
| V1 Backend Logic | Old payment services | ❌ Not Used |

---

## 🔀 How to Switch V1 ↔ V2?

**Backend**: Set `USE_CONTRACT_V2=true` in environment  
**Frontend**: Set `NEXT_PUBLIC_USE_CONTRACT_V2=true` in environment

**No code changes needed** - It's all feature flag controlled.

---

## 📚 Where to Learn More?

1. **System Architecture**: [`ARCHITECTURE.md`](ARCHITECTURE.md)
2. **Production Readiness**: [`PRODUCTION_READINESS_V2.md`](PRODUCTION_READINESS_V2.md)
3. **Integration Guide**: [`V2_INTEGRATION_COMPLETE.md`](V2_INTEGRATION_COMPLETE.md)
4. **Deployment**: [`docs/deployment/V2_DEPLOYMENT_SUMMARY.md`](docs/deployment/V2_DEPLOYMENT_SUMMARY.md)

---

**Quick Answer**: Smart contracts handle payments. Backend = API only. See `ARCHITECTURE.md` for details.

