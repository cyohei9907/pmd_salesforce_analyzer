# Multi-stage build for production

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json frontend/pnpm-lock.yaml ./
RUN npm install -g pnpm@latest && pnpm install --no-frozen-lockfile
COPY frontend/ ./
RUN pnpm run build

# Stage 2: Final image with Nginx + Python
FROM python:3.12-slim

# Install system dependencies including Nginx
RUN apt-get update && apt-get install -y \
    default-jre \
    nginx \
    supervisor \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy PMD analyzer
COPY analyzer/ ./analyzer/
# Make PMD executable
RUN chmod +x /app/analyzer/bin/pmd /app/analyzer/bin/pmd.bat

# Copy backend application
COPY backend/ ./backend/

# Copy built frontend to Nginx directory
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy cloud storage configuration
COPY backend/cloud_storage.py ./

# Create necessary directories
# /data will be mounted as Cloud Storage volume in production
RUN mkdir -p /app/project \
             /data/ast \
             /data/database \
             /data/graph/exports \
             /data/graph/graphs \
             /var/log/supervisor && \
    chmod -R 755 /app/project /data /var/log/supervisor

# Copy sample AST files for testing (to /data/ast when using cloud storage)
COPY output/ast/ /app/output/ast/

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy entrypoint script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=apex_graph.settings
ENV PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8080}/ || exit 1

# Change to backend directory
WORKDIR /app/backend

# Run with supervisor to manage Nginx and Gunicorn
CMD ["/app/docker-entrypoint.sh"]
