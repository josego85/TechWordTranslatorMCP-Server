# TechWord Translator MCP Server - Project Summary

## Overview
Professional MCP (Model Context Protocol) server that provides translation services for technical terms across English, Spanish, and German. Built with FastMCP and powered by the TechWordTranslator API.

## Architecture

### Core Components

1. **Server Module** (`src/techword_mcp/server.py`)
   - FastMCP server implementation
   - 5 MCP tools for technical term translation
   - Async request handling
   - Automatic cleanup on shutdown

2. **HTTP Client** (`src/techword_mcp/client.py`)
   - Async HTTP client using httpx
   - Connection reuse and pooling
   - Smart pagination handling

3. **Data Models** (`src/techword_mcp/models.py`)
   - Pydantic models for type safety
   - Word, Translation, and response models
   - Built-in validation

### MCP Tools

| Tool | Description | Parameters |
|------|-------------|-----------|
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

```
TechWordTranslatorMCP-Server/
├── src/
│   └── techword_mcp/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Entry point
│       ├── server.py            # FastMCP server (5 tools)
│       ├── client.py            # Async HTTP client
│       └── models.py            # Pydantic models
├── tests/
│   ├── __init__.py
│   └── test_client.py           # Client tests
├── pyproject.toml               # Python project configuration
├── Dockerfile                   # Docker container definition
├── docker-compose.yml           # Docker Compose configuration
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── LICENSE                      # GPL-3.0 License
├── README.md                    # Main documentation
├── QUICKSTART.md                # Quick start guide
├── DOCKER_SETUP.md              # Docker installation guide
├── DEPLOYMENT.md                # Deployment guide
├── PROJECT_SUMMARY.md           # This file
└── claude_desktop_config.example.json  # Claude Desktop config

Total: 4 directories, 21 files
```

## Technical Stack

### Core Dependencies
- **FastMCP** (>=0.2.0) - MCP server framework
- **httpx** (>=0.27.0) - Async HTTP client
- **Pydantic** (>=2.0.0) - Data validation
- **python-dotenv** (>=1.0.0) - Environment management

### Python Version
- Python 3.10 or higher

## Features

### Security
✓ Secure configuration via environment variables
✓ No hardcoded secrets
✓ Docker security best practices

### Performance
✓ Async/await throughout
✓ HTTP connection pooling
✓ Efficient cursor-based pagination
✓ Minimal memory footprint

### Developer Experience
✓ Type hints everywhere
✓ Pydantic validation
✓ Clear error messages
✓ Comprehensive documentation
✓ Example configurations

### Deployment Options
✓ Docker / Docker Compose
✓ Local installation

## Installation Methods

### 1. Docker (Quick Testing)
```bash
docker compose build
docker compose up -d
```

### 2. Local Python (Claude Desktop)
```bash
pip install -e .
python -m techword_mcp.server
```

### 3. Cloud Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions

## Configuration

### Environment Variables
```env
TECHWORD_TRANSLATOR_API_URL=https://api.example.com
MCP_SERVER_NAME=TechWord Translator
MCP_SERVER_VERSION=1.0.0
```

### Claude Desktop Integration
```json
{
  "mcpServers": {
    "techword-translator": {
      "command": "python",
      "args": ["-m", "techword_mcp.server"],
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
pytest tests/
```

### Code Formatting
```bash
black src/
ruff check src/
```

### Building Docker Image
```bash
docker build -t techword-mcp .
```

## API Integration

This server integrates with the [TechWordTranslator API](https://github.com/josego85/TechWordTranslatorAPI):

- RESTful endpoints with versioning
- Cursor-based pagination
- Comprehensive translation database

## Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Complete project documentation |
| [QUICKSTART.md](QUICKSTART.md) | Get started in 5 minutes |
| [DOCKER_SETUP.md](DOCKER_SETUP.md) | Docker installation guide |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment guide |

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

GNU General Public License v3.0 - see [LICENSE](LICENSE) file

## Credits

- **TechWordTranslator API** - Backend API
- **FastMCP** - MCP framework
- **Anthropic** - MCP protocol specification

## Support

- GitHub Issues: Report bugs and request features
- Documentation: Comprehensive guides included
- MCP Community: Join the MCP developer community

## Version

Current version: **1.0.0**

Status: ✅ Production Ready

---

Built with ❤️ using FastMCP and Python
