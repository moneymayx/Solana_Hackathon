#!/bin/bash
# Test runner script for Activity Tracker feature
# Runs all automated tests related to the activity tracker

set -e

echo "🧪 Running Activity Tracker Automated Tests"
echo "==========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

cd "$(dirname "$0")/.."

# Frontend Component Tests
echo -e "${YELLOW}📦 Running Frontend Component Tests...${NC}"
npm test -- ActivityTracker UsernamePrompt --passWithNoTests

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Component tests passed${NC}"
else
    echo -e "${RED}❌ Component tests failed${NC}"
    exit 1
fi

echo ""

# Frontend Integration Tests
echo -e "${YELLOW}🔗 Running Frontend Integration Tests...${NC}"
npm test -- ActivityTrackerIntegration --passWithNoTests

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Integration tests passed${NC}"
else
    echo -e "${RED}❌ Integration tests failed${NC}"
    exit 1
fi

echo ""

# Backend API Tests (requires backend running)
echo -e "${YELLOW}🔧 Running Backend API Tests...${NC}"
echo -e "${YELLOW}   (Backend must be running on http://localhost:8000)${NC}"

cd ../tests
python3 test_user_profile_api.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend API tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  Backend API tests skipped or failed${NC}"
    echo -e "${YELLOW}   Make sure backend is running: python3 apps/backend/main.py${NC}"
fi

echo ""
echo -e "${GREEN}🎉 All automated tests completed!${NC}"
echo ""
echo "💡 To run E2E tests: npm run test:e2e -- activity-tracker"

