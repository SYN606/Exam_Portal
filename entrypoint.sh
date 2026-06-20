#!/bin/sh

set -e

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && \
   [ -n "$DJANGO_SUPERUSER_EMAIL" ] && \
   [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then

python manage.py shell << EOF
from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username="$DJANGO_SUPERUSER_USERNAME").exists():
    User.objects.create_superuser(
        "$DJANGO_SUPERUSER_USERNAME",
        "$DJANGO_SUPERUSER_EMAIL",
        "$DJANGO_SUPERUSER_PASSWORD"
    )
    print("Superuser created")
else:
    print("Superuser already exists")
EOF

fi

echo "Starting Gunicorn..."

exec gunicorn examportal.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3
