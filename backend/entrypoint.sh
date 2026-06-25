#!/bin/sh
set -e

echo "============================================"
echo " Container starting up"
echo " DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"
echo "============================================"

# ---------------------------------------------------------------------------
# 1. Wait for database with exponential backoff
# ---------------------------------------------------------------------------
echo "[1/6] Waiting for database..."
python -c "
import time, os, sys
import dj_database_url
import psycopg2

db_url = os.environ.get('DATABASE_URL', '')
if not db_url:
    print('ERROR: DATABASE_URL is not set!')
    sys.exit(1)

db = dj_database_url.parse(db_url)
max_retries = 60
wait = 1

for i in range(max_retries):
    try:
        conn = psycopg2.connect(
            dbname=db['NAME'], user=db['USER'], password=db['PASSWORD'],
            host=db['HOST'], port=db['PORT'], connect_timeout=5
        )
        conn.close()
        print(f'Database is ready after {i+1} attempt(s)!')
        sys.exit(0)
    except psycopg2.OperationalError as e:
        print(f'Attempt {i+1}/{max_retries}: DB not ready ({e}), retrying in {wait}s...')
        time.sleep(wait)
        wait = min(wait * 2, 10)

print('ERROR: Could not connect to database after 60 attempts. Aborting.')
sys.exit(1)
"

# ---------------------------------------------------------------------------
# 2. Run migrations
# ---------------------------------------------------------------------------
if [ "${SKIP_MIGRATE:-false}" = "true" ]; then
    echo "[2/6] Skipping migrations (SKIP_MIGRATE=true)"
else
    echo "[2/6] Migration state BEFORE:"
    python manage.py showmigrations --list

    echo "[2/6] Running migrations..."
    python manage.py migrate --noinput --verbosity 2
    if [ $? -ne 0 ]; then
        echo "ERROR: Migration failed! Aborting."
        exit 1
    fi

    echo "[2/6] Migration state AFTER:"
    python manage.py showmigrations --list
fi

# ---------------------------------------------------------------------------
# 2b. Ensure media directories exist and are writable by django user
# ---------------------------------------------------------------------------
echo "[2b/6] Ensuring media directories exist and are writable..."
MEDIA_ROOT="${MEDIA_ROOT:-/app/media}"
mkdir -p "$MEDIA_ROOT"/{site,site/hero,site/about,site/software,site/app,site/why_us,site/categories,site/testimonials,site/newsletter,banners,partners,categories,products,products/gallery,blog/images}

chown -R django:django "$MEDIA_ROOT"
chmod -R 775 "$MEDIA_ROOT"

echo "Media directory ownership set to django:django."

# ---------------------------------------------------------------------------
# 3. Collect static files (running as root, fix ownership afterwards)
# ---------------------------------------------------------------------------
echo "[3/6] Collecting static files..."
python manage.py collectstatic --noinput --verbosity 1
chown -R django:django /app/staticfiles 2>/dev/null || true

# Also ensure the whole /app tree is readable by django
chown -R django:django /app 2>/dev/null || true

# ---------------------------------------------------------------------------
# 4. Seed data (idempotent)
# ---------------------------------------------------------------------------
echo "[4/6] Seeding provinces & cities..."
python manage.py load_provinces_cities || true

echo "[5/6] Setting province zones..."
python manage.py set_province_zones || true

echo "[6/6] Seeding shipping..."
python manage.py seed_shipping || true

# ---------------------------------------------------------------------------
# 5. Start Gunicorn
# ---------------------------------------------------------------------------
echo "============================================"
echo " Starting Gunicorn on port ${PORT:-8000} as user django"
echo "============================================"
exec su -s /bin/sh django -c "
gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --forwarded-allow-ips='*'
"
