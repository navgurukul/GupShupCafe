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

# Install runtime deps
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy backend runtime dependencies
COPY --from=backend-builder /usr/local /usr/local

# Copy backend code
COPY server_py/ ./server_py/

# Copy built frontend assets
COPY --from=frontend-builder /app/client/dist ./server_py/static

# Set permissions
RUN mkdir -p ./server_py/data && chmod -R 755 ./server_py

WORKDIR /app/server_py

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
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

# ✅ Use production Uvicorn with workers (no --reload)
CMD ["uvicorn", "main:socket_app", "--host", "0.0.0.0", "--port", "3003", "--workers", "4"]
