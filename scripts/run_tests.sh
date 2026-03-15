#!/bin/bash
set -e

echo "=========================================="
echo "CoPaw Test Suite Runner"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
SKIPPED=0

echo "📋 Running backend tests (pytest)..."
echo ""

# Run Python tests
if pytest tests/test_auth.py tests/test_auth_integration.py tests/test_categories.py -v --tb=short; then
    echo -e "${GREEN}✅ Backend tests passed${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Backend tests failed${NC}"
    ((FAILED++))
fi

echo ""
echo "=========================================="
echo "📋 Running frontend tests (vitest)..."
echo ""

# Check if node_modules exists
if [ ! -d "console/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Node modules not found. Running npm install...${NC}"
    cd console && npm install && cd ..
fi

# Run frontend tests
cd console
if npm run test:run; then
    echo -e "${GREEN}✅ Frontend tests passed${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Frontend tests failed${NC}"
    ((FAILED++))
fi
cd ..

echo ""
echo "=========================================="
echo "📊 Test Summary"
echo "=========================================="
echo -e "Passed:  ${GREEN}${PASSED}${NC}"
echo -e "Failed:  ${RED}${FAILED}${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
