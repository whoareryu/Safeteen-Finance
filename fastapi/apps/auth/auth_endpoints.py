"""인증 엔드포인트 (회원가입 · 로그인 · 중복확인 · Google OAuth)."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.auth.consent_flow import create_pending_signup
from apps.auth.dependencies import get_current_user
from apps.auth.jwt_service import TOKEN_TTL_SECONDS, decode_token, issue_token
from apps.auth.owner_session import is_valid_owner_token, issue_owner_token
from apps.auth.session_store import SessionStorePort, get_session_store
from apps.auth.user_model import User
from apps.auth.user_provisioning import find_existing_user
from apps.auth.user_role import UserRole
from apps.database import get_sync_db


async def _start_session(
    response: Response, user: User, session_store: SessionStorePort
) -> None:
    """로그인 성공 시 JWT를 발급해 Redis에 세션으로 저장하고, httpOnly 쿠키로 내려준다."""
    token, jti = issue_token(
        user_id=user.id,
        email=user.email,
        role=user.role.value if isinstance(user.role, UserRole) else str(user.role),
    )
    await session_store.save(jti, user.id)
    response.set_cookie(
        "wr_session",
        token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=TOKEN_TTL_SECONDS,
    )

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
    region: str | None = None
    agree_terms: bool = False


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
    region: str | None = None


class GoogleLoginResponse(UserResponse):
    is_owner: bool = False


class PendingConsentResponse(BaseModel):
    """OAuth 신규 가입자 — 계정 생성 전 서비스 약관 동의가 먼저 필요하다."""

    pending: bool = True
    consent_token: str
    email: str
    nickname: str


def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        role=user.role.value if isinstance(user.role, UserRole) else str(user.role),
        region=user.region,
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


@auth_router.get("/owner-check")
def owner_check(wr_owner_session: str | None = Cookie(default=None)) -> dict:
    return {"is_owner": is_valid_owner_token(wr_owner_session)}


# ---------------------------------------------------------------------------
# 세션 (JWT+Redis) — 새로고침 시 프론트가 로그인 상태를 복원할 때 사용
# ---------------------------------------------------------------------------
@auth_router.get("/session")
def get_session(current_user: User = Depends(get_current_user)) -> UserResponse:
    return _user_response(current_user)


@auth_router.post("/logout")
async def logout(
    response: Response,
    wr_session: str | None = Cookie(default=None),
    session_store: SessionStorePort = Depends(get_session_store),
) -> dict:
    if wr_session:
        payload = decode_token(wr_session)
        if payload:
            await session_store.revoke(payload["jti"])
    response.delete_cookie("wr_session")
    response.delete_cookie("wr_owner_session")
    return {"ok": True}


# ---------------------------------------------------------------------------
# 회원가입
# ---------------------------------------------------------------------------
signup_router = APIRouter(tags=["auth"])


@signup_router.post("/signup")
async def register(
    body: SignupRequest,
    response: Response,
    db: Session = Depends(get_sync_db),
    session_store: SessionStorePort = Depends(get_session_store),
) -> UserResponse:
    if body.password != body.password_confirm:
        raise HTTPException(status_code=422, detail="비밀번호가 일치하지 않습니다.")
    if len(body.password) < 6:
        raise HTTPException(status_code=422, detail="비밀번호는 6자 이상이어야 합니다.")
    if not body.agree_terms:
        raise HTTPException(status_code=422, detail="이용약관 및 개인정보처리방침에 동의해야 합니다.")

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
        region=body.region.strip() if body.region and body.region.strip() else None,
        created_at=datetime.now(timezone.utc),
        policy_agreed_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.flush()
    db.refresh(user)
    await _start_session(response, user, session_store)
    return _user_response(user)


# ---------------------------------------------------------------------------
# 로그인
# ---------------------------------------------------------------------------
login_router = APIRouter(tags=["auth"])


@login_router.post("/login")
async def login(
    body: LoginRequest,
    response: Response,
    db: Session = Depends(get_sync_db),
    session_store: SessionStorePort = Depends(get_session_store),
) -> UserResponse:
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
    await _start_session(response, user, session_store)
    return _user_response(user)
# ---------------------------------------------------------------------------
@auth_router.post("/google")
async def google_login(
    body: GoogleLoginRequest,
    response: Response,
    db: Session = Depends(get_sync_db),
    session_store: SessionStorePort = Depends(get_session_store),
) -> GoogleLoginResponse | PendingConsentResponse:
    """Google ID 토큰 검증 후 로그인(기존) 또는 약관 동의 대기(신규)."""
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

    user = find_existing_user(db, provider="GOOGLE", sub=google_sub, email=email)
    if user is None:
        # 신규 사용자 — 계정을 바로 만들지 않고 약관 동의부터 받는다.
        token = await create_pending_signup(
            provider="GOOGLE", sub=google_sub, email=email, name=name
        )
        return PendingConsentResponse(consent_token=token, email=email, nickname=name)

    user.last_login_at = datetime.now(timezone.utc)
    db.flush()
    await _start_session(response, user, session_store)

    owner_token = issue_owner_token(email)
    if owner_token:
        response.set_cookie(
            "wr_owner_session",
            owner_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 30,
        )
    else:
        response.delete_cookie("wr_owner_session")

    return GoogleLoginResponse(**_user_response(user).model_dump(), is_owner=owner_token is not None)
