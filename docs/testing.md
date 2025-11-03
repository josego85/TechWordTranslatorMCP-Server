# Testing Guide

## Quick Start

```bash
# Run all tests
./run-tests.sh

# Run with coverage report
./run-tests.sh coverage

# Run specific test file
./run-tests.sh tests/test_models.py
```

## Test Results

- **158 tests** - 100% passing ✅
- **99% coverage** - 269/270 lines covered
- **~1.5s** execution time

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── test_models.py              # Domain models (30 tests)
├── test_api_client.py          # HTTP client (28 tests)
├── test_search_service.py      # Search logic (31 tests)
├── test_translator_service.py  # Translation (18 tests)
├── test_formatters.py          # Formatting (33 tests)
└── test_server_integration.py  # MCP tools (18 tests)
```

## Running Tests

### All Tests
```bash
./run-tests.sh
```

### Unit Tests Only
```bash
./run-tests.sh unit
```

### Integration Tests Only
```bash
./run-tests.sh integration
```

### Coverage Report
```bash
./run-tests.sh coverage
# Opens htmlcov/index.html
```

### Specific Test
```bash
docker-compose run --rm techword-mcp pytest tests/test_models.py::TestWord -v
```

## Local Development (without Docker)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest -v
```

## CI/CD Integration

```yaml
# Example GitHub Actions
- name: Run Tests
  run: docker-compose run --rm techword-mcp pytest --cov

- name: Upload Coverage
  uses: codecov/codecov-action@v2
```

## Coverage

View detailed coverage:
```bash
./run-tests.sh coverage
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Writing Tests

See `tests/README.md` for detailed guide on writing tests.
