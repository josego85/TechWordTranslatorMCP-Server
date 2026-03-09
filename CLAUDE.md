# CLAUDE.md — TechWordTranslator MCP Server

> Developer guide for AI assistants and contributors working on this codebase.

---

## Project Overview

**TechWordTranslator MCP Server** is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that provides translation services for technical terms across English (`en`), Spanish (`es`), and German (`de`). It delegates all data to the [TechWordTranslator API](https://github.com/josego85/TechWordTranslatorAPI) via HTTP.

- **Language**: Python 3.12+
- **MCP Framework**: FastMCP ≥ 3.1.0
- **Version**: 0.3.0
- **License**: GNU GPL v3.0

---

## Architecture

### Layered Structure

```
MCP Client (Claude/Cursor)
       │
   tools.py            ← 5 MCP tool handlers (presentation layer)
       │
   formatters.py       ← Response formatting (presentation layer)
       │
   services/           ← Business logic
   ├── translator.py   ← Translation coordination
   ├── search.py       ← Search + pagination iteration
   └── api_client.py   ← HTTP wrapper (httpx.AsyncClient)
       │
   models/             ← Domain models (Pydantic)
   ├── word.py         ← Word, TranslationItem
   └── api.py          ← WordsResponse, PaginationMeta
       │
   container.py        ← Service singletons (DI/IoC)
   server.py           ← FastMCP registration + dotenv load
```

### Key Design Decisions

- **Stateless tools**: Tools return formatted strings; no server-side state persisted between invocations.
- **Service singletons**: `container.py` uses module-level globals + `@asynccontextmanager` for lazy initialization and reuse across tool calls.
- **No database**: All data lives in the external TechWordTranslator API. This server is a pure proxy with formatting.
- **Async I/O throughout**: All services and tools are `async def`. Never use sync I/O in the hot path.
- **Pydantic v2 for validation**: All API responses are validated via Pydantic models before use.
- **Early-return error pattern in tools**: Tools return a user-readable error string rather than raising exceptions.

---

## MCP Tools (5 total)

All tools are defined in `src/techword_translator/tools.py`.

| Tool | Parameters | Purpose |
|------|-----------|---------|
| `translate_term` | `term`, `from_locale`, `to_locale` | Translate a single term between languages |
| `search_tech_terms` | `term`, `locale?`, `limit?` | Partial-match search across all terms |
| `get_all_translations` | `term`, `source_locale` | All translations of a term in a given language |
| `get_term_details` | `word_id` | Full detail by numeric ID |
| `list_tech_terms` | `page_size?`, `cursor?` | Cursor-paginated list of terms |

**Valid locales**: `en`, `es`, `de` — defined as `VALID_LOCALES` in `tools.py`.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TECHWORD_TRANSLATOR_API_URL` | **Yes** | — | Base URL of TechWordTranslator API |
| `MCP_SERVER_NAME` | No | `TechWord Translator` | Server name reported to MCP clients |
| `MCP_SERVER_VERSION` | No | `0.3.0` | Server version reported to MCP clients |

Copy `.env.example` to `.env` before running locally.

---

## Running the Server

### With Docker (recommended)

```bash
# Build
docker compose build

# Run MCP server
docker compose run --rm techword-mcp

# Run with custom API URL
docker compose run --rm -e TECHWORD_TRANSLATOR_API_URL=https://api.example.com techword-mcp
```

### Local Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
python -m techword_translator.server
```

---

## Testing

### Run Tests

```bash
# All tests with coverage
./run-tests.sh

# Unit tests only
./run-tests.sh unit

# Integration tests only
./run-tests.sh integration

# Full coverage report (HTML + XML)
./run-tests.sh coverage

# Inside Docker
docker compose run --rm techword-mcp pytest
```

### Test Statistics (v0.3.0)

- **151 tests** — 100% passing
- **99% code coverage** (branch coverage enabled)
- **~1.1s** execution time

### Test Architecture

| File | Purpose |
|------|---------|
| `tests/conftest.py` | Fixtures: sample models, service instances, HTTP mocks |
| `tests/test_models.py` | Pydantic model validation |
| `tests/test_api_client.py` | HTTP client with `respx` mocks |
| `tests/test_search_service.py` | Pagination iteration + filtering |
| `tests/test_translator_service.py` | Translation coordination |
| `tests/test_formatters.py` | Output formatting |
| `tests/test_server_integration.py` | End-to-end MCP tool flow |

**Critical test fixture**: `reset_services` in `conftest.py` is an `autouse` fixture that clears the service container globals between every test. **Do not remove it.**

### Testing Patterns

- Use `respx` (not `httpx`) for mocking HTTP calls.
- Use `pytest-mock` for async function mocks (`AsyncMock`).
- Never make real HTTP calls in tests — always mock `APIClient` at the `respx` or `AsyncMock` layer.
- Integration tests mock at the `AsyncMock` level on service methods, not HTTP.

---

## Code Quality

```bash
# Format
black src/ tests/

# Lint
ruff check src/ tests/

# Format + lint (combined)
black src/ tests/ && ruff check src/ tests/
```

**Style rules** (from `pyproject.toml`):
- Line length: **100 characters**
- Target: Python 3.12
- Black + Ruff enforced — no exceptions.

---

## Adding a New MCP Tool

1. **Add the tool function** in `src/techword_translator/tools.py`:
   ```python
   @mcp.tool()
   async def my_new_tool(param: str) -> str:
       async with get_services() as (api, search, translator):
           # business logic
           return ResponseFormatter.format_something(result)
   ```
2. **Add a formatter method** in `src/techword_translator/formatters.py` if needed.
3. **Add a service method** in the appropriate service if needed.
4. **Write tests** — minimum: unit test for the formatter + integration test for the tool.
5. **Update `docs/api-reference.md`** with parameters and example output.
6. **Update `CHANGELOG.md`** under `[Unreleased]`.

---

## Adding a New Service

1. Create `src/techword_translator/services/my_service.py`.
2. Inject dependencies via constructor (pass `APIClient` or other services).
3. Register the singleton in `container.py`.
4. Expose via the `get_services()` context manager tuple.
5. Write unit tests in `tests/test_my_service.py`.

---

## Adding a New Language

1. Add the locale code to `VALID_LOCALES` in `src/techword_translator/tools.py`.
2. Update docstrings in all affected tools.
3. Update `docs/api-reference.md`.
4. Ensure the TechWordTranslator API supports the new locale.

---

## Security

### What is safe here

- **No credentials**: The backend API is public and requires no auth tokens.
- **Input validation**: All inputs are validated by Pydantic before use.
- **Non-root Docker**: Container runs as `appuser` (UID/GID matched to host developer).
- **Read-only volumes**: Dev mounts use `:ro` to prevent container from writing to host.
- **HTTP timeouts**: `httpx.AsyncClient` is configured with a 30s timeout.
- **Pagination guard**: Search loop is capped at `max_pages=10` to prevent runaway requests.

### What to watch for

- **Never log or expose raw user input** without sanitization.
- **Never hardcode `TECHWORD_TRANSLATOR_API_URL`** in source code — always read from env.
- **Never add credentials/tokens** to `.env` (this file may be committed by mistake); use a secrets manager or runtime `-e` injection.
- **Never disable the pagination cap** without understanding the consequences.
- **If you add a new tool parameter** that is user-controlled and used in URL construction, sanitize it explicitly — do not rely solely on Pydantic.

---

## Project File Map (key files)

```
src/techword_translator/
├── __init__.py          # version = "0.3.0"
├── __main__.py          # module entry point
├── server.py            # FastMCP init + dotenv load (22 lines — keep minimal)
├── container.py         # service singletons + get_services() context manager
├── tools.py             # all 5 @mcp.tool() handlers
├── formatters.py        # ResponseFormatter static methods
├── models/
│   ├── word.py          # Word(id, word, translations=[TranslationItem])
│   └── api.py           # WordsResponse(data, meta), PaginationMeta
└── services/
    ├── api_client.py    # APIClient(base_url) — httpx wrapper
    ├── search.py        # SearchService — multi-page search
    └── translator.py    # TranslatorService — find + extract translation

tests/
├── conftest.py          # fixtures — MUST reset service container between tests
├── test_models.py
├── test_api_client.py
├── test_search_service.py
├── test_translator_service.py
├── test_formatters.py
└── test_server_integration.py

.docker/dev/Dockerfile   # multi-stage build, non-root user, parses pyproject.toml
docker-compose.yml       # dev environment, hot-reload ro volumes
pyproject.toml           # dependencies, build config, pytest config, black/ruff config
run-tests.sh             # test runner convenience script
docs/                    # 8 documentation files
```

---

## Common Pitfalls

| Pitfall | Correct Approach |
|---------|----------------|
| Making sync HTTP calls | Always use `await self.client.get(...)` |
| Raising exceptions in tool handlers | Return a user-readable error string instead |
| Adding state to service instances | Services are singletons — keep them stateless |
| Forgetting to reset container in tests | The `reset_services` autouse fixture handles this |
| Modifying `server.py` heavily | Keep it minimal — it's the framework glue layer |
| Using `requests` library | Use `httpx.AsyncClient` only |
| Hardcoding locale strings | Use `VALID_LOCALES` constant from `tools.py` |

---

## Dependency Update Policy

- Pin **minimum versions** with `>=` (not exact pins) in `pyproject.toml`.
- Run `./run-tests.sh coverage` after any dependency update to verify 99%+ coverage still passes.
- Python runtime requirement: `>=3.12` — do not lower this.

---

## Changelog Policy

- Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.
- Keep an `[Unreleased]` section at the top.
- On release: rename `[Unreleased]` → `[x.y.z] — YYYY-MM-DD`, bump `__init__.py` + `pyproject.toml` version.

---

## MCP Client Integration

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "techword-translator": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--network=host",
               "-e", "TECHWORD_TRANSLATOR_API_URL=http://localhost:8000",
               "techword-mcp"]
    }
  }
}
```

**Cursor** (`.cursor/mcp.json`): same structure as above.

---

## Quick Reference: Data Flow

```
User prompt → MCP client
  → tools.py tool handler
    → get_services() [container.py — lazy init]
      → SearchService / TranslatorService / APIClient
        → httpx.AsyncClient → TechWordTranslator API
          → WordsResponse (Pydantic validated)
        ← List[Word]
      ← filtered/translated result
    ← formatted string
  ← ResponseFormatter output
← Human-readable response
```
