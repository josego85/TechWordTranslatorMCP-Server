FROM python:3.12-slim-trixie

# Build args — pass host UID/GID so volume-mounted files are accessible
# Usage: docker compose build (docker-compose.yml passes these automatically)
ARG UID=1000
ARG GID=1000

# Prevent .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Create non-root user with the same UID/GID as the host developer
RUN groupadd --gid ${GID} appgroup && \
    useradd --uid ${UID} --gid appgroup --no-create-home --shell /sbin/nologin appuser

# Install build deps, install Python packages, then remove build deps in one layer
COPY pyproject.toml .

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    pip install --no-cache-dir --upgrade pip && \
    python -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); \
        deps = d['project']['dependencies']; \
        [print(dep) for dep in deps]" | xargs pip install --no-cache-dir && \
    python -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); \
        deps = d['project']['optional-dependencies']['dev']; \
        [print(dep) for dep in deps]" | xargs pip install --no-cache-dir && \
    apt-get purge -y --auto-remove gcc && \
    rm -rf /var/lib/apt/lists/* /root/.cache

# src/ and tests/ are volume-mounted at runtime — no COPY needed here
# This keeps the image lean and ensures live code changes are reflected immediately

# Ensure the app directory is owned by appuser
RUN chown appuser:appgroup /app

USER appuser

# Environment variables (overridden via docker-compose or --env at runtime)
ENV TECHWORD_TRANSLATOR_API_URL="" \
    MCP_SERVER_NAME="TechWord Translator" \
    MCP_SERVER_VERSION="0.3.0"

CMD ["python", "-m", "techword_translator.server"]
