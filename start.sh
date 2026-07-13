#!/bin/bash
set -e

echo "[1/3] 최신 이미지 가져오는 중..."
docker compose --env-file fastapi/.env -f docker-compose.backend.yaml pull

echo "[2/3] Docker 서비스 시작 중..."
docker compose --env-file fastapi/.env -f docker-compose.backend.yaml up -d "$@"

echo "[3/3] Cloudflare 터널 시작 중..."
./start-tunnel.sh
