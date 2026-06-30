"""인증 엔드포인트 (회원가입 · 로그인 · 중복확인 · Google OAuth)."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.auth.user_model import User
from apps.auth.user_role import UserRole
from apps.database import get_sync_db

auth_router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# 비밀번호 해싱 (stdlib PBKDF2-SHA256, 100k 반복)
# ---------------------------------------------------------------------------
_ITERATIONS = 100_000
_SALT_LEN = 32


def _hash_password(password: str) -> str:
    salt = os.urandom(_SALT_LEN)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return base64.b64encode(salt + key).decode()


def _verify_password(password: str, stored: str) -> bool:
    try:
        decoded = base64.b64decode(stored.encode())
        salt = decoded[:_SALT_LEN]
        key = decoded[_SALT_LEN:]
        new_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
        return hmac.compare_digest(key, new_key)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 스키마
# ---------------------------------------------------------------------------
class SignupRequest(BaseModel):
    username: str
    password: str
    password_confirm: str
    email: str
    nickname: str


class LoginRequest(BaseModel):
    username: str
    password: str


class GoogleLoginRequest(BaseModel):
    credential: str  # Google ID token


class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    email: str
    role: str


def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        role=user.role.value if isinstance(user.role, UserRole) else str(user.role),
    )


# ---------------------------------------------------------------------------
# 중복 확인
# ---------------------------------------------------------------------------
@auth_router.get("/check-username")
def check_username(
    username: str = Query(..., min_length=3, max_length=32),
    db: Session = Depends(get_sync_db),
) -> dict:
    exists = db.execute(
        select(User).where(func.lower(User.username) == username.strip().lower()).limit(1)
    ).scalar_one_or_none()
    if exists:
        return {"available": False, "message": "이미 사용 중인 아이디입니다."}
    return {"available": True, "message": "사용 가능한 아이디입니다."}


@auth_router.get("/check-nickname")
def check_nickname(
    nickname: str = Query(..., min_length=1, max_length=64),
    db: Session = Depends(get_sync_db),
) -> dict:
    exists = db.execute(
        select(User).where(func.lower(User.nickname) == nickname.strip().lower()).limit(1)
    ).scalar_one_or_none()
    if exists:
        return {"available": False, "message": "이미 사용 중인 닉네임입니다."}
    return {"available": True, "message": "사용 가능한 닉네임입니다."}


# ---------------------------------------------------------------------------
# 내 정보
# ---------------------------------------------------------------------------
@auth_router.get("/me")
def get_me(
    x_user_id: int = Query(None, alias="user_id"),
    db: Session = Depends(get_sync_db),
) -> UserResponse:
    from fastapi import Request  # noqa: F401 — unused, kept for DI reference
    # X-User-Id는 proxy 레이어에서 query param으로 전달하거나 직접 사용
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    user = db.get(User, x_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return _user_response(user)


# ---------------------------------------------------------------------------
# 회원가입
# ---------------------------------------------------------------------------
signup_router = APIRouter(tags=["auth"])


@signup_router.post("/signup")
def register(body: SignupRequest, db: Session = Depends(get_sync_db)) -> UserResponse:
    if body.password != body.password_confirm:
        raise HTTPException(status_code=422, detail="비밀번호가 일치하지 않습니다.")
    if len(body.password) < 6:
        raise HTTPException(status_code=422, detail="비밀번호는 6자 이상이어야 합니다.")

    uname = body.username.strip()
    if db.execute(
        select(User).where(func.lower(User.username) == uname.lower()).limit(1)
    ).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다.")

    email = body.email.strip().lower()
    if db.execute(select(User).where(User.email == email).limit(1)).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")

    nick = body.nickname.strip()
    if db.execute(
        select(User).where(func.lower(User.nickname) == nick.lower()).limit(1)
    ).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="이미 사용 중인 닉네임입니다.")

    user = User(
        username=uname,
        email=email,
        nickname=nick,
        password_hash=_hash_password(body.password),
        role=UserRole.user,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.flush()
    db.refresh(user)
    return _user_response(user)


# ---------------------------------------------------------------------------
# 로그인
# ---------------------------------------------------------------------------
login_router = APIRouter(tags=["auth"])


@login_router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_sync_db)) -> UserResponse:
    user = db.execute(
        select(User).where(func.lower(User.username) == body.username.strip().lower()).limit(1)
    ).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")

    if user.password_hash.startswith("GOOGLE:"):
        raise HTTPException(
            status_code=401,
            detail="이 계정은 Google로 가입되었습니다. Google 로그인을 이용해 주세요.",
        )

    if not _verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")

    user.last_login_at = datetime.now(timezone.utc)
    db.flush()
    return _user_response(user)


# ---------------------------------------------------------------------------
# Google OAuth
# ---------------------------------------------------------------------------
@auth_router.post("/google")
async def google_login(body: GoogleLoginRequest, db: Session = Depends(get_sync_db)) -> UserResponse:
    """Google ID 토큰 검증 후 사용자 생성(신규) 또는 로그인(기존)."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": body.credential},
            timeout=10.0,
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Google 인증에 실패했습니다.")

    info = resp.json()
    google_sub: str = info.get("sub", "")
    email: str = info.get("email", "").strip().lower()
    name: str = info.get("name", "") or info.get("given_name", "") or "사용자"

    if not google_sub or not email:
        raise HTTPException(status_code=401, detail="Google 계정 정보를 가져올 수 없습니다.")

    # 기존 Google 계정 확인
    user = db.execute(
        select(User).where(User.password_hash == f"GOOGLE:{google_sub}").limit(1)
    ).scalar_one_or_none()

    if user is None:
        # 같은 이메일로 기존 가입 여부 확인
        user = db.execute(
            select(User).where(User.email == email).limit(1)
        ).scalar_one_or_none()
        if user is not None:
            # 이메일이 같은 기존 계정을 Google 계정으로 연결
            user.password_hash = f"GOOGLE:{google_sub}"
            db.flush()
        else:
            # 신규 사용자 생성
            base_username = email.split("@")[0][:30]
            username = base_username
            suffix = 1
            while db.execute(
                select(User).where(func.lower(User.username) == username.lower()).limit(1)
            ).scalar_one_or_none():
                username = f"{base_username}{suffix}"
                suffix += 1

            nickname = name[:32]
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
                password_hash=f"GOOGLE:{google_sub}",
                role=UserRole.user,
                created_at=datetime.now(timezone.utc),
            )
            db.add(user)
            db.flush()
            db.refresh(user)

    user.last_login_at = datetime.now(timezone.utc)
    db.flush()
    return _user_response(user)
