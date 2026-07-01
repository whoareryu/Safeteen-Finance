#!/bin/bash
set -e

echo "[1/2] Docker 서비스 시작 중..."
docker compose up -d "$@"

echo "[2/2] Cloudflare 터널 시작 중..."
./start-tunnel.sh
