FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only pyproject.toml first for better layer caching
COPY pyproject.toml .

# Install dependencies by parsing pyproject.toml directly
# Single source of truth: all dependencies defined in pyproject.toml only
RUN pip install --no-cache-dir --upgrade pip && \
    # Parse and install production dependencies
    python -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); \
        deps = d['project']['dependencies']; \
        [print(dep) for dep in deps]" | xargs pip install --no-cache-dir && \
    # Parse and install dev dependencies
    python -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); \
        deps = d['project']['optional-dependencies']['dev']; \
        [print(dep) for dep in deps]" | xargs pip install --no-cache-dir

# Copy source code and tests after dependencies are installed
COPY src/ ./src/
COPY tests/ ./tests/

# Set Python path to find the module
ENV PYTHONPATH=/app/src

# Environment variables (can be overridden at runtime)
ENV TECHWORD_TRANSLATOR_API_URL=""
ENV MCP_SERVER_NAME="TechWord Translator"
ENV MCP_SERVER_VERSION="1.0.0"

# Run the MCP server
CMD ["python", "-m", "techword_translator.server"]
