#!/bin/bash
set -e

echo "============================================"
echo "  Backend Deploy — ArvanCloud"
echo "============================================"

if [ ! -f .env ]; then
    echo "ERROR: .env not found!"
    exit 1
fi

source .env
if [ "$POSTGRES_PASSWORD" = "CHANGE_ME_strong_password" ] || [ "$SECRET_KEY" = "CHANGE_ME_random_50_chars" ]; then
    echo "ERROR: Edit .env and set POSTGRES_PASSWORD and SECRET_KEY!"
    exit 1
fi

echo "[1/3] Building..."
docker compose build --no-cache

echo "[2/3] Starting..."
docker compose up -d

echo "[3/3] Waiting for health..."
sleep 15
docker compose ps

echo ""
echo "============================================"
echo "  Backend is live at: http://95.38.161.104"
echo "  API health: http://95.38.161.104/api/health"
echo "  Admin: http://95.38.161.104/admin/"
echo "============================================"
echo ""
echo "Logs: docker compose logs -f"
