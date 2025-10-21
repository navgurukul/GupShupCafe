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
# Stage 2: Backend Dependencies
# ============================================
FROM python:3.11-slim AS backend-builder

WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ libpq-dev && rm -rf /var/lib/apt/lists/*
COPY server_py/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ============================================
# Stage 3: Final Runtime Image
# ============================================
FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy backend + built frontend
COPY --from=backend-builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=backend-builder /usr/local/bin /usr/local/bin
COPY server_py ./server_py
COPY --from=frontend-builder /app/client/dist ./server_py/static

# Security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

ENV PYTHON_ENV=production \
    PORT=3003 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 3003

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:3003/health || exit 1

WORKDIR /app/server_py
CMD ["python", "main.py"]
