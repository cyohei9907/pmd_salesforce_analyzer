#!/bin/bash
set -e

echo "=== Starting PMD Salesforce Analyzer ==="
echo "PORT: ${PORT:-8080}"
echo "PYTHONUNBUFFERED: ${PYTHONUNBUFFERED}"
echo "DEBUG: ${DEBUG}"
echo "USE_CLOUD_STORAGE: ${USE_CLOUD_STORAGE:-false}"
echo "Working directory: $(pwd)"

# Initialize Cloud Storage directories if enabled
if [ "${USE_CLOUD_STORAGE}" = "true" ]; then
    echo "=== Initializing Cloud Storage directories ==="
    mkdir -p /data/ast /data/database /data/graph/exports /data/graph/graphs
    chmod -R 755 /data
    echo "Cloud Storage directories initialized"
    
    # Copy sample AST files if /data/ast is empty
    if [ ! "$(ls -A /data/ast)" ]; then
        echo "Copying sample AST files to Cloud Storage..."
        cp -r /app/output/ast/* /data/ast/ 2>/dev/null || echo "No sample files to copy"
    fi
else
    echo "=== Using local storage ==="
fi

cd /app/backend

echo "=== Running database migrations ==="
python manage.py migrate --noinput || echo "Migration failed but continuing..."

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --clear || echo "Collectstatic failed but continuing..."

echo "=== Starting Nginx and Gunicorn with Supervisor ==="
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
