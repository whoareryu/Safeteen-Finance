"""auth 서비스 비즈니스 로직 — OAuth Provider 연동, 토큰 발급 오케스트레이션.

기존 apps/auth/auth_endpoints.py(Google)·social_login_router.py(Naver/Kakao)·
consent_router.py(신규가입 완료)의 로직을 그대로 옮기되, 토큰 발급만
jwt_service(HS256)+session_store(Redis 허용목록) 조합에서
core.security(RS256)+refresh 토큰 로테이션 조합으로 바꿨다. OAuth API 호출·
사용자 조회/생성 로직(user_provisioning.py)은 손대지 않고 그대로 재사용한다.
"""
from __future__ import annotations

import os
import secrets
from datetime import datetime, timezone
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.auth.consent_flow import create_pending_signup, pop_pending_signup
from apps.auth.owner_session import issue_owner_token
from apps.auth.schemas import (
    ConsentCompleteRequest,
    GoogleLoginResponse,
    PendingConsentResponse,
    UserResponse,
)
from apps.auth.user_model import User
from apps.auth.user_provisioning import create_oauth_user, find_existing_user
from apps.auth.user_role import UserRole
from core import security

_AUD = os.getenv("SERVICE_AUD", "whoareryu-api")
_FRONTEND_URL = os.getenv("FRONTEND_URL", "https://whoareryu.cloud")
_BACKEND_URL = os.environ["BACKEND_PUBLIC_URL"]  # 문서상 auth 컨테이너 자신의 공개 URL


def user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        role=user.role.value if isinstance(user.role, UserRole) else str(user.role),
        region=user.region,
    )


async def start_session(response: Response, user: User) -> None:
    """로그인 성공 시 RS256 액세스 토큰 + 리프레시 토�큰을 발급해 쿠키로 내려준다."""
    roles = [user.role.value if isinstance(user.role, UserRole) else str(user.role)]
    access_token = security.create_access_token(sub=str(user.id), roles=roles, aud=_AUD)
    refresh_token = await security.create_refresh_token(sub=str(user.id))

    response.set_cookie(
        "wr_session",
        access_token,
        max_age=security.ACCESS_TOKEN_TTL_MIN_DEFAULT * 60,
        **security.COOKIE_KWARGS,
    )
    response.set_cookie(
        "wr_refresh",
        refresh_token,
        max_age=security.REFRESH_TOKEN_TTL_SECONDS,
        **security.COOKIE_KWARGS,
    )


def _set_or_clear_owner_cookie(response: Response, email: str) -> bool:
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
    return owner_token is not None


# ---------------------------------------------------------------------------
# Google
# ---------------------------------------------------------------------------
async def google_login(
    credential: str, response: Response, db: Session
) -> GoogleLoginResponse | PendingConsentResponse:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": credential},
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
        token = await create_pending_signup(
            provider="GOOGLE", sub=google_sub, email=email, name=name
        )
        return PendingConsentResponse(consent_token=token, email=email, nickname=name)

    user.last_login_at = datetime.now(timezone.utc)
    db.flush()
    await start_session(response, user)
    is_owner = _set_or_clear_owner_cookie(response, email)

    return GoogleLoginResponse(**user_response(user).model_dump(), is_owner=is_owner)


# ---------------------------------------------------------------------------
# Naver / Kakao 공통 — 인가코드 콜백 이후 로그인 또는 약관동의 리다이렉트
# ---------------------------------------------------------------------------
async def _login_or_redirect_to_consent(
    *, provider: str, sub: str, email: str, name: str, db: Session
) -> RedirectResponse:
    user = find_existing_user(db, provider=provider, sub=sub, email=email)
    if user is None:
        token = await create_pending_signup(provider=provider, sub=sub, email=email, name=name)
        return RedirectResponse(
            f"{_FRONTEND_URL}/auth/consent?"
            f"{urlencode({'token': token, 'email': email, 'nickname': name})}"
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.flush()
    redirect = RedirectResponse(f"{_FRONTEND_URL}/auth/popup-complete")
    await start_session(redirect, user)
    _set_or_clear_owner_cookie(redirect, email)
    return redirect


_NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
_NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")
_NAVER_REDIRECT_URI = f"{_BACKEND_URL}/auth/naver/callback"


def naver_login_redirect() -> RedirectResponse:
    if not _NAVER_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Naver 로그인이 설정되지 않았습니다.")
    state = secrets.token_urlsafe(16)
    params = {
        "response_type": "code",
        "client_id": _NAVER_CLIENT_ID,
        "redirect_uri": _NAVER_REDIRECT_URI,
        "state": state,
    }
    resp = RedirectResponse(f"https://nid.naver.com/oauth2.0/authorize?{urlencode(params)}")
    resp.set_cookie(
        "wr_oauth_state_naver", state, httponly=True, secure=True, samesite="lax", max_age=300
    )
    return resp


async def naver_callback(
    *, code: str | None, state: str | None, error: str | None, state_cookie: str | None, db: Session
) -> RedirectResponse:
    if error or not code or not state or not state_cookie:
        raise HTTPException(status_code=401, detail="Naver 인증이 취소되었거나 실패했습니다.")
    if not secrets.compare_digest(state_cookie, state):
        raise HTTPException(status_code=401, detail="잘못된 인증 요청입니다.")

    async with httpx.AsyncClient() as client:
        token_resp = await client.get(
            "https://nid.naver.com/oauth2.0/token",
            params={
                "grant_type": "authorization_code",
                "client_id": _NAVER_CLIENT_ID,
                "client_secret": _NAVER_CLIENT_SECRET,
                "code": code,
                "state": state,
            },
            timeout=10.0,
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Naver 토큰 교환에 실패했습니다.")
        access_token = token_resp.json().get("access_token")

        profile_resp = await client.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10.0,
        )
    if profile_resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Naver 프로필 조회에 실패했습니다.")

    info = profile_resp.json().get("response", {})
    naver_id: str = info.get("id", "")
    email: str = (info.get("email") or "").strip().lower()
    name: str = info.get("nickname") or info.get("name") or "사용자"
    if not naver_id or not email:
        raise HTTPException(status_code=401, detail="Naver 계정 정보를 가져올 수 없습니다.")

    redirect = await _login_or_redirect_to_consent(
        provider="NAVER", sub=naver_id, email=email, name=name, db=db
    )
    redirect.delete_cookie("wr_oauth_state_naver")
    return redirect


_KAKAO_CLIENT_ID = os.getenv("KAKAO_REST_API_KEY", "")
_KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "")
_KAKAO_REDIRECT_URI = f"{_BACKEND_URL}/auth/kakao/callback"


def kakao_login_redirect() -> RedirectResponse:
    if not _KAKAO_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Kakao 로그인이 설정되지 않았습니다.")
    state = secrets.token_urlsafe(16)
    params = {
        "response_type": "code",
        "client_id": _KAKAO_CLIENT_ID,
        "redirect_uri": _KAKAO_REDIRECT_URI,
        "state": state,
    }
    resp = RedirectResponse(f"https://kauth.kakao.com/oauth/authorize?{urlencode(params)}")
    resp.set_cookie(
        "wr_oauth_state_kakao", state, httponly=True, secure=True, samesite="lax", max_age=300
    )
    return resp


async def kakao_callback(
    *, code: str | None, state: str | None, error: str | None, state_cookie: str | None, db: Session
) -> RedirectResponse:
    if error or not code or not state or not state_cookie:
        raise HTTPException(status_code=401, detail="Kakao 인증이 취소되었거나 실패했습니다.")
    if not secrets.compare_digest(state_cookie, state):
        raise HTTPException(status_code=401, detail="잘못된 인증 요청입니다.")

    token_data = {
        "grant_type": "authorization_code",
        "client_id": _KAKAO_CLIENT_ID,
        "redirect_uri": _KAKAO_REDIRECT_URI,
        "code": code,
    }
    if _KAKAO_CLIENT_SECRET:
        token_data["client_secret"] = _KAKAO_CLIENT_SECRET

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://kauth.kakao.com/oauth/token", data=token_data, timeout=10.0
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Kakao 토큰 교환에 실패했습니다.")
        access_token = token_resp.json().get("access_token")

        profile_resp = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10.0,
        )
    if profile_resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Kakao 프로필 조회에 실패했습니다.")

    info = profile_resp.json()
    kakao_id = str(info.get("id", ""))
    account = info.get("kakao_account", {})
    email: str = (account.get("email") or f"kakao_{kakao_id}@kakao.local").strip().lower()
    name: str = (account.get("profile") or {}).get("nickname") or "사용자"
    if not kakao_id:
        raise HTTPException(status_code=401, detail="Kakao 계정 정보를 가져올 수 없습니다.")

    redirect = await _login_or_redirect_to_consent(
        provider="KAKAO", sub=kakao_id, email=email, name=name, db=db
    )
    redirect.delete_cookie("wr_oauth_state_kakao")
    return redirect


# ---------------------------------------------------------------------------
# 신규가입 약관동의 완료
# ---------------------------------------------------------------------------
async def complete_consent(
    body: ConsentCompleteRequest, response: Response, db: Session
) -> UserResponse:
    if not body.agree_terms:
        raise HTTPException(status_code=422, detail="이용약관 및 개인정보처리방침에 동의해야 합니다.")

    nickname = body.nickname.strip()
    if not nickname:
        raise HTTPException(status_code=422, detail="닉네임을 입력해 주세요.")
    exists = db.execute(
        select(User).where(func.lower(User.nickname) == nickname.lower()).limit(1)
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="이미 사용 중인 닉네임입니다.")

    pending = await pop_pending_signup(body.consent_token)
    if pending is None:
        raise HTTPException(status_code=400, detail="만료되었거나 잘못된 요청입니다. 다시 로그인해 주세요.")

    user = create_oauth_user(
        db,
        provider=pending["provider"],
        sub=pending["sub"],
        email=pending["email"],
        nickname=nickname,
    )
    now = datetime.now(timezone.utc)
    user.policy_agreed_at = now
    user.last_login_at = now
    db.flush()
    await start_session(response, user)
    _set_or_clear_owner_cookie(response, user.email)
    return user_response(user)


# ---------------------------------------------------------------------------
# 세션 갱신 · 로그아웃
# ---------------------------------------------------------------------------
async def refresh_session(refresh_token: str | None, response: Response, db: Session) -> UserResponse:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="리프레시 토큰이 없습니다.")

    result = await security.rotate_refresh_token(refresh_token)
    if result is None:
        response.delete_cookie("wr_session", domain=os.getenv("COOKIE_DOMAIN") or None)
        response.delete_cookie("wr_refresh", domain=os.getenv("COOKIE_DOMAIN") or None)
        raise HTTPException(status_code=401, detail="세션이 만료되었습니다. 다시 로그인해 주세요.")

    sub, new_refresh_token = result
    user = db.get(User, int(sub))
    if user is None:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")

    roles = [user.role.value if isinstance(user.role, UserRole) else str(user.role)]
    access_token = security.create_access_token(sub=sub, roles=roles, aud=_AUD)
    response.set_cookie(
        "wr_session",
        access_token,
        max_age=security.ACCESS_TOKEN_TTL_MIN_DEFAULT * 60,
        **security.COOKIE_KWARGS,
    )
    response.set_cookie(
        "wr_refresh",
        new_refresh_token,
        max_age=security.REFRESH_TOKEN_TTL_SECONDS,
        **security.COOKIE_KWARGS,
    )
    return user_response(user)


async def logout(sub: str | None, jti: str | None, response: Response) -> None:
    if sub:
        await security.revoke_refresh_family(sub)
    if jti:
        await security.blacklist_token(jti, ttl_seconds=security.ACCESS_TOKEN_TTL_MIN_DEFAULT * 60)
    cookie_domain = os.getenv("COOKIE_DOMAIN") or None
    response.delete_cookie("wr_session", domain=cookie_domain)
    response.delete_cookie("wr_refresh", domain=cookie_domain)
    response.delete_cookie("wr_owner_session")
