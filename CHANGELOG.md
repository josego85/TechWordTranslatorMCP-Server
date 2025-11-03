# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
