#!/bin/bash

echo "[1/2] Cloudflare 터널 종료 중..."
pkill -f "cloudflared tunnel" 2>/dev/null || true

echo "[2/2] Docker 서비스 종료 중..."
docker compose --env-file .env -f docker-compose.yaml down

echo "완료"
