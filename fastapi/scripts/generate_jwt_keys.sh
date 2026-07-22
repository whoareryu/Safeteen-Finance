#!/usr/bin/env bash
set -euo pipefail

openssl genrsa -out jwt_private.pem 2048
openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem

echo "jwt_private.pem → .env.auth 의 JWT_PRIVATE_KEY 로"
echo "jwt_public.pem  → .env(백엔드)의 JWT_PUBLIC_KEY 로"
