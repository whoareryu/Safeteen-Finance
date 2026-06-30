from __future__ import annotations

from fastapi import Header, HTTPException

from apps.auth.user_model import User


async def get_current_user(x_user_id: str | None = Header(default=None)) -> User:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="인증이 필요합니다. X-User-Id 헤더를 전달하세요.")
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="X-User-Id는 정수여야 합니다.")
    user = User()
    user.__dict__["id"] = user_id
    return user
