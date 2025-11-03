# Docker Setup Guide

This guide explains how to install and run the TechWord Translator MCP Server using Docker.

## Prerequisites

### Required Software

1. **Docker Desktop** or **Docker Engine**
   - **Windows/Mac**: Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - **Linux**: Install [Docker Engine](https://docs.docker.com/engine/install/)

2. **Docker Compose** (optional, but recommended)
   - Included with Docker Desktop
   - Linux users: Follow [installation guide](https://docs.docker.com/compose/install/)

### Verify Installation

Check that Docker is installed correctly:

```bash
docker --version
docker-compose --version
```

You should see version numbers for both commands.

## Configuration

### 1. Environment Variables

The MCP server requires the following environment variables to connect to the TechWordTranslator API:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `TECHWORD_TRANSLATOR_API_URL` | Yes | Base URL of the API | `https://api.techwordtranslator.com` |

*Note: Email and password are optional if the API allows unauthenticated access to public endpoints.

### 2. Create Environment File

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit the `.env` file with your credentials:

```env
TECHWORD_TRANSLATOR_API_URL=https://your-api-url.com
```

**Important**: Never commit the `.env` file to version control!

## Installation Methods

### Method 1: Using Docker Compose (Recommended)

This is the easiest method for local development and testing.

#### Step 1: Verify docker-compose.yml

Ensure the `docker-compose.yml` file exists in your project root:

```yaml
version: '3.8'

services:
  techword-mcp:
    build: .
    container_name: techword-translator-mcp
    environment:
      - TECHWORD_TRANSLATOR_API_URL=${TECHWORD_TRANSLATOR_API_URL}
      - MCP_SERVER_NAME=TechWord Translator
      - MCP_SERVER_VERSION=1.0.0
    restart: unless-stopped
    stdin_open: true
    tty: true
```

#### Step 2: Build and Run

```bash
# Build the Docker image
docker compose build --no-cache

# Start the container
docker compose up -d

# View logs
docker compose logs -f

# Stop the container
docker compose down
```

#### Step 3: Verify Running Container

```bash
docker compose ps
```

You should see the `techword-translator-mcp` container running.

### Method 2: Using Docker CLI

If you prefer to use Docker commands directly:

#### Step 1: Build the Image

```bash
docker build -t techword-mcp .
```

This creates a Docker image named `techword-mcp`.

#### Step 2: Run the Container

**Option A: Using environment variables directly**

```bash
docker run -d \
  --name techword-translator-mcp \
  -e TECHWORD_TRANSLATOR_API_URL=https://your-api-url.com \
  -e MCP_SERVER_NAME="TechWord Translator" \
  -e MCP_SERVER_VERSION="1.0.0" \
  techword-mcp
```

**Option B: Using .env file**

```bash
docker run -d \
  --name techword-translator-mcp \
  --env-file .env \
  techword-mcp
```

#### Step 3: Verify Running Container

```bash
# List running containers
docker ps

# View logs
docker logs -f techword-translator-mcp

# Check container status
docker inspect techword-translator-mcp
```

## Container Management

### View Logs

```bash
# Docker Compose
docker-compose logs -f

# Docker CLI
docker logs -f techword-translator-mcp
```

### Stop Container

```bash
# Docker Compose
docker-compose stop

# Docker CLI
docker stop techword-translator-mcp
```

### Start Container

```bash
# Docker Compose
docker-compose start

# Docker CLI
docker start techword-translator-mcp
```

### Restart Container

```bash
# Docker Compose
docker-compose restart

# Docker CLI
docker restart techword-translator-mcp
```

### Remove Container

```bash
# Docker Compose (stops and removes)
docker-compose down

# Docker CLI
docker stop techword-translator-mcp
docker rm techword-translator-mcp
```

### Remove Image

```bash
docker rmi techword-mcp
```

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker-compose logs
# or
docker logs techword-translator-mcp
```

**Common issues:**
- Missing environment variables
- Invalid API credentials
- API endpoint not accessible

### Rebuild After Code Changes

```bash
# Docker Compose
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Docker CLI
docker stop techword-translator-mcp
docker rm techword-translator-mcp
docker build --no-cache -t techword-mcp .
docker run -d --name techword-translator-mcp --env-file .env techword-mcp
```

### View Container Resource Usage

```bash
docker stats techword-translator-mcp
```

### Access Container Shell

```bash
# Docker Compose
docker-compose exec techword-mcp /bin/sh

# Docker CLI
docker exec -it techword-translator-mcp /bin/sh
```

### Test API Connection

From inside the container:

```bash
docker exec -it techword-translator-mcp python -c "
from techword_mcp.client import TechWordAPIClient
import asyncio

async def test():
    async with TechWordAPIClient() as client:
        words = await client.get_words(per_page=5)
        print(f'Connected! Found {len(words.data)} words')

asyncio.run(test())
"
```

## Production Deployment

### Security Best Practices

1. **Use a Non-Root User** (add to Dockerfile):
```dockerfile
RUN adduser -D mcp
USER mcp
```

2. **Scan for Vulnerabilities**:
```bash
docker scan techword-mcp
```

### Resource Limits

Add resource constraints to `docker-compose.yml`:

```yaml
services:
  techword-mcp:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

Or with Docker CLI:

```bash
docker run -d \
  --name techword-translator-mcp \
  --memory="512m" \
  --cpus="0.5" \
  --env-file .env \
  techword-mcp
```

### Health Checks

Add to `docker-compose.yml`:

```yaml
services:
  techword-mcp:
    # ... other config ...
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Automatic Restart

The container is configured to restart automatically:

```yaml
restart: unless-stopped
```

This ensures the container restarts after crashes or system reboots.

## Using with MCP Clients

Since this is an MCP server using stdio (standard input/output), you cannot directly connect to it over HTTP. Instead:

### Option 1: Local Integration

Run the container locally and configure your MCP client to use it:

```json
{
  "mcpServers": {
    "techword-translator": {
      "command": "docker",
      "args": ["exec", "-i", "techword-translator-mcp", "python", "-m", "techword_mcp.server"]
    }
  }
}
```

### Option 2: Install Locally (Recommended for MCP)

For Claude Desktop and other MCP clients, it's better to install locally:

```bash
pip install -e .
```

Then configure:

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

## Docker Hub (Optional)

### Tag and Push to Docker Hub

If you want to share your image:

```bash
# Login to Docker Hub
docker login

# Tag the image
docker tag techword-mcp your-dockerhub-username/techword-mcp:latest

# Push to Docker Hub
docker push your-dockerhub-username/techword-mcp:latest
```

### Pull and Run from Docker Hub

Others can then use:

```bash
docker pull your-dockerhub-username/techword-mcp:latest
docker run -d --name techword-translator-mcp --env-file .env your-dockerhub-username/techword-mcp:latest
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best practices for writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [MCP Server Documentation](https://modelcontextprotocol.io/)

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review container logs
3. Verify environment variables are set correctly
4. Ensure the API endpoint is accessible
5. Open an issue on GitHub with logs and configuration
