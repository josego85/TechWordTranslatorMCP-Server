# Development Guide

Guide for developers contributing to or extending the TechWord Translator MCP Server.

## Prerequisites

- Python 3.11+
- Docker (for containerized development)
- TechWordTranslator API running locally

## Project Structure

```
TechWordTranslatorMCP-Server/
├── docs/                       # Documentation
│   ├── quickstart.md          # Quick start guide
│   ├── api-reference.md       # API tools reference
│   ├── development.md         # This file
│   ├── docker-setup.md        # Docker setup guide
│   ├── deployment.md          # Deployment options
│   ├── cursor-setup.md        # Cursor IDE integration
│   └── project-summary.md     # Project overview
├── src/
│   └── techword_translator/   # Main package
│       ├── __init__.py
│       ├── __main__.py
│       ├── server.py          # FastMCP server with tools
│       ├── formatters.py      # Response formatting
│       ├── models/            # Data models
│       │   ├── __init__.py
│       │   ├── word.py        # Word & Translation (domain)
│       │   └── api.py         # API response models
│       └── services/          # Business logic
│           ├── __init__.py
│           ├── api_client.py  # HTTP client
│           ├── search.py      # Search logic
│           └── translator.py  # Translation service
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_client.py
├── Dockerfile                 # Docker container definition
├── docker-compose.yml         # Docker Compose config
├── pyproject.toml            # Package configuration
├── .env.example              # Environment variables template
├── .gitignore
└── README.md
```

## Architecture

The project follows **SOLID principles** with clear separation of concerns:

### Models (`models/`)
- **word.py**: Domain models (Word, Translation)
- **api.py**: API response models (WordsResponse, PaginationMeta)

### Services (`services/`)
- **api_client.py**: HTTP client for API communication
- **search.py**: Search and filtering logic
- **translator.py**: Translation coordination

### Other Components
- **server.py**: FastMCP server and tool definitions
- **formatters.py**: Response formatting for user display

## Dependency Management

**Single source of truth**: All dependencies are defined in `pyproject.toml` (PEP 621).

### Adding Dependencies

```toml
# pyproject.toml
[project]
dependencies = [
    "new-package>=1.0.0",  # Production dependency
]

[project.optional-dependencies]
dev = [
    "new-dev-tool>=2.0.0",  # Development dependency
]
```

Then rebuild:
```bash
docker-compose build
./run-tests.sh
```

**Note**: No `requirements.txt` needed. Docker parses `pyproject.toml` directly.

## Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/TechWordTranslatorMCP-Server.git
cd TechWordTranslatorMCP-Server
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your local API URL
```

Required variable:
```env
TECHWORD_TRANSLATOR_API_URL=http://localhost:8000
```

### 3. Build Docker Image

```bash
docker compose build
```

### 4. Run Tests

```bash
./run-tests.sh
```

## Code Style

### Formatting

We use [Black](https://black.readthedocs.io/) for code formatting:

```bash
# Format all code
black src/

# Check formatting
black --check src/
```

### Linting

We use [Ruff](https://github.com/astral-sh/ruff) for linting:

```bash
# Lint code
ruff check src/

# Fix auto-fixable issues
ruff check --fix src/
```

### Type Checking

We use type hints throughout the codebase:

```bash
# Type check with mypy
mypy src/
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_client.py
```

### Writing Tests

Place tests in `tests/` directory following the naming convention `test_*.py`.

Example:
```python
import pytest
from techword_translator.services import APIClient

def test_api_client_initialization():
    client = APIClient(base_url="http://localhost:8000")
    assert client.base_url == "http://localhost:8000"
```

## Adding New Features

### Adding a New Tool

1. **Add tool function** in `server.py`:
```python
@mcp.tool()
async def my_new_tool(param: str) -> str:
    """Tool description."""
    async with get_services() as (api, search, translator):
        # Implementation
        return ResponseFormatter.format_result(result)
```

2. **Add formatting method** in `formatters.py` if needed:
```python
@staticmethod
def format_my_result(data) -> str:
    """Format my result."""
    return f"Result: {data}"
```

3. **Update documentation**:
   - Add tool to `docs/api-reference.md`
   - Update README.md features list

### Adding a New Model

1. Create model in appropriate file:
   - Domain models → `models/word.py`
   - API models → `models/api.py`

2. Export from `models/__init__.py`:
```python
from .word import MyNewModel

__all__ = ["MyNewModel", ...]
```

### Adding a New Service

1. Create service in `services/`:
```python
# services/my_service.py
class MyService:
    """Service description."""

    def __init__(self, dependency):
        self.dependency = dependency
```

2. Export from `services/__init__.py`

3. Wire up in `server.py` if needed

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TECHWORD_TRANSLATOR_API_URL` | Backend API URL | - | Yes |
| `MCP_SERVER_NAME` | Server display name | "TechWord Translator" | No |
| `MCP_SERVER_VERSION` | Server version | "1.0.0" | No |

## Debugging

### Enable Debug Logging

Set environment variable:
```bash
export LOG_LEVEL=DEBUG
```

### Docker Debugging

```bash
# Run with debug output
docker run --rm -it \
  -e TECHWORD_TRANSLATOR_API_URL=http://localhost:8000 \
  techword-mcp

# Access container shell
docker run --rm -it techword-mcp /bin/bash
```

## Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Pull Request Guidelines

- Follow existing code style
- Add tests for new features
- Update documentation
- Keep commits atomic and well-described

## Best Practices

1. **SOLID Principles**: Each module has a single responsibility
2. **Type Hints**: Use type hints for all function signatures
3. **Docstrings**: Document all public functions and classes
4. **Error Handling**: Handle errors gracefully with user-friendly messages
5. **Async/Await**: Use async patterns for I/O operations

## Troubleshooting

### Common Issues

**ModuleNotFoundError**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/path/to/src
```

**API Connection Errors**
```bash
# Check API is running
curl http://localhost:8000/api/v1/words

# Verify network configuration in Docker
docker run --network=host ...  # Linux
# or
# Use host.docker.internal on macOS/Windows
```

## Related Documentation

- [API Reference](api-reference.md) - Available tools
- [Quick Start](quickstart.md) - Get started quickly
- [Docker Setup](docker-setup.md) - Docker configuration
- [Deployment](deployment.md) - Production deployment
