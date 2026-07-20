"""OAuth(Google·Naver·Kakao) 사용자 조회·생성 — provider:sub 마커로 계정을 식별한다.

기존 사용자는 조회만(find_existing_user), 신규 사용자는 서비스 약관 동의를 받은
뒤(apps/auth/consent_flow.py 경유) create_oauth_user로 생성한다.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.auth.user_model import User
from apps.auth.user_role import UserRole


def _marker(provider: str, sub: str) -> str:
    return f"{provider}:{sub}"


def find_existing_user(db: Session, *, provider: str, sub: str, email: str) -> User | None:
    marker = _marker(provider, sub)
    user = db.execute(
        select(User).where(User.password_hash == marker).limit(1)
    ).scalar_one_or_none()
    if user is not None:
        return user

    user = db.execute(select(User).where(User.email == email).limit(1)).scalar_one_or_none()
    if user is not None:
        # 이메일이 같은 기존 계정을 이 provider 계정으로 연결
        user.password_hash = marker
        db.flush()
        return user
    return None


def create_oauth_user(db: Session, *, provider: str, sub: str, email: str, name: str) -> User:
    base_username = email.split("@")[0][:30]
    username = base_username
    suffix = 1
    while db.execute(
        select(User).where(func.lower(User.username) == username.lower()).limit(1)
    ).scalar_one_or_none():
        username = f"{base_username}{suffix}"
        suffix += 1

    nickname = name[:32] or base_username
    nick_check = nickname
    suffix = 1
    while db.execute(
        select(User).where(func.lower(User.nickname) == nick_check.lower()).limit(1)
    ).scalar_one_or_none():
        nick_check = f"{nickname}{suffix}"
        suffix += 1

    user = User(
        username=username,
        email=email,
        nickname=nick_check,
        password_hash=_marker(provider, sub),
        role=UserRole.user,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.flush()
    db.refresh(user)
    return user
