# Laniakea Protocol Enhanced Dockerfile
# Multi-stage build for optimization and security

# Base stage
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --upgrade pip && \
    pip install black flake8 mypy pytest pytest-asyncio pytest-cov

# Install application dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

# Create application directory
WORKDIR /app

# Copy source code
COPY . .

# Set permissions
RUN chmod +x start_node.sh

# Expose port
EXPOSE 8000

# Development command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Testing stage
FROM development as testing

# Run tests
RUN python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

# Production stage
FROM base as production

# Create non-root user
RUN groupadd -r laniakea && \
    useradd -r -g laniakea -d /app -s /bin/bash laniakea

# Install application dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Create application directory
WORKDIR /app

# Copy source code
COPY --chown=laniakea:laniakea . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs && \
    chown -R laniakea:laniakea /app

# Set permissions
RUN chmod +x start_node.sh

# Switch to non-root user
USER laniakea

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Production command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Production with SSL
FROM production as production-ssl

# Copy SSL certificates (if available)
COPY --chown=laniakea:laniakea ./ssl/ /app/ssl/ || true

# Run with SSL
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "/app/ssl/key.pem", "--ssl-certfile", "/app/ssl/cert.pem", "--workers", "4"]

# Final stage (default to production)
FROM production