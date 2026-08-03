from __future__ import annotations

from functools import lru_cache

from redis.asyncio import Redis

from apps.auth.app.ports.output.mobile_nonce_store_port import NonceStorePort
from core.matrix.secret_manager import secret_manager

_KEY_PREFIX = "auth:mobile:nonce:"
_TTL_SECONDS = 300


@lru_cache(maxsize=1)
def _redis_client() -> Redis:
    return Redis.from_url(secret_manager.get_secret("REDIS_URL", "redis://redis:6379/0"))


class RedisNonceStore(NonceStorePort):

    async def consume_once(self, nonce: str) -> bool:
        return bool(await _redis_client().set(f"{_KEY_PREFIX}{nonce}", "1", nx=True, ex=_TTL_SECONDS))
