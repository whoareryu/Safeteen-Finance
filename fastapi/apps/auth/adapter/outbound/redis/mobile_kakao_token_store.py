"""모바일 전용 토큰 저장소 — core.security의 RS256 발급/로테이션/블랙리스트를
auth:mobile: 네임스페이스로 감싼다. 웹(core.security 기본 네임스페이스 "")과
Redis 키가 절대 겹치지 않는다.
"""
from __future__ import annotations

from apps.auth.app.ports.output.mobile_token_store_port import MobileTokenStorePort
from core import security

_NAMESPACE = "auth:mobile:"
_PLATFORM = "mobile"


class MobileKakaoTokenStore(MobileTokenStorePort):

    def __init__(self, aud: str) -> None:
        self._aud = aud

    async def create_access_token(self, *, sub: str, roles: list[str]) -> tuple[str, int]:
        token = security.create_access_token(sub=sub, roles=roles, aud=self._aud, platform=_PLATFORM)
        return token, security.ACCESS_TOKEN_TTL_MIN_DEFAULT * 60

    async def create_refresh_token(self, *, sub: str, device_id: str) -> str:
        return await security.create_refresh_token(
            sub, namespace=_NAMESPACE, extra={"device_id": device_id, "platform": _PLATFORM}
        )

    async def rotate_refresh_token(self, refresh_token: str) -> tuple[str, str] | None:
        return await security.rotate_refresh_token(refresh_token, namespace=_NAMESPACE)

    async def revoke_all(self, sub: str) -> None:
        await security.revoke_refresh_family(sub, namespace=_NAMESPACE)

    async def blacklist_access_token(self, jti: str) -> None:
        await security.blacklist_token(
            jti, ttl_seconds=security.ACCESS_TOKEN_TTL_MIN_DEFAULT * 60, namespace=_NAMESPACE
        )
