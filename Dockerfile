# ============================================================
# Laniakea Protocol — Multi-stage Dockerfile
# Stage 1: Build cosmic UI (Vite)
# Stage 2: Backend (FastAPI)
# Stage 3: Nginx serving UI + proxying API
# ============================================================

# ---------- Stage 1: Build frontend ----------
FROM node:20-alpine AS ui-builder
WORKDIR /build
COPY web/package.json web/package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY web/ ./
RUN npm run build

# ---------- Stage 2: Backend ----------
FROM python:3.11-slim AS backend
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app
WORKDIR $APP_HOME

# System deps for cryptography, asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Python deps (cached layer)
COPY requirements.txt requirements_extended.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements_extended.txt || true

# App code
COPY . $APP_HOME

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# ---------- Stage 3: Runtime with Nginx ----------
FROM nginx:1.25-alpine AS runtime

# Install python for backend sidecar (or just use uvicorn in same container)
# We use a single-image approach: nginx + uvicorn via supervisord-light

# Backend files
COPY --from=backend /app /app

# Built UI
COPY --from=ui-builder /build/dist /usr/share/nginx/html

# Nginx config (serves UI + proxies /api and /ws)
COPY nginx/nginx.cosmic.conf /etc/nginx/conf.d/default.conf

# Entrypoint runs both nginx and uvicorn
RUN apk add --no-cache python3 py3-pip supervisor \
    && pip3 install --break-system-packages --no-cache-dir -r /app/requirements.txt || true

COPY nginx/supervisord.conf /etc/supervisord.conf

EXPOSE 80 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD wget -qO- http://localhost/health || exit 1

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
