#!/bin/bash
# Test script for V3 payment endpoint integration
# Tests that the router is properly registered and accessible

set -e

echo "🧪 Testing V3 Payment Endpoint Integration"
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."

# Check if backend is running
echo "1. Checking if backend is running..."
if curl -s http://localhost:8000/api/context/health > /dev/null 2>&1; then
    echo "   ✅ Backend is running on http://localhost:8000"
else
    echo "   ⚠️  Backend not running - start with: python3 -m uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000"
    echo "   Continuing with import tests only..."
fi

# Test Python imports
echo ""
echo "2. Testing Python imports..."
python3 << 'PYTHON_EOF'
import sys
sys.path.insert(0, '.')

try:
    from apps.backend.api.v3_payment_router import router, V3TestPaymentRequest
    print("   ✅ Router imports successfully")
    print(f"   ✅ Router prefix: {router.prefix}")
    
    # Test request model
    test_req = V3TestPaymentRequest(
        user_wallet="TestWallet1111111111111111111111111111",
        entry_amount=10_000_000,
        amount_usdc=10.0
    )
    print(f"   ✅ Request model works: {test_req.amount_usdc} USDC")
    
    # Check if adapter can be loaded
    from src.services.contract_adapter_v3 import get_contract_adapter_v3, USE_CONTRACT_V3
    print(f"   ✅ Contract adapter imports: USE_CONTRACT_V3={USE_CONTRACT_V3}")
    
    if USE_CONTRACT_V3:
        adapter = get_contract_adapter_v3()
        if adapter:
            print(f"   ✅ Adapter initialized: Program ID={adapter.program_id}")
        else:
            print("   ⚠️  Adapter is None (may need V3_BACKEND_AUTHORITY env var)")
    else:
        print("   ⚠️  USE_CONTRACT_V3 is False - set USE_CONTRACT_V3=true")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_EOF

# Test API endpoint (if backend is running)
echo ""
echo "3. Testing API endpoint (if backend is running)..."
if curl -s http://localhost:8000/api/context/health > /dev/null 2>&1; then
    # Check if endpoint exists by looking at docs
    if curl -s http://localhost:8000/docs | grep -q "v3/payment" 2>/dev/null; then
        echo "   ✅ V3 payment endpoint appears in API docs"
    else
        echo "   ⚠️  V3 payment endpoint not found in docs (may need to check router registration)"
    fi
    
    # Try to make a test request (will likely fail without proper setup, but tests routing)
    response=$(curl -s -X POST http://localhost:8000/api/v3/payment/test \
        -H "Content-Type: application/json" \
        -d '{
            "user_wallet": "TestWallet1111111111111111111111111111",
            "entry_amount": 10000000,
            "amount_usdc": 10.0
        }' 2>&1)
    
    if echo "$response" | grep -q "V3 contract" || echo "$response" | grep -q "error"; then
        echo "   ✅ Endpoint is accessible (got response)"
        echo "   Response: $(echo "$response" | head -c 200)"
    else
        echo "   ⚠️  Unexpected response or endpoint not found"
        echo "   Response: $response"
    fi
else
    echo "   ⏭️  Skipping endpoint test (backend not running)"
fi

echo ""
echo "=========================================="
echo "✅ Integration tests complete!"
echo ""
echo "Next steps:"
echo "  1. Ensure backend is running"
echo "  2. Set USE_CONTRACT_V3=true in backend .env"
echo "  3. Ensure backend wallet has USDC on devnet"
echo "  4. Test from frontend with NEXT_PUBLIC_PAYMENT_MODE=test_contract"




