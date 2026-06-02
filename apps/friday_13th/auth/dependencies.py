"""Gourmet·즐겨찾기 등 — 요청 사용자 식별 (localStorage `user.id` → ``X-User-Id``)."""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.friday_13th.auth.user_model import User
from apps.database import get_sync_db


def resolve_user(
    db: Session,
    *,
    x_user_id: int | None = None,
    as_username: str | None = None,
) -> User:
    if x_user_id is not None:
        user = db.get(User, x_user_id)
        if user is not None:
            return user
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    if as_username and as_username.strip():
        row = db.execute(
            select(User)
            .where(func.lower(User.username) == as_username.strip().lower())
            .limit(1)
        ).scalar_one_or_none()
        if row is not None:
            return row
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    raise HTTPException(
        status_code=401,
        detail="로그인이 필요합니다. 요청 헤더 X-User-Id 를 보내 주세요.",
    )


def get_current_user(
    x_user_id: int | None = Header(None, alias="X-User-Id"),
    user_id: int | None = Query(
        None,
        description="(하위 호환) 쿼리 user_id — X-User-Id 권장",
    ),
    as_username: str | None = Query(
        None,
        description="(하위 호환) Whoareryu 등 username",
    ),
    db: Session = Depends(get_sync_db),
) -> User:
    uid = x_user_id if x_user_id is not None else user_id
    return resolve_user(db, x_user_id=uid, as_username=as_username)
