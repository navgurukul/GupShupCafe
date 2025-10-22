# ============================================
# Stage 1: Build Frontend (React + Vite)
# ============================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/client

COPY client/package*.json ./
RUN npm ci --legacy-peer-deps

COPY client/ ./
RUN npm run build

# ============================================
# Stage 2: Build Backend (FastAPI)
# ============================================
FROM python:3.11-slim AS backend-builder

WORKDIR /app

# Install build-time dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ make libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY server_py/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 3: Final Image
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy backend runtime dependencies (Python venv)
COPY --from=backend-builder /usr/local /usr/local

# Copy backend code
COPY server_py/ ./server_py/

# Copy built frontend assets into the backend's static folder
COPY --from=frontend-builder /app/client/dist ./server_py/static

# Create data directory before changing permissions
RUN mkdir -p /app/server_py/data

# Create non-root user and set ownership for the entire /app directory
# This covers the app code, static files, and the data directory
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Switch to the correct directory for running the app
WORKDIR /app/server_py

# Switch to non-root user
USER appuser

EXPOSE 3003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3003/api/health || exit 1

# Environment variables
ENV PYTHON_ENV=production \
    PORT=3003 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# ✅ Use production Uvicorn with workers AND the --proxy-headers fix
CMD ["uvicorn", "main:socket_app", "--host", "0.0.0.0", "--port", "3003", "--workers", "4", "--proxy-headers"]

