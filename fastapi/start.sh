#!/bin/bash
set -e

echo "[1/4] 최신 이미지 가져오는 중..."
docker compose --env-file .env -f docker-compose.yaml pull

echo "[2/4] Docker 서비스 시작 중..."
docker compose --env-file .env -f docker-compose.yaml up -d "$@"

echo "[3/4] 안 쓰는 이전 이미지 정리 중..."
docker image prune -f

echo "[4/4] Cloudflare 터널 시작 중..."
./start-tunnel.sh
