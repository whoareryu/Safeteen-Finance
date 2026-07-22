"""RS256 토큰 검증 기반 FastAPI 의존성 — auth-gateway-harness.md 2.3.

apps/auth 발급 로직과 달리 이 모듈은 JWT_PUBLIC_KEY만 있으면 되므로 모든
컨테이너(백엔드 포함)가 공용으로 쓸 수 있다.
"""
from __future__ import annotations

import os

import jwt
from fastapi import Cookie, Depends, Header, HTTPException

from apps.auth.user_role import UserRole
from core.security import TokenPayload, is_token_blacklisted, verify_token

_SERVICE_AUD = os.getenv("SERVICE_AUD", "whoareryu-api")


async def get_current_user(
    wr_session: str | None = Cookie(default=None),
    authorization: str | None = Header(default=None),
) -> TokenPayload:
    token = wr_session
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ")
    if not token:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    try:
        payload = verify_token(token, aud=_SERVICE_AUD)
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.") from e

    if await is_token_blacklisted(payload.jti):
        raise HTTPException(status_code=401, detail="차단된 세션입니다.")

    return payload


class RoleChecker:
    """dependencies=[Depends(RoleChecker(UserRole.admin))] 형태로 라우터에 건다."""

    def __init__(self, *allowed: UserRole) -> None:
        self._allowed = set(allowed)

    def __call__(self, user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if not any(role in self._allowed for role in user.roles):
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        return user
