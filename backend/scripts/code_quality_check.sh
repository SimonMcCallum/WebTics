#!/bin/bash
# Comprehensive code quality check script for WebTics
# Run before committing or deploying

set -e  # Exit on error

echo "🔍 WebTics Code Quality Check"
echo "=============================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

# Change to backend directory
cd "$(dirname "$0")/.."

# Check if dependencies are installed
echo "📦 Checking dependencies..."
pip list | grep -q "black" || { echo -e "${RED}✗ Black not installed${NC}"; FAILED=1; }
pip list | grep -q "ruff" || { echo -e "${RED}✗ Ruff not installed${NC}"; FAILED=1; }
pip list | grep -q "mypy" || { echo -e "${RED}✗ MyPy not installed${NC}"; FAILED=1; }
pip list | grep -q "pytest" || { echo -e "${RED}✗ Pytest not installed${NC}"; FAILED=1; }

if [ $FAILED -eq 1 ]; then
    echo -e "${RED}Missing dependencies. Install with: pip install -r requirements-dev.txt${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All dependencies installed${NC}"
echo ""

# 1. Code formatting check (Black)
echo "1️⃣  Checking code formatting (Black)..."
if black --check app/ 2>&1 | grep -q "would reformat"; then
    echo -e "${RED}✗ Code formatting issues found${NC}"
    echo "  Run: black app/ to fix"
    FAILED=1
else
    echo -e "${GREEN}✓ Code formatting OK${NC}"
fi
echo ""

# 2. Linting (Ruff)
echo "2️⃣  Running linter (Ruff)..."
if ruff check app/ --quiet; then
    echo -e "${GREEN}✓ Linting passed${NC}"
else
    echo -e "${RED}✗ Linting issues found${NC}"
    echo "  Run: ruff check app/ --fix to auto-fix"
    FAILED=1
fi
echo ""

# 3. Type checking (MyPy)
echo "3️⃣  Type checking (MyPy)..."
if mypy app/ --ignore-missing-imports --no-error-summary 2>&1 | grep -q "error:"; then
    echo -e "${YELLOW}⚠ Type checking warnings (non-blocking)${NC}"
    # Don't fail on type errors (informational only)
else
    echo -e "${GREEN}✓ Type checking passed${NC}"
fi
echo ""

# 4. Security linting (Bandit)
echo "4️⃣  Security scan (Bandit)..."
if bandit -r app/ -q 2>&1 | grep -q "Issue:"; then
    echo -e "${YELLOW}⚠ Security issues found (review manually)${NC}"
    bandit -r app/ -f screen | head -20
else
    echo -e "${GREEN}✓ No security issues${NC}"
fi
echo ""

# 5. Tests
echo "5️⃣  Running tests..."
if pytest tests/ -v --tb=short; then
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo -e "${RED}✗ Tests failed${NC}"
    FAILED=1
fi
echo ""

# 6. Test coverage
echo "6️⃣  Checking test coverage..."
COVERAGE=$(pytest tests/ --cov=app --cov-report=term-missing --cov-report=json -q | grep "TOTAL" | awk '{print $4}' | tr -d '%')
if [ ! -z "$COVERAGE" ]; then
    if [ $(echo "$COVERAGE >= 80" | bc) -eq 1 ]; then
        echo -e "${GREEN}✓ Test coverage: ${COVERAGE}% (target: ≥80%)${NC}"
    else
        echo -e "${YELLOW}⚠ Test coverage: ${COVERAGE}% (target: ≥80%)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Could not determine coverage${NC}"
fi
echo ""

# 7. Check for TODOs and FIXMEs
echo "7️⃣  Checking for TODOs/FIXMEs..."
TODO_COUNT=$(grep -r "TODO\|FIXME" app/ --exclude-dir=__pycache__ | wc -l)
if [ $TODO_COUNT -gt 0 ]; then
    echo -e "${YELLOW}⚠ Found $TODO_COUNT TODO/FIXME comments${NC}"
    grep -rn "TODO\|FIXME" app/ --exclude-dir=__pycache__ | head -5
else
    echo -e "${GREEN}✓ No TODOs/FIXMEs${NC}"
fi
echo ""

# Summary
echo "=============================="
if [ $FAILED -eq 1 ]; then
    echo -e "${RED}❌ Quality check FAILED${NC}"
    echo "Please fix the issues above before committing."
    exit 1
else
    echo -e "${GREEN}✅ All quality checks PASSED${NC}"
    echo "Code is ready for commit/deployment!"
    exit 0
fi
