# TechWord Translator MCP Server

A public Model Context Protocol (MCP) server that provides translation services for technical terms across English, Spanish, and German. Built with FastMCP and powered by the [TechWordTranslator API](https://github.com/josego85/TechWordTranslatorAPI).

## ✨ Features

- 🌍 **Multi-language Translation**: Translate technical terms between English, Spanish, and German
- 🔍 **Smart Search**: Search for technical terms with partial matching
- 📚 **Comprehensive Database**: Access to a curated database of IT and technology terminology
- ⚡ **Fast & Efficient**: Built on FastMCP with async HTTP client
- 🔌 **Easy Integration**: Works with Claude Desktop, Cursor, and other MCP clients

## 🚀 Quick Start

```bash
# Build the Docker image
docker build -t techword-mcp .

# Run the server
docker run --rm -i \
  -e TECHWORD_TRANSLATOR_API_URL=http://localhost:8000 \
  techword-mcp
```

## 📖 Documentation

| Guide | Description |
|-------|-------------|
| [Quickstart](docs/quickstart.md) | Get up and running in 5 minutes |
| [API Reference](docs/api-reference.md) | Complete documentation of all 5 MCP tools |
| [Docker Setup](docs/docker-setup.md) | Detailed Docker configuration guide |
| [Cursor Setup](docs/cursor-setup.md) | Integrate with Cursor IDE |
| [Development](docs/development.md) | Developer guide and architecture |
| [Deployment](docs/deployment.md) | Production deployment options |

## 🛠️ Available Tools

The server provides 5 MCP tools for technical term translation and search. See the [API Reference](docs/api-reference.md) for complete details.

- `translate_term` - Translate a technical term from one language to another
- `search_tech_terms` - Search for technical terms in the database
- `get_all_translations` - Get all available translations for a term
- `get_term_details` - Get detailed information about a specific term
- `list_tech_terms` - List technical terms with pagination

## 🔧 Integration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "techword-translator": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i", "--network=host",
        "-e", "TECHWORD_TRANSLATOR_API_URL=http://localhost:8000",
        "techword-mcp"
      ]
    }
  }
}
```

### Cursor IDE

See the complete [Cursor Setup Guide](docs/cursor-setup.md) for integration steps.

## 🏗️ Architecture

Built following SOLID principles with a clean, modular architecture:

- **models/** - Domain models (Word, Translation) and API response models
- **services/** - Business logic (APIClient, SearchService, TranslatorService)
- **formatters.py** - Response formatting utilities
- **server.py** - FastMCP server with tool definitions

## 📋 Requirements

- Docker (recommended) or Python 3.11+
- TechWordTranslator API instance

### Environment Variables

- `TECHWORD_TRANSLATOR_API_URL` - Base URL of the TechWordTranslator API (required)

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [TechWordTranslator API](https://github.com/josego85/TechWordTranslatorAPI) - The backend API
- [FastMCP](https://github.com/jlowin/fastmcp) - FastMCP framework
- [Anthropic MCP](https://modelcontextprotocol.io/) - Model Context Protocol specification
