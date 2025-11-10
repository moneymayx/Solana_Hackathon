# Smart Contract Directory

This directory contains all smart contract implementations, organized by version.

## Directory Structure

```
smart-contract/
├── v1/                          # Original V1 smart contracts
│   └── billions-bounty/         # V1 contract implementation
│
└── v2_implementation/           # V2 smart contract implementation
    ├── backend/
    │   ├── services/            # V2 backend services
    │   │   ├── payment_processor.py
    │   │   └── contract_service.py
    │   └── api/                 # V2 API endpoints
    │       ├── v2_payment_router.py
    │       └── contract_adapter_v2.py
    ├── contracts/               # V2 Solana smart contracts
    │   └── billions-bounty-v2/
    ├── scripts/                 # V2 deployment and testing scripts
    │   ├── init_v2.py
    │   ├── test_v2_integration.py
    │   └── update_v2_ids.py
    └── tests/                   # V2 test files
        ├── test_v2_service.py
        └── integration/
            └── test_contract_v2_adapter.py
```

## Importing V2 Code

Since V2 files have been moved to this location, you need to update your Python path or import statements:

### Option 1: Update sys.path

```python
import sys
from pathlib import Path

# Add smart-contract/v2_implementation/backend to path
v2_backend_path = Path(__file__).parent.parent / "smart-contract" / "v2_implementation" / "backend"
sys.path.insert(0, str(v2_backend_path))

# Now you can import
from services.payment_processor import V2PaymentProcessor
from api.v2_payment_router import router
```

### Option 2: Use absolute imports with new path

```python
from smart_contract.v2_implementation.backend.services.payment_processor import V2PaymentProcessor
```

### Option 3: Create symlinks or update src/__init__.py

To maintain backward compatibility, you may want to:
- Update `src/__init__.py` to import from new locations
- Or create symlinks from old locations to new locations

## V1 Contracts (Deprecated)

V1 contracts are kept for reference but are no longer in active use. All new development should use V2.

## V2 Status

✅ **V2 is the active implementation**  
📍 **Location**: `smart-contract/v2_implementation/`  
🔧 **Environment Flag**: Set `USE_CONTRACT_V2=true` to use V2

## Notes

- Frontend V2 components remain in `frontend/src/components/` and `frontend/src/lib/v2/`
- V2 documentation remains in `docs/V2_*.md` files
- All references in existing code have been updated to point to new locations

