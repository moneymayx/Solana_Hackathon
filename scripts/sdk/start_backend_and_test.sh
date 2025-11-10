#!/bin/bash
# Start backend and test SDK endpoints

echo "🚀 Starting Backend with SDK Integration..."
echo "=" | head -c 60 && echo

cd "$(dirname "$0")/../../"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    exit 1
fi

source venv/bin/activate

# Check environment variables
echo "🔍 Checking Environment Variables..."
echo "ENABLE_KORA_SDK: ${ENABLE_KORA_SDK:-not set}"
echo "ENABLE_ATTESTATIONS_SDK: ${ENABLE_ATTESTATIONS_SDK:-not set}"
echo "ENABLE_SOLANA_PAY_SDK: ${ENABLE_SOLANA_PAY_SDK:-not set}"
echo

# Start backend in background
echo "📡 Starting FastAPI backend..."
python apps/backend/main.py &
BACKEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"
echo "⏳ Waiting for backend to initialize..."

# Wait for backend to be ready
sleep 5

# Test endpoints
echo ""
echo "🧪 Testing SDK Endpoints..."
echo "=" | head -c 60 && echo

# Kora endpoints
echo ""
echo "📡 Testing Kora Endpoints:"
curl -s http://localhost:8000/api/sdk-test/kora/status | python -m json.tool || echo "❌ Kora status failed"
curl -s http://localhost:8000/api/sdk-test/kora/config | python -m json.tool || echo "❌ Kora config failed"

# Attestations endpoints
echo ""
echo "📡 Testing Attestations Endpoints:"
curl -s http://localhost:8000/api/sdk-test/attestations/status | python -m json.tool || echo "❌ Attestations status failed"
curl -s -X POST http://localhost:8000/api/sdk-test/attestations/verify-kyc \
  -H "Content-Type: application/json" \
  -d '{"wallet_address": "11111111111111111111111111111111"}' | python -m json.tool || echo "❌ Attestations verify-kyc failed"

# Solana Pay endpoints
echo ""
echo "📡 Testing Solana Pay Endpoints:"
curl -s http://localhost:8000/api/sdk-test/solana-pay/status | python -m json.tool || echo "❌ Solana Pay status failed"

echo ""
echo "=" | head -c 60 && echo
echo "✅ Tests Complete!"
echo ""
echo "💡 Backend is still running (PID: $BACKEND_PID)"
echo "   To stop: kill $BACKEND_PID"

