# Multi-stage Dockerfile for GupShup Cafe
# Builds React frontend and FastAPI backend for AWS Fargate deployment

# ============================================
# Stage 1: Build Frontend (React + Vite)
# ============================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/client

# Copy frontend package files
COPY client/package*.json ./

# Install frontend dependencies
RUN npm ci --legacy-peer-deps

# Copy frontend source code
COPY client/ ./

# Build the frontend for production
RUN npm run build

# ============================================
# Stage 2: Setup Backend (Python FastAPI)
# ============================================
FROM python:3.11-slim AS backend-builder

WORKDIR /app

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY server_py/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 3: Final Production Image
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend source code
COPY server_py/ ./server_py/

# Copy built frontend assets to be served by backend
COPY --from=frontend-builder /app/client/dist ./server_py/static

# Create necessary directories
RUN mkdir -p ./server_py/data && \
    chmod -R 755 ./server_py

# Set working directory to backend
WORKDIR /app/server_py

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port (Fargate will map this)
EXPOSE 3003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3003/api/health || exit 1

# Set environment variables
ENV PYTHON_ENV=production \
    PORT=3003 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Start the FastAPI server
CMD ["uvicorn", "main:socket_app", "--port", "3003", "--reload", "--host", "0.0.0.0", "--log-level", "debug"]
