#!/bin/bash
# Test SDK endpoints (assumes backend is already running)

BASE_URL="${1:-http://localhost:8000}"

echo "🧪 Testing SDK Endpoints"
echo "Base URL: $BASE_URL"
echo "=" | head -c 60 && echo

test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    echo ""
    echo "📡 $method $endpoint"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_CODE/d')
    
    if [ "$http_code" = "200" ]; then
        echo "   ✅ Status: $http_code"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    else
        echo "   ❌ Status: $http_code"
        echo "   Response: $body"
    fi
}

# Kora endpoints
echo ""
echo "🔵 Kora SDK"
echo "-" | head -c 60 && echo
test_endpoint "GET" "/api/sdk-test/kora/status"
test_endpoint "GET" "/api/sdk-test/kora/config"
test_endpoint "GET" "/api/sdk-test/kora/supported-tokens"

# Attestations endpoints
echo ""
echo "🟢 Attestations SDK"
echo "-" | head -c 60 && echo
test_endpoint "GET" "/api/sdk-test/attestations/status"
test_endpoint "POST" "/api/sdk-test/attestations/verify-kyc" '{"wallet_address": "11111111111111111111111111111111"}'
test_endpoint "GET" "/api/sdk-test/attestations/all/11111111111111111111111111111111"

# Solana Pay endpoints
echo ""
echo "🟡 Solana Pay SDK"
echo "-" | head -c 60 && echo
test_endpoint "GET" "/api/sdk-test/solana-pay/status"
test_endpoint "POST" "/api/sdk-test/solana-pay/create-transfer-request" '{"recipient": "11111111111111111111111111111111", "amount": 0.1}'

echo ""
echo "=" | head -c 60 && echo
echo "✅ All endpoint tests complete!"

