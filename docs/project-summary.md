# TechWord Translator MCP Server - Project Summary

## Overview

Professional MCP (Model Context Protocol) server that provides translation services for technical terms across English, Spanish, and German. Built with FastMCP and powered by the TechWordTranslator API.

## Architecture

### Core Components

1. **server.py** (`src/techword_translator/server.py`) — Thin entry point: registers tools and starts FastMCP
2. **tools.py** (`src/techword_translator/tools.py`) — All 5 MCP tool implementations as plain async functions
3. **container.py** (`src/techword_translator/container.py`) — Service singleton lifecycle (dependency container)
4. **APIClient** (`src/techword_translator/services/api_client.py`) — Async HTTP client using httpx with pagination support
5. **Data Models** (`src/techword_translator/models/word.py`) — `Word` and `TranslationItem` Pydantic models

### MCP Tools

| Tool | Description | Parameters |
| ---- | ----------- | ---------- |
| `translate_term` | Translate between languages | term, from_locale, to_locale |
| `search_tech_terms` | Search with partial matching | term, locale (optional), limit |
| `get_all_translations` | Get all translations for a term | term, source_locale |
| `get_term_details` | Get detailed info by ID | word_id |
| `list_tech_terms` | List with pagination | page_size, cursor |

### Supported Languages

- **en** - English
- **es** - Spanish (Español)
- **de** - German (Deutsch)

## Project Structure

```text
TechWordTranslatorMCP-Server/
├── .docker/
│   └── dev/
│       └── Dockerfile           # Dev Docker image (Python 3.12, Debian Trixie)
├── src/
│   └── techword_translator/
│       ├── __init__.py
│       ├── server.py            # Thin entry point
│       ├── tools.py             # 5 MCP tool implementations
│       ├── container.py         # Service dependency container
│       ├── formatters.py        # Response formatters
│       ├── models/
│       │   ├── __init__.py
│       │   └── word.py          # Word, TranslationItem models
│       └── services/
│           ├── api_client.py    # Async HTTP client
│           ├── search.py        # Search logic
│           └── translator.py    # Translation logic
├── tests/
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_api_client.py
│   ├── test_search_service.py
│   ├── test_translator_service.py
│   ├── test_formatters.py
│   └── test_server_integration.py
├── docs/                        # Documentation
├── pyproject.toml
├── docker-compose.yml
├── .env.example
├── .markdownlint.json
└── README.md
```

## Technical Stack

### Core Dependencies

- **FastMCP** (>=3.1.0) - MCP server framework
- **httpx** (>=0.28.0) - Async HTTP client
- **Pydantic** (>=2.12.0) - Data validation
- **python-dotenv** (>=1.2.0) - Environment management

### Python Version

- Python 3.12 or higher

## Features

### Security

- Secure configuration via environment variables
- No hardcoded secrets
- Non-root Docker user with host UID/GID matching

### Performance

- Async/await throughout
- HTTP connection pooling
- Efficient cursor-based pagination

### Developer Experience

- Type hints everywhere
- Pydantic validation
- 151 tests, 99% coverage
- Read-only volume mounts in Docker dev environment

## Installation Methods

### 1. Docker (Recommended)

```bash
docker compose build
docker compose up -d
```

### 2. Local Python

```bash
pip install -e .
python -m techword_translator
```

### 3. Deployment

See [deployment.md](deployment.md) for detailed instructions.

## Configuration

### Environment Variables

```env
TECHWORD_TRANSLATOR_API_URL=https://api.example.com
MCP_SERVER_NAME=TechWord Translator
MCP_SERVER_VERSION=0.3.0
```

### Claude Desktop Integration

```json
{
  "mcpServers": {
    "techword-translator": {
      "command": "python",
      "args": ["-m", "techword_translator"],
      "env": {
        "TECHWORD_TRANSLATOR_API_URL": "https://your-api-url.com"
      }
    }
  }
}
```

## Usage Examples

### Translate a term

```python
translate_term(term="computer", from_locale="en", to_locale="es")
# Output: computer (en) → computadora (es)
```

### Search for terms

```python
search_tech_terms(term="soft", locale="en", limit=5)
# Returns matching terms containing "soft"
```

### Get all translations

```python
get_all_translations(term="database", source_locale="en")
# Returns translations in all available languages
```

## Development

### Running Tests

```bash
docker compose run --rm techword-mcp pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

### Building Docker Image

```bash
docker compose build
```

## API Integration

This server integrates with the [TechWordTranslator API](https://github.com/josego85/TechWordTranslatorAPI):

- RESTful endpoints with versioning
- Cursor-based pagination
- Comprehensive translation database

## Documentation

| Document | Purpose |
| -------- | ------- |
| [README.md](../README.md) | Main project documentation |
| [quickstart.md](quickstart.md) | Get started in 5 minutes |
| [docker-setup.md](docker-setup.md) | Docker configuration guide |
| [deployment.md](deployment.md) | Production deployment guide |
| [testing.md](testing.md) | Testing guide and coverage |
| [development.md](development.md) | Developer guide and architecture |

## License

GNU General Public License v3.0 - see [LICENSE](../LICENSE) file

## Credits

- **TechWordTranslator API** - Backend API
- **FastMCP** - MCP framework
- **Anthropic** - MCP protocol specification

## Version

Current version: **0.3.0**

Status: ✅ Production Ready

---

Built with FastMCP and Python 3.12
