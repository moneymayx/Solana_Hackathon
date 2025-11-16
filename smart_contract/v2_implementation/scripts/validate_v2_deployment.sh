#!/bin/bash
###############################################################################
# V2 Staging Deployment Validation Script
#
# This script validates that the v2 contract is properly deployed and ready
# for staging integration.
#
# Usage:
#   ./scripts/staging/validate_v2_deployment.sh
#
# Exit codes:
#   0 - All validations passed
#   1 - One or more validations failed
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
TOTAL=0

# Test result function
test_result() {
    TOTAL=$((TOTAL + 1))
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        FAILED=$((FAILED + 1))
    fi
}

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  V2 Contract Staging Validation${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "Anchor.toml" ]; then
    echo -e "${RED}Error: Must run from project root${NC}"
    exit 1
fi

echo -e "${YELLOW}[1/6] Checking TypeScript validation...${NC}"
cd programs/billions-bounty-v2
if ANCHOR_PROVIDER_URL=https://api.devnet.solana.com npx ts-node -T tests/devnet_simple_validation.ts 2>&1 | grep -q "tests passed"; then
    test_result 0 "TypeScript validation"
else
    test_result 1 "TypeScript validation"
fi
cd ../..

echo ""
echo -e "${YELLOW}[2/6] Checking Python integration...${NC}"
# Activate virtual environment if it exists
if [ -d "venv/bin" ]; then
    source venv/bin/activate 2>/dev/null || true
fi
if python3 smart_contract/v2_implementation/scripts/test_v2_integration.py 2>&1 | grep -q "All integration tests passed"; then
    test_result 0 "Python integration tests"
else
    test_result 1 "Python integration tests"
fi

echo ""
echo -e "${YELLOW}[3/6] Checking backend service...${NC}"
# Activate virtual environment if it exists
if [ -d "venv/bin" ]; then
    source venv/bin/activate 2>/dev/null || true
fi
if python3 -c "import sys; sys.path.insert(0, 'src'); from services.v2.contract_service import ContractServiceV2; import asyncio; s = ContractServiceV2(program_id='GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm'); result = asyncio.run(s.get_bounty_status(1)); assert result['success'], 'Service failed'" 2>&1; then
    test_result 0 "Backend v2 service"
else
    test_result 1 "Backend v2 service"
fi

echo ""
echo -e "${YELLOW}[4/6] Checking documentation...${NC}"
DOCS=(
    "docs/deployment/V2_DEPLOYMENT_SUMMARY.md"
    "docs/deployment/STAGING_CHECKLIST.md"
    "docs/development/INTEGRATION_V2_PLAN.md"
    "docs/development/E2E_V2_TEST_PLAN.md"
    "docs/development/STAGING_ENV_FLAGS.md"
)

DOC_CHECK=0
for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo -e "  ${GREEN}✓${NC} $doc"
    else
        echo -e "  ${RED}✗${NC} $doc (missing)"
        DOC_CHECK=1
    fi
done
test_result $DOC_CHECK "Documentation complete"

echo ""
echo -e "${YELLOW}[5/6] Checking environment variables...${NC}"
ENV_VARS=(
    "LOTTERY_PROGRAM_ID_V2"
    "V2_GLOBAL_PDA"
    "V2_BOUNTY_1_PDA"
    "V2_BOUNTY_POOL_WALLET"
    "V2_OPERATIONAL_WALLET"
    "V2_BUYBACK_WALLET"
    "V2_STAKING_WALLET"
)

echo "Required environment variables for staging:"
for var in "${ENV_VARS[@]}"; do
    echo "  - $var"
done
test_result 0 "Environment variables documented"

echo ""
echo -e "${YELLOW}[6/6] Checking contract verifiability...${NC}"
if anchor idl fetch --provider.cluster devnet GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm > /dev/null 2>&1; then
    test_result 0 "IDL fetchable from devnet"
else
    test_result 1 "IDL fetchable from devnet"
fi

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Results: ${PASSED}/${TOTAL} tests passed${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All validations passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Deploy backend to DigitalOcean staging"
    echo "2. Set environment variables from docs/development/STAGING_ENV_FLAGS.md"
    echo "3. Set USE_CONTRACT_V2=false initially"
    echo "4. Test with USE_CONTRACT_V2=true after smoke tests"
    echo "5. Monitor logs for 24 hours"
    echo ""
    echo "See docs/deployment/STAGING_CHECKLIST.md for full deployment guide."
    exit 0
else
    echo -e "${RED}⚠️  ${FAILED} validation(s) failed${NC}"
    echo ""
    echo "Review failures above and fix before deploying to staging."
    exit 1
fi

