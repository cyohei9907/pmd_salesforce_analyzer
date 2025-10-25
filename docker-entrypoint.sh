#!/bin/bash
set -e

echo "=== Starting PMD Salesforce Analyzer ==="
echo "PORT: ${PORT:-8080}"
echo "PYTHONUNBUFFERED: ${PYTHONUNBUFFERED}"
echo "DEBUG: ${DEBUG}"
echo "Working directory: $(pwd)"

cd /app/backend

echo "=== Running database migrations ==="
python manage.py migrate --noinput || echo "Migration failed but continuing..."

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --clear || echo "Collectstatic failed but continuing..."

echo "=== Starting Gunicorn server on 0.0.0.0:${PORT:-8080} ==="
exec gunicorn apex_graph.wsgi:application \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers 2 \
    --threads 2 \
    --timeout 0 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    --capture-output
