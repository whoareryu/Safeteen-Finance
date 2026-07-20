"""사용자 세션 JWT 발급·검증.

Redis 세션 저장(session_store.py)과 함께 써야 완전하다 — 여기서 서명이 유효해도
Redis에 jti가 없으면(로그아웃·강제 만료) 세션 무효로 취급한다.
"""
from __future__ import annotations

import os
import time
import uuid

import jwt

_SECRET = os.environ["JWT_SECRET"]
_ALGORITHM = "HS256"
TOKEN_TTL_SECONDS = 60 * 60 * 24 * 30  # 30일


def issue_token(user_id: int, email: str, role: str) -> tuple[str, str]:
    """(token, jti) 반환. jti는 Redis 세션 키로 쓴다."""
    jti = uuid.uuid4().hex
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "jti": jti,
        "iat": now,
        "exp": now + TOKEN_TTL_SECONDS,
    }
    token = jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)
    return token, jti


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
    except jwt.PyJWTError:
        return None
