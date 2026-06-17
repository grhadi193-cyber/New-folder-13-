#!/bin/sh

echo "Running migrations..."
python manage.py migrate --noinput || echo "Migration had issues, continuing..."

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Seeding provinces & cities..."
python manage.py load_provinces_cities || true

echo "Setting province zones..."
python manage.py set_province_zones || true

echo "Seeding shipping..."
python manage.py seed_shipping || true

echo "Starting gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120
