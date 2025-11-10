# V3 Lottery Initialization Status

**Date**: Current  
**Status**: ❌ **NOT INITIALIZED**

## Summary

✅ **Program Deployed**: `ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb` on devnet  
❌ **Lottery Account**: NOT initialized (PDA: `GT92MxqzyrMEnmCvcRLwFmTWGs6X6Q2QFHeCk2bpu35i`)

## Current Wallet Status

### Authority Wallet
- Address: `ApmfsAisbiPys6v79hbhG6Bbipx1SmxBnaHqPLs7v7bC`
- SOL Balance: ~7.06 SOL ✅ (sufficient for fees)

### Jackpot Wallet
- Address: `CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF`
- SOL Balance: 0 SOL
- USDC Balance: **15 USDC** (V2 devnet test token: `JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh`)
  - Token Account: `FxZ2AywgfAzi2a6SbuFBePbNytsTqzXXSYwApXdST5NG`

## Required for Initialization

1. **Research Fund Floor**: Minimum 10 USDC (10,000,000 smallest units)
   - Current: 15 USDC available ✅ (sufficient)
   
2. **Research Fee**: 10 USDC per entry (configurable)

3. **Backend Authority**: Public key for signature verification
   - Default: Same as jackpot wallet (`CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF`)

## Next Steps

### Option 1: Initialize with Current Funds (Recommended for Testing)

The jackpot wallet has 15 USDC, which is sufficient for a test initialization with a 10 USDC research fund floor.

**Command**:
```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
V3_RESEARCH_FUND_FLOOR=10000000 \
V3_USDC_MINT_DEVNET=JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh \
npx ts-node scripts/initialize_v3_lottery_anchor.ts
```

**Note**: The Anchor-based script needs fixing (IDL loading issue). Alternative: use the Python backend initialization endpoint if available.

### Option 2: Use Python Backend Initialization

If the backend has an initialization endpoint, you could call it directly:

```python
# From backend
from src.services.contract_adapter_v3 import ContractAdapterV3

adapter = ContractAdapterV3()
# Initialize lottery...
```

### Option 3: Fix TypeScript Initialization Script

The raw instruction script (`initialize_v3_lottery.ts`) encountered a `DeclaredProgramIdMismatch` error. This might be:
- An Anchor metadata issue
- Incorrect instruction building
- Need to use Anchor Program class properly

## Verification

After initialization, verify with:

```bash
node scripts/check_v3_lottery_status.js
```

Should show:
- ✅ Program is deployed
- ✅ Lottery account EXISTS

## Resources

- V3 Integration Guide: `docs/development/V3_INTEGRATION_GUIDE.md`
- Program ID: `ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb`
- Lottery PDA: `GT92MxqzyrMEnmCvcRLwFmTWGs6X6Q2QFHeCk2bpu35i`

