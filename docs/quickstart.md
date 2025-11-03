# Quick Start Guide

Get the TechWord Translator MCP Server running in 5 minutes using Docker!

## Prerequisites
- Docker installed on your system
- TechWordTranslator API running (see [API repository](https://github.com/josego85/TechWordTranslatorAPI))

## Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/TechWordTranslatorMCP-Server.git
   cd TechWordTranslatorMCP-Server
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t techword-mcp .
   ```

3. **Run the container:**
   ```bash
   docker run --rm -i \
     -e TECHWORD_TRANSLATOR_API_URL=http://localhost:8000 \
     techword-mcp
   ```

   **Note:** If the API is running on your host machine, use:
   - Linux: `http://localhost:8000`
   - macOS/Windows: `http://host.docker.internal:8000`

4. **Test the server** by integrating with an MCP client (see below)

## Integrating with AI Tools

### Claude Desktop

Edit the configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add this configuration:

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

See the complete integration guide: [Cursor Setup Guide](cursor-setup.md)

## Testing the Tools

Once configured, you can use these tools in Claude:

### Translate a term
```
translate_term(term="computer", from_locale="en", to_locale="es")
```

### Search for terms
```
search_tech_terms(term="software", locale="en", limit=5)
```

### Get all translations
```
get_all_translations(term="database", source_locale="en")
```

## Troubleshooting

### Server won't start
1. Check your environment variables are set correctly
2. Verify the API URL is accessible
3. Check the logs for error messages

### Connection issues
1. Ensure the API base URL is correct
2. Check your internet connection

### Claude Desktop doesn't see the server
1. Restart Claude Desktop after adding the configuration
2. Check the configuration file syntax (valid JSON)
3. Verify the command path is correct
4. Check Claude Desktop logs for errors

## Need More Help?

- Full documentation: [README.md](../README.md)
- Docker guide: [docker-setup.md](docker-setup.md)
- Deployment guide: [deployment.md](deployment.md)
- Cursor IDE guide: [cursor-setup.md](cursor-setup.md)
- Open an issue: [GitHub Issues](https://github.com/yourusername/TechWordTranslatorMCP-Server/issues)
