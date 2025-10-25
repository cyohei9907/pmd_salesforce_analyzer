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

echo "=== Starting Nginx and Gunicorn with Supervisor ==="
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
