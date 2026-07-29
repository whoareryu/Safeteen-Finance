"""OAuth 신규 가입자의 서비스 약관 동의를 기다리는 동안 프로필을 임시 보관한다.

Google·Naver·Kakao 로그인에서 계정이 아직 없는 사용자는 여기 거쳐서 동의를
받은 뒤에만 계정을 생성한다(apps/auth/consent_router.py). 기존 사용자(재로그인)는
이미 최초 가입 때 동의했으므로 이 단계를 건너뛴다.
"""
from __future__ import annotations

import json
import secrets
from functools import lru_cache

from redis.asyncio import Redis

from core.matrix.secret_manager import secret_manager

_KEY_PREFIX = "pending_signup:"
_TTL_SECONDS = 600


@lru_cache(maxsize=1)
def _redis_client() -> Redis:
    return Redis.from_url(secret_manager.get_secret("REDIS_URL", "redis://redis:6379/0"))


async def create_pending_signup(*, provider: str, sub: str, email: str, name: str) -> str:
    token = secrets.token_urlsafe(24)
    payload = json.dumps({"provider": provider, "sub": sub, "email": email, "name": name})
    await _redis_client().set(f"{_KEY_PREFIX}{token}", payload, ex=_TTL_SECONDS)
    return token


async def pop_pending_signup(token: str) -> dict | None:
    client = _redis_client()
    key = f"{_KEY_PREFIX}{token}"
    raw = await client.get(key)
    if raw is None:
        return None
    await client.delete(key)
    return json.loads(raw)
