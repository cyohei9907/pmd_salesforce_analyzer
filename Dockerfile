# Multi-stage build for production

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json frontend/pnpm-lock.yaml ./
RUN npm install -g pnpm@latest && pnpm install --no-frozen-lockfile
COPY frontend/ ./
RUN pnpm run build

# Stage 2: Python backend with built frontend
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-jre \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy PMD analyzer
COPY analyzer/ ./analyzer/

# Copy backend application
COPY backend/ ./backend/

# Copy built frontend to Django static files
COPY --from=frontend-builder /app/frontend/dist ./backend/static/

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Create necessary directories
RUN mkdir -p /app/project /app/output /app/graphdata

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=apex_graph.settings
ENV PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Change to backend directory
WORKDIR /app/backend

# Run migrations and start server
CMD python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    gunicorn apex_graph.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --threads 2 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
