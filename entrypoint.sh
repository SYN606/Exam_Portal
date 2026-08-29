#!/bin/sh

set -e

# Wait for Database (optional, ensures DB is up before running migrations)
if [ -n "$DATABASE_HOST" ]; then
    echo "Waiting for database ($DATABASE_HOST)..."
    while ! nc -z "$DATABASE_HOST" "${DATABASE_PORT:-5432}"; do
      sleep 0.5
    done
    echo "Database ready!"
fi

echo "Applying database migrations..."
python manage.py migrate --no-input

echo "Collecting static files..."
python manage.py collectstatic --no-input

# Automatic Superuser Creation
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && \
   [ -n "$DJANGO_SUPERUSER_EMAIL" ] && \
   [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then

    echo "Ensuring superuser exists..."
    python manage.py createsuperuser \
        --no-input \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "$DJANGO_SUPERUSER_EMAIL" || echo "Superuser already exists."
fi

echo "Starting Gunicorn server..."
exec gunicorn examportal.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile - \
    --error-logfile -