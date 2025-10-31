# Documentation Index

**Last Updated**: October 31, 2025

This index provides a complete guide to all documentation in the Billions Bounty repository.

---

## 🚀 Quick Start

**New to the project?** Start here:
1. [README.md](../README.md) - Project overview and current status
2. [ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture and active code paths
3. [QUICK_REFERENCE_V2.md](../QUICK_REFERENCE_V2.md) - Quick answers for common questions

---

## 📚 Core Documentation

### System Architecture
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - Complete system architecture, active vs deprecated code, payment flow

### V2 Smart Contract Documentation

All V2 documentation has been consolidated into comprehensive guides:

1. **[V2_INTEGRATION_GUIDE.md](./V2_INTEGRATION_GUIDE.md)**
   - Backend integration (Python)
   - Frontend integration (TypeScript/React)
   - API endpoints
   - Configuration
   - Troubleshooting

2. **[V2_DEPLOYMENT_GUIDE.md](./V2_DEPLOYMENT_GUIDE.md)**
   - Deployment status
   - Contract details
   - Initialization
   - Enabling V2
   - Staging deployment
   - Production deployment
   - Troubleshooting

3. **[V2_TESTING_GUIDE.md](./V2_TESTING_GUIDE.md)**
   - Test results summary
   - Automated testing
   - Manual testing
   - Payment testing
   - Integration testing
   - Test reports

4. **[V2_STATUS.md](./V2_STATUS.md)**
   - Overall status
   - Deployment status
   - Features status
   - Testing status
   - Integration status
   - Known issues
   - Next steps

5. **[PRODUCTION_READINESS_V2.md](../PRODUCTION_READINESS_V2.md)**
   - Production readiness checklist
   - Git branch strategy
   - File organization
   - Code comments
   - Environment variables
   - Deployment procedures

6. **[QUICK_REFERENCE_V2.md](../QUICK_REFERENCE_V2.md)**
   - Quick answers
   - Active code locations
   - Deprecated code locations
   - Configuration quick reference

---

## 📁 Documentation by Category

### Deployment Documentation
- **[V2_DEPLOYMENT_GUIDE.md](./V2_DEPLOYMENT_GUIDE.md)** - Complete deployment guide
- **[STAGING_CHECKLIST.md](./deployment/STAGING_CHECKLIST.md)** - Staging deployment checklist
- **[DEPLOYMENT_INSTRUCTIONS.md](../DEPLOYMENT_INSTRUCTIONS.md)** - Detailed deployment instructions
- **[SMART_CONTRACT_DEPLOYMENT.md](./deployment/SMART_CONTRACT_DEPLOYMENT.md)** - Smart contract deployment guide

### Development Documentation
- **[V2_INTEGRATION_GUIDE.md](./V2_INTEGRATION_GUIDE.md)** - Developer integration guide
- **[INTEGRATION_V2_PLAN.md](./development/INTEGRATION_V2_PLAN.md)** - Integration plan
- **[CI_V2_IDL_AND_TESTS.md](./development/CI_V2_IDL_AND_TESTS.md)** - CI/CD for V2
- **[E2E_V2_TEST_PLAN.md](./development/E2E_V2_TEST_PLAN.md)** - End-to-end test plan

### Testing Documentation
- **[V2_TESTING_GUIDE.md](./V2_TESTING_GUIDE.md)** - Complete testing guide
- **[STAGING_TEST_REPORT.md](../STAGING_TEST_REPORT.md)** - Staging test results
- **[TEST_SUMMARY.md](../TEST_SUMMARY.md)** - Test summary

### Configuration Documentation
- **[STAGING_ENV_FLAGS.md](./development/STAGING_ENV_FLAGS.md)** - Environment variable reference
- **[VERCEL_ENV_VARIABLES_EXPLAINED.md](../VERCEL_ENV_VARIABLES_EXPLAINED.md)** - Vercel environment variables
- **[ENV_FILES_CONSOLIDATED.md](../ENV_FILES_CONSOLIDATED.md)** - Environment file consolidation

---

## 🔍 Finding Specific Information

### "Where is the payment logic?"
- **Smart Contracts**: `programs/billions-bounty-v2/src/lib.rs`
- **Backend Adapter**: `src/services/v2/payment_processor.py`
- **Frontend Adapter**: `frontend/src/lib/v2/paymentProcessor.ts`
- **Documentation**: [V2_INTEGRATION_GUIDE.md](./V2_INTEGRATION_GUIDE.md)

### "How do I enable V2?"
- **Guide**: [V2_DEPLOYMENT_GUIDE.md](./V2_DEPLOYMENT_GUIDE.md) - Section "Enabling V2"
- **Quick**: Set `USE_CONTRACT_V2=true` in environment

### "How do I test payments?"
- **Guide**: [V2_TESTING_GUIDE.md](./V2_TESTING_GUIDE.md) - Section "Payment Testing"
- **Test Script**: `programs/billions-bounty-v2/scripts/test_v2_raw_payment.ts`

### "What's the deployment status?"
- **Guide**: [V2_STATUS.md](./V2_STATUS.md)
- **Quick**: ✅ Production ready on devnet

### "Where is deprecated code?"
- **Location**: `src/services/obsolete/`
- **Documentation**: [ARCHITECTURE.md](../ARCHITECTURE.md) - Section "Inactive Code Indicators"

---

## 📂 Archive

### Consolidated Documentation

The following files were consolidated into the guides above and archived in `docs/archive/v2_consolidation/`:

**Integration Files** (→ V2_INTEGRATION_GUIDE.md):
- V2_INTEGRATION_COMPLETE.md
- V2_INTEGRATION_COMPLETE_SUMMARY.md
- V2_INTEGRATION_SUMMARY.md
- V2_INTEGRATION_TEST_REPORT.md

**Deployment Files** (→ V2_DEPLOYMENT_GUIDE.md):
- V2_DEPLOYMENT_STATUS.md
- V2_SWITCH_FIX.md
- ENABLE_V2_GUIDE.md
- docs/deployment/V2_DEPLOYMENT_SUMMARY.md
- docs/deployment/V2_STAGING_SUMMARY.md

**Testing Files** (→ V2_TESTING_GUIDE.md):
- V2_PAYMENT_TEST_GUIDE.md
- V2_PAYMENT_TEST_INSTRUCTIONS.md
- V2_TEST_STATUS.md

**Status Files** (→ V2_STATUS.md):
- V2_COMPLETE_STATUS.md
- V2_COMPLETION_REPORT.md
- V2_FINAL_COMPLETION_REPORT.md
- V2_FINAL_STATUS.md
- V2_ACTIVATION_SUCCESS.md
- V2_ID_UPDATE_SUMMARY.md
- V2_PRODUCTION_ORGANIZATION_SUMMARY.md

---

## 🔗 External Resources

- **Solana Explorer**: https://explorer.solana.com/address/HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm?cluster=devnet
- **Anchor Documentation**: https://www.anchor-lang.com/
- **Solana Documentation**: https://docs.solana.com/

---

## 📝 Documentation Standards

### File Naming
- `GUIDE.md` - Comprehensive how-to guides
- `STATUS.md` - Current status and metrics
- `README.md` - Directory overviews
- `INDEX.md` - Documentation indexes

### Status Markers
- ✅ Active/Complete
- ⏳ In Progress
- ❌ Deprecated/Not Used
- ⚠️ Warning/Important Note

---

**Last Updated**: October 31, 2025  
**Maintainer**: See git history for contributors

