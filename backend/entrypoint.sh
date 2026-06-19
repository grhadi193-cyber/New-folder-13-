#!/bin/sh
set -e

echo "Waiting for database..."
python -c "
import time, os, sys
import dj_database_url
try:
    db = dj_database_url.parse(os.environ.get('DATABASE_URL', ''))
    import psycopg2
    for i in range(30):
        try:
            conn = psycopg2.connect(
                dbname=db['NAME'], user=db['USER'], password=db['PASSWORD'],
                host=db['HOST'], port=db['PORT']
            )
            conn.close()
            print('Database is ready!')
            sys.exit(0)
        except psycopg2.OperationalError:
            print(f'Database not ready, waiting... ({i+1}/30)')
            time.sleep(2)
    print('Could not connect to database after 30 attempts')
    sys.exit(1)
except Exception as e:
    print(f'DB check skipped: {e}')
"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Seeding provinces & cities..."
python manage.py load_provinces_cities || true

echo "Setting province zones..."
python manage.py set_province_zones || true

echo "Seeding shipping..."
python manage.py seed_shipping || true

echo "Starting gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120
