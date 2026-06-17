#!/bin/sh

echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "collectstatic failed, continuing..."

echo "Starting gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120
