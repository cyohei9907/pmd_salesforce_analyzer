#!/bin/bash
set -e

echo "=== Starting PMD Salesforce Analyzer ==="
echo "PORT: ${PORT:-8080}"
echo "PYTHONUNBUFFERED: ${PYTHONUNBUFFERED}"
echo "DEBUG: ${DEBUG}"

cd /app/backend

echo "=== Running database migrations ==="
python manage.py migrate --noinput

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --clear

echo "=== Starting Gunicorn server on 0.0.0.0:${PORT:-8080} ==="
exec gunicorn apex_graph.wsgi:application \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers 2 \
    --threads 2 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output
