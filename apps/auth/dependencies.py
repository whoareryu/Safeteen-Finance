from __future__ import annotations

from fastapi import Cookie, Header, HTTPException

from apps.auth.user_model import User


async def get_current_user(
    x_user_id: str | None = Header(default=None),
    wr_session: str | None = Cookie(default=None),
) -> User:
    # X-User-Id 헤더 우선, Cloudflare가 헤더를 차단할 경우 wr_session 쿠키 fallback
    raw = x_user_id or wr_session
    if raw is None:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    try:
        user_id = int(raw)
    except ValueError:
        raise HTTPException(status_code=400, detail="X-User-Id는 정수여야 합니다.")
    user = User()
    user.__dict__["id"] = user_id
    return user
