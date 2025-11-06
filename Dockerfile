# 🌌 Laniakea Protocol v0.0.02 - Unified Dockerfile
# Dockerfile یکپارچه و بهینه شده برای production و development

# Multi-stage build for optimization
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Build dependencies
    build-essential \
    curl \
    git \
    # Runtime dependencies
    libpq-dev \
    libffi-dev \
    libssl-dev \
    # Optional dependencies for enhanced features
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --upgrade pip && \
    pip install pytest pytest-asyncio pytest-cov black flake8 mypy

# Copy requirements first for better caching
COPY requirements_unified.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_unified.txt

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p data logs backups models cache profiles uploads temp

# Create non-root user
RUN useradd --create-home --shell /bin/bash laniakea && \
    chown -R laniakea:laniakea /app
USER laniakea

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command for development
CMD ["python", "main_unified.py", "--node-id", "docker-dev", "--port", "8000"]

# Production stage
FROM base as production

# Install production dependencies
RUN pip install --upgrade pip

# Copy requirements first for better caching
COPY requirements_unified.txt .

# Install only essential production dependencies
RUN pip install --no-cache-dir -r requirements_unified.txt

# Copy source code
COPY . .

# Create necessary directories
RUN mkdir -p data logs backups models cache profiles uploads temp

# Create non-root user
RUN useradd --create-home --shell /bin/bash laniakea && \
    chown -R laniakea:laniakea /app
USER laniakea

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command for production
CMD ["python", "main_unified.py", "--node-id", "docker-prod", "--port", "8000"]

# Minimal stage (for security-sensitive deployments)
FROM python:3.11-slim as minimal

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy minimal requirements
COPY requirements_minimal.txt .

# Install minimal dependencies
RUN pip install --no-cache-dir -r requirements_minimal.txt

# Copy only essential files
COPY main_unified.py .
COPY config_unified.py .
COPY src/ ./src/

# Create essential directories
RUN mkdir -p data logs cache

# Create non-root user
RUN useradd --create-home --shell /bin/bash laniakea && \
    chown -R laniakea:laniakea /app
USER laniakea

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "main_unified.py", "--node-id", "docker-minimal", "--port", "8000", "--disable-enhanced"]