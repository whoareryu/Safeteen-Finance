from __future__ import annotations

from abc import ABC, abstractmethod


class MobileTokenStorePort(ABC):
    """모바일(auth:mobile:* 네임스페이스) 액세스/리프레시 토큰 발급·로테이션·폐기."""

    @abstractmethod
    async def create_access_token(self, *, sub: str, roles: list[str]) -> tuple[str, int]:
        """(jwt, expires_in_seconds)를 반환한다."""

    @abstractmethod
    async def create_refresh_token(self, *, sub: str, device_id: str) -> str:
        pass

    @abstractmethod
    async def rotate_refresh_token(self, refresh_token: str) -> tuple[str, str] | None:
        """(sub, 새 리프레시 토큰). 실패/재사용 감지 시 None."""

    @abstractmethod
    async def revoke_all(self, sub: str) -> None:
        pass

    @abstractmethod
    async def blacklist_access_token(self, jti: str) -> None:
        """액세스 토큰의 남은 수명 동안 차단한다 — TTL은 어댑터가 발급 시 쓴 TTL과 맞춰 결정한다."""
