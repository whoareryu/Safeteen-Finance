"""인증 엔드포인트 (Google OAuth · 닉네임 중복확인/수정 · 세션)."""
from __future__ import annotations

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

# Google 로그인은 프론트 프록시(whoareryu.cloud)를 거쳐 응답하지만, 네이버·카카오는
# OAuth state 쿠키 문제로 팝업이 api.whoareryu.cloud를 직접 연다(social_login_router
# 참고). 이 때문에 wr_session이 api.whoareryu.cloud에만 저장되면 whoareryu.cloud를 통해
# 오는 /api/auth/session 요청에는 쿠키가 붙지 않아 401이 난다. 두 도메인이 공유하는
# 상위 도메인을 명시해 서브도메인 어디서 로그인하든 같은 쿠키를 쓰게 한다.
_COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN") or None


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
        domain=_COOKIE_DOMAIN,
    )

auth_router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# 스키마
# ---------------------------------------------------------------------------
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


class UpdateNicknameRequest(BaseModel):
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
# 닉네임 중복확인·수정
# ---------------------------------------------------------------------------
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


@auth_router.patch("/nickname", response_model=UserResponse)
def update_nickname(
    body: UpdateNicknameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
) -> UserResponse:
    nick = body.nickname.strip()
    if not nick:
        raise HTTPException(status_code=422, detail="닉네임을 입력해 주세요.")
    exists = db.execute(
        select(User).where(
            func.lower(User.nickname) == nick.lower(), User.id != current_user.id
        )
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="이미 사용 중인 닉네임입니다.")
    current_user.nickname = nick
    db.flush()
    return _user_response(current_user)


# ---------------------------------------------------------------------------
# 내 정보 · 세션
# ---------------------------------------------------------------------------
@auth_router.get("/owner-check")
def owner_check(wr_owner_session: str | None = Cookie(default=None)) -> dict:
    return {"is_owner": is_valid_owner_token(wr_owner_session)}


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
    response.delete_cookie("wr_session", domain=_COOKIE_DOMAIN)
    response.delete_cookie("wr_owner_session")
    return {"ok": True}


# ---------------------------------------------------------------------------
# Google 로그인
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
        # 신규 사용자 — 계정을 바로 만들지 않고 약관 동의·닉네임 설정부터 받는다.
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
