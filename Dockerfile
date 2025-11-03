FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml first for better layer caching
COPY pyproject.toml .

# Install dependencies from pyproject.toml
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    "fastmcp>=0.2.0" \
    "httpx>=0.27.0" \
    "pydantic>=2.0.0" \
    "python-dotenv>=1.0.0"

# Copy source code
COPY src/ ./src/

# Set Python path to find the module
ENV PYTHONPATH=/app/src

# Environment variables (can be overridden at runtime)
ENV TECHWORD_TRANSLATOR_API_URL=""
ENV MCP_SERVER_NAME="TechWord Translator"
ENV MCP_SERVER_VERSION="1.0.0"

# Run the MCP server
CMD ["python", "-m", "techword_translator.server"]
