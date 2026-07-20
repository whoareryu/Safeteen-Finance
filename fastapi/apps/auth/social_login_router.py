"""Naver·Kakao 로그인 — 서버사이드 OAuth 인가코드 리다이렉트 플로우.

Google(JS credential 팝업 방식, auth_endpoints.py)과 달리 Naver/Kakao는 버튼을
누르면 페이지 전체가 이동했다가 콜백에서 돌아오는 방식이다. 기존 사용자는 바로
로그인(_start_session)하고, 신규 사용자는 계정을 만들지 않고 약관 동의 페이지
(www `/auth/consent`)로 보낸다 — 동의 완료는 apps/auth/consent_router.py가 처리.
"""
from __future__ import annotations

import os
import secrets
from datetime import datetime, timezone
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Cookie, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from apps.auth.auth_endpoints import _start_session
from apps.auth.consent_flow import create_pending_signup
from apps.auth.session_store import SessionStorePort, get_session_store
from apps.auth.user_provisioning import find_existing_user
from apps.database import get_sync_db

_FRONTEND_URL = os.getenv("FRONTEND_URL", "https://whoareryu.cloud")
_BACKEND_URL = os.environ["BACKEND_PUBLIC_URL"]

social_login_router = APIRouter(prefix="/auth", tags=["auth"])


async def _login_or_redirect_to_consent(
    *, provider: str, sub: str, email: str, name: str, db: Session, session_store: SessionStorePort
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
    # 로그인 버튼이 팝업 창으로 여는 흐름이라, 팝업이 부모 창에 알리고 스스로 닫는
    # 페이지로 보낸다 (www/app/auth/popup-complete).
    redirect = RedirectResponse(f"{_FRONTEND_URL}/auth/popup-complete")
    await _start_session(redirect, user, session_store)
    return redirect


# ---------------------------------------------------------------------------
# Naver
# ---------------------------------------------------------------------------
_NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
_NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")
_NAVER_REDIRECT_URI = f"{_BACKEND_URL}/auth/naver/callback"


@social_login_router.get("/naver/login")
def naver_login() -> RedirectResponse:
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


@social_login_router.get("/naver/callback")
async def naver_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    wr_oauth_state_naver: str | None = Cookie(default=None),
    db: Session = Depends(get_sync_db),
    session_store: SessionStorePort = Depends(get_session_store),
) -> RedirectResponse:
    if error or not code or not state or not wr_oauth_state_naver:
        raise HTTPException(status_code=401, detail="Naver 인증이 취소되었거나 실패했습니다.")
    if not secrets.compare_digest(wr_oauth_state_naver, state):
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
        provider="NAVER", sub=naver_id, email=email, name=name, db=db, session_store=session_store
    )
    redirect.delete_cookie("wr_oauth_state_naver")
    return redirect


# ---------------------------------------------------------------------------
# Kakao
# ---------------------------------------------------------------------------
_KAKAO_CLIENT_ID = os.getenv("KAKAO_REST_API_KEY", "")
_KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "")
_KAKAO_REDIRECT_URI = f"{_BACKEND_URL}/auth/kakao/callback"


@social_login_router.get("/kakao/login")
def kakao_login() -> RedirectResponse:
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


@social_login_router.get("/kakao/callback")
async def kakao_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    wr_oauth_state_kakao: str | None = Cookie(default=None),
    db: Session = Depends(get_sync_db),
    session_store: SessionStorePort = Depends(get_session_store),
) -> RedirectResponse:
    if error or not code or not state or not wr_oauth_state_kakao:
        raise HTTPException(status_code=401, detail="Kakao 인증이 취소되었거나 실패했습니다.")
    if not secrets.compare_digest(wr_oauth_state_kakao, state):
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
        provider="KAKAO", sub=kakao_id, email=email, name=name, db=db, session_store=session_store
    )
    redirect.delete_cookie("wr_oauth_state_kakao")
    return redirect
