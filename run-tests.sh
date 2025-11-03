#!/bin/bash

# TechWord Translator MCP Server - Test Runner Script
# Simple script to run tests inside Docker container

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🧪 TechWord Translator MCP Server - Test Suite${NC}"
echo "================================================"

# Parse command line arguments
COMMAND=${1:-"all"}

case $COMMAND in
  "all")
    echo -e "${YELLOW}Running all tests...${NC}"
    docker-compose run --rm techword-mcp pytest -v --cov=src/techword_translator --cov-report=term-missing
    ;;

  "unit")
    echo -e "${YELLOW}Running unit tests only...${NC}"
    docker-compose run --rm techword-mcp pytest tests/test_models.py tests/test_api_client.py tests/test_search_service.py tests/test_translator_service.py tests/test_formatters.py -v
    ;;

  "integration")
    echo -e "${YELLOW}Running integration tests only...${NC}"
    docker-compose run --rm techword-mcp pytest tests/test_server_integration.py -v
    ;;

  "coverage")
    echo -e "${YELLOW}Running tests with detailed coverage report...${NC}"
    docker-compose run --rm techword-mcp pytest --cov=src/techword_translator --cov-report=term-missing --cov-report=html --cov-branch -v
    echo -e "${GREEN}✓ Coverage report generated in htmlcov/index.html${NC}"
    ;;

  "build")
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker-compose build
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
    ;;

  "shell")
    echo -e "${YELLOW}Opening shell in container...${NC}"
    docker-compose run --rm techword-mcp /bin/bash
    ;;

  *)
    echo -e "${YELLOW}Running specific test: $@${NC}"
    docker-compose run --rm techword-mcp pytest "$@" -v
    ;;
esac

echo -e "${GREEN}✓ Done${NC}"
