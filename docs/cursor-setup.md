# Cursor IDE Setup Guide

This guide explains how to configure the TechWord Translator MCP Server in Cursor IDE using Docker.

## Prerequisites

- Cursor IDE installed
- Docker installed and running
- TechWordTranslator API running (usually on `http://localhost:8000`)

## Setup Steps

### Step 1: Build the Docker Image

```bash
cd /path/to/TechWordTranslatorMCP-Server
docker build -t techword-mcp .
```

### Step 2: Configure Cursor MCP Settings

Edit the MCP settings file:

**Location by OS:**

- **macOS**: `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- **Linux**: `~/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- **Windows**: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

**Configuration:**

```json
{
  "mcpServers": {
    "techword-translator": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--network=host",
        "-e", "TECHWORD_TRANSLATOR_API_URL=http://localhost:8000",
        "techword-mcp"
      ]
    }
  }
}
```

**Important:** Replace with your actual API URL:
- `TECHWORD_TRANSLATOR_API_URL`: URL where your TechWordTranslator API is running

**Network Notes:**
- Linux: Use `http://localhost:8000` with `--network=host`
- macOS/Windows: Use `http://host.docker.internal:8000` and remove `--network=host`

### Step 3: Restart Cursor

Close and reopen Cursor IDE for the changes to take effect.

### Step 4: Verify Configuration

1. Open Claude chat in Cursor (Cmd/Ctrl + L)
2. You should see "techword-translator" in the list of available MCP servers
3. Try a test command:
   ```
   Can you translate the word "computer" from English to Spanish using the techword-translator?
   ```

## Available Tools

Once configured, you'll have access to these tools in Cursor:

### 1. translate_term
Translate a technical term from one language to another.

**Example:**
```
Translate "database" from English to Spanish
```

### 2. search_tech_terms
Search for technical terms in the database.

**Example:**
```
Search for terms containing "software"
```

### 3. get_all_translations
Get all available translations for a term.

**Example:**
```
Get all translations for "server" from English
```

### 4. get_term_details
Get detailed information about a term by ID.

**Example:**
```
Get details for word ID 42
```

### 5. list_tech_terms
List technical terms with pagination.

**Example:**
```
List 10 technical terms
```

## Supported Languages

- **en** - English
- **es** - Spanish (Español)
- **de** - German (Deutsch)

## Troubleshooting

### Server not showing in Cursor

**Check:**
1. Is Docker running? Run: `docker ps`
2. Is the Docker image built? Run: `docker images | grep techword-mcp`
3. Is the configuration file correct? Check JSON syntax
4. Did you restart Cursor after adding the configuration?

**Solution:**
```bash
# Rebuild the Docker image
cd /path/to/TechWordTranslatorMCP-Server
docker build -t techword-mcp .

# Restart Cursor
```

### Connection errors

**Check:**
1. Is the TechWordTranslator API running?
   ```bash
   curl http://localhost:8000/api/v1/words
   ```
2. Can you reach the API from Docker?
   ```bash
   docker run --rm --network=host techword-mcp python -c "import httpx; print(httpx.get('http://localhost:8000/api/v1/words').status_code)"
   ```

**Solution:**
Verify the API is accessible and restart Cursor.

### Docker image not found

**Error:** `Unable to find image 'techword-mcp:latest' locally`

**Solution:**
```bash
# Build the Docker image
cd /path/to/TechWordTranslatorMCP-Server
docker build -t techword-mcp .
```

## Testing the Integration

### Quick Test

In Cursor's Claude chat, try:

```
Use the techword-translator to:
1. Search for terms containing "data"
2. Translate "computer" from English to Spanish
3. Get all translations for "software" from English
```

### Expected Output

Claude should use the MCP tools and return results like:

```
1. Found terms: database, data structure, metadata...
2. computer (en) → computadora (es)
3. Translations for 'software':
   English: software
   Spanish: software
   German: Software
```

## Updating the Server

When you update the server code:

```bash
cd /path/to/TechWordTranslatorMCP-Server
git pull  # if using git
docker build -t techword-mcp .
```

Then restart Cursor.

## Alternative Configuration (Using Docker Compose)

You can use a Docker Compose setup:

1. Create a `docker-compose.yml` (already provided in the repo)
2. Create a `.env` file with your API URL
3. Start with: `docker compose up -d`
4. Use this Cursor configuration:

```json
{
  "mcpServers": {
    "techword-translator": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "techword-translator-mcp",
        "python",
        "-m",
        "techword_translator.server"
      ]
    }
  }
}
```

**Note:** The Docker container must be running for this to work.

## Additional Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Cursor Documentation](https://docs.cursor.sh/)
- [Project README](../README.md)
- [Docker Setup Guide](docker-setup.md)
- [Quick Start Guide](quickstart.md)

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Verify your API is running and accessible
3. Check Cursor's logs (Help → Show Logs)
4. Check Docker logs: `docker logs <container-id>`
5. Open an issue on GitHub with:
   - Cursor version
   - Docker version
   - Error messages
   - Configuration used
   - Steps to reproduce

---

**Pro Tip:** Keep your API URL configuration secure and never commit sensitive data to version control.
