#!/bin/bash
# Test runner for AGI MCP Server

set -e

echo "========================================="
echo "AGI MCP Server Test Suite"
echo "========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}pytest not found. Installing dependencies...${NC}"
    pip install -r requirements.txt
fi

# Run different test suites based on argument
case "${1:-all}" in
    unit)
        echo -e "${GREEN}Running unit tests...${NC}"
        pytest tests/ -m "not integration" -v
        ;;
    integration)
        echo -e "${GREEN}Running integration tests...${NC}"
        pytest tests/test_integration.py -v
        ;;
    meta)
        echo -e "${GREEN}Running meta-learning tests...${NC}"
        pytest tests/test_meta_learning_tools.py -v
        ;;
    multiagent)
        echo -e "${GREEN}Running multi-agent tests...${NC}"
        pytest tests/test_multi_agent_tools.py -v
        ;;
    skill)
        echo -e "${GREEN}Running skill evolution tests...${NC}"
        pytest tests/test_skill_evolution_tools.py -v
        ;;
    goal)
        echo -e "${GREEN}Running goal decomposition tests...${NC}"
        pytest tests/test_goal_decomposition_tools.py -v
        ;;
    context)
        echo -e "${GREEN}Running context synthesis tests...${NC}"
        pytest tests/test_context_synthesis_tools.py -v
        ;;
    darwin)
        echo -e "${GREEN}Running Darwin Gödel tests...${NC}"
        pytest tests/test_darwin_godel_tools.py -v
        ;;
    server)
        echo -e "${GREEN}Running server initialization tests...${NC}"
        pytest tests/test_server_initialization.py -v
        ;;
    coverage)
        echo -e "${GREEN}Running tests with coverage report...${NC}"
        pytest tests/ --cov=server --cov-report=term-missing --cov-report=html
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    quick)
        echo -e "${GREEN}Running quick test suite (no coverage)...${NC}"
        pytest tests/ -v --no-cov
        ;;
    all)
        echo -e "${GREEN}Running all tests with coverage...${NC}"
        pytest tests/ -v
        ;;
    *)
        echo -e "${RED}Usage: $0 {all|unit|integration|meta|multiagent|skill|goal|context|darwin|server|coverage|quick}${NC}"
        exit 1
        ;;
esac

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}All tests passed!${NC}"
    echo -e "${GREEN}=========================================${NC}"
else
    echo -e "${RED}=========================================${NC}"
    echo -e "${RED}Some tests failed!${NC}"
    echo -e "${RED}=========================================${NC}"
fi

exit $exit_code
