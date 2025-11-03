# Deployment Guide

This guide explains how to deploy the TechWord Translator MCP Server as a public service.

## Deployment Options

### 1. Docker (Self-hosted)

Deploy on any server with Docker installed.

**Steps:**

1. Build the image:
   ```bash
   docker build -t techword-mcp .
   ```

2. Run with environment variables:
   ```bash
   docker run -d \
     -e TECHWORD_TRANSLATOR_API_URL=your-api-url \
     --name techword-mcp \
     techword-mcp
   ```

**Using Docker Compose:**

1. Create a `.env` file:
   ```env
   TECHWORD_TRANSLATOR_API_URL=your-api-url
   ```

2. Start the service:
   ```bash
   docker-compose up -d
   ```

## Connecting Clients to Public Server

### For MCP Clients using stdio

Since MCP servers typically communicate via stdio (standard input/output), deploying as a "public server" requires a different approach:

**Option A: MCP-over-HTTP Proxy**
You'll need to create an HTTP wrapper that:
1. Accepts MCP protocol messages over HTTP/WebSocket
2. Forwards them to the stdio-based MCP server
3. Returns responses back to the client

**Option B: Direct Distribution**
Instead of hosting centrally, distribute the server as a package:
1. Publish to PyPI: `pip install techword-translator-mcp`
2. Users run locally: `python -m techword_mcp.server`
3. Configuration via environment variables

**Option C: Claude Desktop Integration**
Users install locally and configure in Claude Desktop:
```json
{
  "mcpServers": {
    "techword-translator": {
      "command": "python",
      "args": ["-m", "techword_mcp.server"]
    }
  }
}
```

## Publishing to PyPI

To make your server publicly available via PyPI:

1. Create account at https://pypi.org

2. Install build tools:
   ```bash
   pip install build twine
   ```

3. Build the package:
   ```bash
   python -m build
   ```

4. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

5. Users can then install:
   ```bash
   pip install techword-translator-mcp
   ```

## Security Considerations

When deploying publicly:

1. **Environment Variables**: Use secure secret management
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **Monitoring**: Set up logging and monitoring
4. **Updates**: Keep dependencies updated for security patches

## Monitoring and Logs

### Docker
```bash
docker logs -f techword-mcp
```

### Local Installation
Check logs in your terminal or use log files if configured

## Scaling Considerations

- MCP servers are typically lightweight
- Most deployments work well with a single instance
- For high traffic, consider:
  - Load balancing multiple instances
  - Caching API responses
  - Connection pooling for HTTP requests

## Troubleshooting

### Server won't start
- Check environment variables are set correctly
- Verify API credentials are valid
- Check logs for error messages

### Connection issues
- Ensure the API base URL is accessible
- Check firewall rules
- Verify network connectivity

### Performance issues
- Monitor API response times
- Check for rate limiting from the upstream API
- Consider implementing caching
