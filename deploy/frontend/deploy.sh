#!/bin/bash
set -e

echo "============================================"
echo "  Frontend Deploy — ArvanCloud"
echo "============================================"

echo "[1/3] Building..."
docker compose build --no-cache

echo "[2/3] Starting..."
docker compose up -d

echo "[3/3] Waiting..."
sleep 10
docker compose ps

echo ""
echo "============================================"
echo "  Frontend is live at: http://95.38.161.205"
echo "============================================"
echo ""
echo "Logs: docker compose logs -f"
