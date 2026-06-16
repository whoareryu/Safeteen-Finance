from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.auth.user_model import User
from apps.auth.user_role import UserRole


def _require_admin(db: Session, username: str) -> None:
    user = db.execute(
        select(User).where(func.lower(User.username) == username.lower()).limit(1)
    ).scalar_one_or_none()
    if user is None or user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
