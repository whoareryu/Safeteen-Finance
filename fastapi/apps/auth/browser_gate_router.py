"""api.whoareryu.cloud에 브라우저로 직접 접근할 때만 Google 로그인으로 막는 라우터.

/api/* 등 www 프론트엔드가 호출하는 엔드포인트는 대상이 아니다 — 사람이 주소창에
직접 입력해서 보는 화면(GATED_PATHS)만 대상. main.py의 미들웨어가 이 화면 요청을
가로채 여기로 리다이렉트한다.
"""
from __future__ import annotations

import os
import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Cookie, HTTPException, Query
from fastapi.responses import RedirectResponse

from apps.auth.owner_session import issue_owner_token

GATED_PATHS = {"/", "/docs", "/redoc", "/openapi.json"}

_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
_REDIRECT_URI = f"{os.environ['BACKEND_PUBLIC_URL']}/auth/google/browser-callback"

browser_gate_router = APIRouter(prefix="/auth/google", tags=["auth"])


@browser_gate_router.get("/browser-login")
def browser_login(next: str = Query(default="/")) -> RedirectResponse:
    target = next if next in GATED_PATHS else "/"
    state = secrets.token_urlsafe(16)
    params = {
        "client_id": _CLIENT_ID,
        "redirect_uri": _REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email",
        "state": state,
        "prompt": "select_account",
    }
    resp = RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}")
    resp.set_cookie(
        "wr_oauth_state",
        f"{state}:{target}",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=300,
    )
    return resp


@browser_gate_router.get("/browser-callback")
async def browser_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    wr_oauth_state: str | None = Cookie(default=None),
) -> RedirectResponse:
    if error or not code or not state or not wr_oauth_state:
        raise HTTPException(status_code=401, detail="Google 인증이 취소되었거나 실패했습니다.")

    saved_state, _, target = wr_oauth_state.partition(":")
    if not secrets.compare_digest(saved_state, state):
        raise HTTPException(status_code=401, detail="잘못된 인증 요청입니다.")
    target = target if target in GATED_PATHS else "/"

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": _CLIENT_ID,
                "client_secret": _CLIENT_SECRET,
                "redirect_uri": _REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=10.0,
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Google 토큰 교환에 실패했습니다.")

        userinfo_resp = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token_resp.json().get('access_token')}"},
            timeout=10.0,
        )
    if userinfo_resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Google 사용자 정보를 가져오지 못했습니다.")

    email = userinfo_resp.json().get("email", "").strip().lower()
    owner_token = issue_owner_token(email)
    if owner_token is None:
        raise HTTPException(status_code=403, detail="허용되지 않은 계정입니다.")

    resp = RedirectResponse(target)
    resp.delete_cookie("wr_oauth_state")
    # 이 게이트 전용 — 짧게만 유지해서 재방문할 때마다 다시 Google 로그인을 타게 한다.
    # (채팅 등 다른 owner 전용 기능이 쓰는 wr_owner_session의 30일 쿠키와는 별개.)
    resp.set_cookie(
        "wr_docs_gate",
        owner_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60,
    )
    return resp
