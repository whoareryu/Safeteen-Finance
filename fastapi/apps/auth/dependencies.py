from __future__ import annotations

from fastapi import Cookie, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from apps.auth.jwt_service import decode_token
from apps.auth.owner_session import is_valid_owner_token
from apps.auth.session_store import SessionStorePort, get_session_store
from apps.auth.user_model import User
from apps.auth.user_role import UserRole
from apps.database import get_sync_db


async def get_current_user(
    wr_session: str | None = Cookie(default=None),
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_sync_db),
    session_store: SessionStorePort = Depends(get_session_store),
) -> User:
    token = wr_session
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ")
    if not token:
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")

    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="유효하지 않은 세션입니다.")

    if not await session_store.exists(payload["jti"]):
        raise HTTPException(status_code=401, detail="만료되었거나 로그아웃된 세션입니다.")

    user = db.get(User, int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")
    return user


async def require_owner(wr_owner_session: str | None = Cookie(default=None)) -> None:
    """이메일 발송·주소록·lesson 탭처럼 소유자 본인만 써야 하는 기능의 게이트."""
    if not is_valid_owner_token(wr_owner_session):
        raise HTTPException(status_code=403, detail="본인 Google 계정으로 로그인해야 합니다.")


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """관리자 대시보드·사용자 관리 등 RBAC role=admin 전용 게이트."""
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    return current_user
