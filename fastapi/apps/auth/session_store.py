"""JWT 세션을 Redis에 저장 — 로그아웃·강제 만료 시 즉시 무효화하기 위함.

서명만으로는(jwt_service.decode_token) 만료 전 로그아웃을 표현할 수 없어서,
발급한 jti를 Redis에 TTL과 함께 저장해두고 요청마다 존재 여부를 확인한다.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from functools import lru_cache

from redis.asyncio import Redis

from apps.auth.jwt_service import TOKEN_TTL_SECONDS

_KEY_PREFIX = "session:"


class SessionStorePort(ABC):
    @abstractmethod
    async def save(self, jti: str, user_id: int) -> None: ...

    @abstractmethod
    async def exists(self, jti: str) -> bool: ...

    @abstractmethod
    async def revoke(self, jti: str) -> None: ...


class RedisSessionStore(SessionStorePort):
    def __init__(self, client: Redis) -> None:
        self._client = client

    async def save(self, jti: str, user_id: int) -> None:
        await self._client.set(f"{_KEY_PREFIX}{jti}", user_id, ex=TOKEN_TTL_SECONDS)

    async def exists(self, jti: str) -> bool:
        return await self._client.exists(f"{_KEY_PREFIX}{jti}") == 1

    async def revoke(self, jti: str) -> None:
        await self._client.delete(f"{_KEY_PREFIX}{jti}")


@lru_cache(maxsize=1)
def _redis_client() -> Redis:
    return Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"))


def get_session_store() -> SessionStorePort:
    return RedisSessionStore(client=_redis_client())
