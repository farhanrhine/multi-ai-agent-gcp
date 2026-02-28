# ============================================================================
# Stage 1: Builder - Install dependencies
# ============================================================================
FROM python:3.12-slim AS builder

## Essential environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

## Installing system dependencies and uv
RUN apt-get -o Acquire::ForceIPv4=true update && apt-get -o Acquire::ForceIPv4=true install -y \
    build-essential \
    curl \
    git \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

## Add uv to PATH
ENV PATH="/root/.cargo/bin:$PATH"

## Copy project files to builder
COPY pyproject.toml uv.lock* ./

## Install dependencies using uv (frozen lockfile if available)
RUN uv sync --frozen 2>/dev/null || uv sync

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.12-slim

## Essential environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HOME=/app

## Install runtime dependencies only
RUN apt-get -o Acquire::ForceIPv4=true update && apt-get -o Acquire::ForceIPv4=true install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

## Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

## Copy uv from builder
COPY --from=builder /root/.cargo/bin/uv /usr/local/bin/uv

## Copy project files
COPY . .

## Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

## Backend Configuration
ENV BACKEND_HOST="0.0.0.0" \
    BACKEND_PORT="9999"

## Exposed Ports
## 8501 - Streamlit Frontend
## 9999 - FastAPI Backend
EXPOSE 8501 9999

## Health check (optional - checks if services are responding)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501')" || exit 1

## Run the application
CMD ["python", "main.py"]