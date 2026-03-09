# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- `CLAUDE.md` — developer guide for AI assistants and contributors covering architecture, MCP tools, testing patterns, security rules, common pitfalls, and extension guides
- `create_tech_word(english_word, es_translation?, de_translation?)` MCP tool — creates a new technical term with optional translations; word errors abort early, translation errors are reported inline per language without aborting the word creation
- `APIClient.create_word(english_word)` — POST `/api/v1/words` with auth headers; returns `Word` or raises `httpx.HTTPStatusError`
- `APIClient.create_translation(word_id, language, translation)` — POST `/api/v1/translations` with auth headers; returns raw response dict
- `ResponseFormatter.format_word_created(word_id, english_word, translations_created)` — formats creation result with `[lang]` tags and language names
- `TECHWORD_API_TOKEN` optional env var — Sanctum service token stored in `APIClient._auth_headers`; passed only to write methods (`create_word`, `create_translation`); read methods (`fetch_words`, `fetch_word`) never include the header, keeping public endpoints header-free
- `TECHWORD_API_TOKEN=${TECHWORD_API_TOKEN:-}` propagated in `docker-compose.yml` environment section
- 16 new tests: 3 for auth-header initialization, 3 for `create_word` (success + 422 + 401), 2 for `create_translation` (success + 422), 4 for `format_word_created`, 4 integration tests for `create_tech_word` — 167 total, 99% branch coverage maintained

### Changed

- `APIClient.__init__` reads `TECHWORD_API_TOKEN` at startup and stores `_auth_headers: dict[str, str]` — empty `{}` when absent, `{"Authorization": "Bearer <token>"}` when present; the shared `httpx.AsyncClient` headers remain unmodified (no token leak to public endpoints)

---

## [0.3.0] - 2026-03-08

### Added

- `container.py` — service singleton lifecycle extracted from `server.py` (SRP)
- `tools.py` — all 5 MCP tool functions as plain async functions, single `VALID_LOCALES` constant
- `.docker/dev/Dockerfile` — dedicated dev Dockerfile replacing root-level `Dockerfile`
- `.markdownlint.json` — linter config to allow duplicate headings across changelog versions

### Changed

- `server.py` refactored into thin entry point (22 lines): registers tools and runs MCP server
- `Word` model rewritten to match current API response (`translations: [{language, translation}]`)
- Upgraded to Python 3.12 and Debian 13 (Trixie) in Docker image
- All package constraints updated to match currently installed versions
- `docker-compose.yml`: Dockerfile path updated, volumes set to `:ro`, UID/GID build args added so container user matches host developer
- `coverage.xml` and `.venv/` added to `.gitignore`
- Docs updated to reflect v0.3.0: Python 3.12+, new module structure (`tools.py`, `container.py`), Dockerfile path, test count (151), package constraints
- `project-summary.md` rewritten — old `techword_mcp` module references replaced with `techword_translator`, structure and links corrected
- `docker-setup.md` docker-compose example updated to match current `docker-compose.yml`

### Removed

- Root-level `Dockerfile` (moved to `.docker/dev/`)
- `fetch_translation()` from `APIClient` (dead code — API embeds translations in word response)
- `htmlcov/` volume mount from docker-compose (HTML coverage report removed)

---

## [0.2.0] - 2025-11-03

### Added
- Comprehensive test suite with 158 tests and 99% code coverage
- `run-tests.sh` script for easy test execution
- Testing documentation in `docs/testing.md`
- pytest configuration in `pyproject.toml` with coverage reports
- Additional dev dependencies: `pytest-cov`, `pytest-mock`, `respx`
- Test fixtures and mocks in `tests/conftest.py`
- Unit tests for all core modules (models, API client, services, formatters)
- Integration tests for MCP server tools

### Changed
- Refactored Dockerfile to parse dependencies from `pyproject.toml` directly (single source of truth)
- Updated docker-compose.yml with development volumes for hot-reloading (`src/`, `tests/`, `htmlcov/`)
- Set default API URL in docker-compose.yml to production endpoint
- Enhanced development documentation with dependency management guide

---

## [0.1.0] - 2025-11-03

### Added
- Initial release of TechWord Translator MCP Server
- 5 MCP tools for technical term translation:
  - `translate_term` - Translate terms between English, Spanish, and German
  - `search_tech_terms` - Search technical terms database
  - `get_all_translations` - Get all translations for a term
  - `get_term_details` - Get detailed term information by ID
  - `list_tech_terms` - List terms with pagination support
- Docker support for easy deployment
- Docker Compose configuration for local development
- Integration guides for Claude Desktop and Cursor IDE
- Comprehensive documentation in `docs/` folder
- SOLID architecture with clean separation of concerns:
  - Domain models in `models/`
  - Business logic in `services/`
  - Response formatters
- GPL-3.0 License

### Technical Details
- Built with FastMCP framework
- Async HTTP client using httpx
- Pydantic models for data validation
- Python 3.11+ support
- Environment-based configuration
- Public API endpoints (no authentication required)

### Deployment
- Docker and Docker Compose support
- Local Python installation option
- Simplified deployment options (removed cloud platform configs)

[0.1.0]: https://github.com/yourusername/TechWordTranslatorMCP-Server/releases/tag/v0.1.0
