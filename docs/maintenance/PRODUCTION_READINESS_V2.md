# V2 Production Readiness Guide

**Last Updated**: October 31, 2025  
**Target**: Make V2 production-ready on Devnet  
**Status**: ✅ Ready for production deployment

**Related Documentation**:
- **Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Integration**: [docs/V2_INTEGRATION_GUIDE.md](./docs/V2_INTEGRATION_GUIDE.md)
- **Deployment**: [docs/V2_DEPLOYMENT_GUIDE.md](./docs/V2_DEPLOYMENT_GUIDE.md)
- **Testing**: [docs/V2_TESTING_GUIDE.md](./docs/V2_TESTING_GUIDE.md)
- **Status**: [docs/V2_STATUS.md](./docs/V2_STATUS.md)
- **Quick Reference**: [docs/maintenance/QUICK_REFERENCE_V2.md](./docs/maintenance/QUICK_REFERENCE_V2.md)

---

## 🎯 Goal

Make V2 smart contract system production-ready **on Devnet** with proper organization, documentation, and git strategy - ready to merge to main and deploy.

---

## ✅ Current Status

### What's Complete
- [x] V2 smart contracts deployed and tested
- [x] Backend integration (payment processor, API router)
- [x] Frontend integration (payment processor, React component)
- [x] All tests passing
- [x] Documentation created
- [x] Feature flag system working

### What Needs Organization
- [ ] Git branch strategy
- [ ] File organization cleanup
- [ ] README updates
- [ ] Deprecated code marking
- [ ] Production deployment documentation

---

## 📋 Production Readiness Checklist

### 1. Git Branch Strategy

#### Current State
- `main` - Production branch (has both V1 and V2 code)
- `staging-v2` - V2 development branch (has all new V2 code)

#### Recommended Strategy

**Option A: Merge to Main (Recommended)**
```bash
# 1. Ensure staging-v2 is fully tested
git checkout staging-v2
git pull origin staging-v2

# 2. Merge to main
git checkout main
git pull origin main
git merge staging-v2 --no-ff -m "feat: Add V2 smart contract integration (devnet)"

# 3. Push to main
git push origin main

# 4. Tag release
git tag -a v2.0.0-devnet -m "V2 Smart Contracts (Devnet)"
git push origin v2.0.0-devnet
```

**Option B: Keep Separate (If still testing)**
- Keep `staging-v2` as development branch
- Merge to `main` only after full production testing
- Use `main` for stable, tested code

#### Branch Protection Rules (GitHub/GitLab)
1. Require pull request reviews before merging
2. Require status checks to pass (tests)
3. Require branches to be up to date
4. Do not allow force pushes to main

### 2. File Organization

#### Current Structure (Good)
```
src/
├── services/
│   ├── v2/              # ✅ V2 active code
│   ├── smart_contract_service.py  # ✅ Active (switches V1/V2)
│   └── obsolete/        # ❌ Deprecated
├── api/
│   ├── v2_payment_router.py  # ✅ V2 endpoints
│   └── (other routers)  # ✅ Active
programs/
├── billions-bounty-v2/  # ✅ Active contract
└── billions-bounty/     # ❓ Check if needed
```

#### Recommended Additions

**Add Clear Deprecation Markers**:

1. **Mark V1 backend routing as deprecated**:
```python
# src/services/payment_flow_service.py (if exists and not used)
"""
⚠️ DEPRECATED: This service routes funds through backend.

V2 Migration: All fund routing now happens on-chain via smart contracts.
This service is kept for backward compatibility only.
Use src/services/v2/payment_processor.py for new integrations.
"""
```

2. **Create obsolete directory if missing**:
```bash
mkdir -p src/services/obsolete
# Move any unused payment routing code here
```

3. **Add README in root explaining active code**:
- Create/update `ARCHITECTURE.md` (already created ✅)
- Update main `README.md` with V2 status

### 3. README Updates

#### Update Main README

Add section at top:
```markdown
## 🚀 Current Version: V2 Smart Contracts (Devnet)

**Active System**: This repository uses **V2 Solana Smart Contracts** for all payment operations.
The backend serves as an API layer only - **no fund routing happens in backend code**.

- ✅ **Active**: Smart contracts in `programs/billions-bounty-v2/`
- ✅ **Active**: V2 integration in `src/services/v2/`
- ❌ **Deprecated**: Backend fund routing in `src/services/obsolete/`

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture.
```

#### Add Quick Start Section
```markdown
## Quick Start

### For Developers
1. Smart Contracts: See `programs/billions-bounty-v2/README.md`
2. Backend API: See `src/services/v2/README.md`
3. Frontend: See `frontend/src/lib/v2/README.md`

### For Operators
- Enable V2: Set `USE_CONTRACT_V2=true` in environment
- Deploy: See `docs/deployment/V2_DEPLOYMENT_SUMMARY.md`
- Monitor: See `docs/deployment/STAGING_CHECKLIST.md`
```

### 4. Code Comments & Markers

#### Add Status Comments

**In Active Files**:
```python
# src/services/v2/payment_processor.py
"""
V2 Payment Processor - ACTIVE (Production)

This is the active payment processing system.
All fund routing happens on-chain via smart contracts.
Backend only provides API endpoints and AI decisions.
"""
```

**In Deprecated Files**:
```python
# src/services/obsolete/fund_routing_service.py
"""
⚠️ DEPRECATED: V1 Backend Fund Routing

This code is no longer used. All fund routing moved to V2 smart contracts.
Kept for reference and rollback purposes only.
"""
```

### 5. Environment Variable Documentation

#### Create `.env.example` with Comments
```bash
# ==============================================================================
# V2 SMART CONTRACT CONFIGURATION (ACTIVE)
# ==============================================================================
# Master switch: Set to 'true' to enable V2 smart contracts
USE_CONTRACT_V2=true

# V2 Program ID (Devnet)
LOTTERY_PROGRAM_ID_V2=HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm

# V2 PDAs (Derived from program ID)
V2_GLOBAL_PDA=BursCahsMxKjiSUgTCy11uUTWnaZ1eqcGcADUxiMzHMb
V2_BOUNTY_1_PDA=2J455GTdBfceWWUF7dcPawixW4PEfWBdVgX7Soqc3trb

# ==============================================================================
# V1 SMART CONTRACT (DEPRECATED - For Rollback Only)
# ==============================================================================
# Keep for backward compatibility
LOTTERY_PROGRAM_ID=4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK
```

### 6. Production Deployment Documentation

#### Create Production Checklist

**File**: `docs/deployment/PRODUCTION_READY_V2.md`

Include:
1. Environment variable checklist
2. Deployment steps for DigitalOcean
3. Deployment steps for Vercel
4. Monitoring setup
5. Rollback procedure
6. Testing checklist

### 7. Git Commit Message Strategy

#### Use Conventional Commits

```bash
# Features
git commit -m "feat: Add V2 payment processor"

# Bug fixes
git commit -m "fix: Correct PDA derivation in V2 processor"

# Documentation
git commit -m "docs: Add V2 architecture overview"

# Breaking changes
git commit -m "feat!: Switch to V2 smart contracts (breaking)"
```

#### Tag Releases

```bash
# Devnet release
git tag -a v2.0.0-devnet -m "V2 Smart Contracts (Devnet)"

# Mainnet release (when ready)
git tag -a v2.0.0 -m "V2 Smart Contracts (Mainnet)"
```

---

## 🔍 How Visitors Know What's Active

### 1. Root README.md
- Add prominent "Active System" section at top
- Link to ARCHITECTURE.md
- Show file structure with ✅/❌ indicators

### 2. ARCHITECTURE.md (Created ✅)
- Clear diagram showing active paths
- Directory structure with status
- Feature flag documentation

### 3. File Naming
- ✅ `v2/` prefix for active V2 code
- ❌ `obsolete/` for deprecated code
- ✅ Clear file names (`payment_processor.py`, not `payment.py`)

### 4. Code Comments
- Status comments at top of files
- `# ACTIVE` or `# DEPRECATED` markers
- Links to documentation

### 5. Documentation Index

**File**: `docs/README.md` or `docs/index.md`

```markdown
# Documentation Index

## Active Systems (V2)
- [V2 Architecture](ARCHITECTURE.md)
- [V2 Integration Guide](../V2_INTEGRATION_COMPLETE.md)
- [V2 Deployment](../docs/deployment/V2_DEPLOYMENT_SUMMARY.md)

## Deprecated Systems (V1)
- [V1 Migration Plan](../SMART_CONTRACT_MIGRATION_PLAN.md) - Historical reference
- [Old Backend Services](../src/services/obsolete/) - Not in use
```

---

## 📝 Specific File Changes Needed

### 1. Update README.md
```markdown
## Current System Status

**✅ ACTIVE**: V2 Smart Contracts (Devnet)
- All payments flow through Solana smart contracts
- Backend provides API only (no fund routing)
- See [ARCHITECTURE.md](ARCHITECTURE.md) for details

**❌ DEPRECATED**: V1 Backend Fund Routing
- Code preserved in `src/services/obsolete/` for reference
- Not used in production
```

### 2. Create `.github/CODEOWNERS` (Optional)
```
# V2 Smart Contracts
/programs/billions-bounty-v2/ @your-team

# V2 Integration
/src/services/v2/ @your-team
/src/api/v2_payment_router.py @your-team

# Deprecated code
/src/services/obsolete/ @archived
```

### 3. Create `.github/PULL_REQUEST_TEMPLATE.md`
```markdown
## Changes
- [ ] V2 smart contracts
- [ ] Backend API
- [ ] Frontend components
- [ ] Documentation

## Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Manual testing completed

## Deployment
- [ ] Environment variables documented
- [ ] Breaking changes documented
- [ ] Rollback plan documented
```

---

## 🚀 Deployment Checklist

Before marking as "production-ready":

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Environment variables documented
- [ ] Git branch strategy defined
- [ ] Code organization clear
- [ ] Deprecated code marked
- [ ] README updated
- [ ] Architecture diagram created
- [ ] Deployment guide created
- [ ] Rollback plan documented

---

## 📚 Next Steps

1. **Update README.md** - Add V2 status section
2. **Create ARCHITECTURE.md** - Done ✅
3. **Mark deprecated code** - Add comments
4. **Update .env.example** - Add V2 variables
5. **Git merge strategy** - Decide on branch approach
6. **Create production deployment guide**

---

**Status**: Ready to proceed with organization and documentation updates! 🚀

