"""auth 서비스(auth_main.py) 라우터.

기존 apps/auth/auth_endpoints.py·social_login_router.py·consent_router.py가
쓰던 경로를 그대로 유지한다 — 프론트(www/lib/auth.ts, auth-modal.tsx)가 이미
이 경로들을 호출하고 있어서, Phase D에서는 "어느 호스트로 보내는지"만 바꾸면
되게 하기 위함이다. 여기 새로 추가된 건 POST /auth/refresh와
GET /.well-known/jwks.json뿐이다.
"""
from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.auth import services
from apps.auth.schemas import (
    ConsentCompleteRequest,
    GoogleCallbackRequest,
    GoogleLoginResponse,
    PendingConsentResponse,
    UpdateNicknameRequest,
    UserResponse,
)
from apps.auth.user_model import User
from apps.database import get_sync_db
from core.dependencies import get_current_user
from core.security import TokenPayload, public_jwk

router = APIRouter(prefix="/auth", tags=["auth"])
# JWKS는 RFC 5785 well-known URI 관례상 도메인 루트에 있어야 해서 /auth 프리픽스 밖에 둔다.
jwks_router = APIRouter(tags=["auth"])


def _load_current_user(payload: TokenPayload, db: Session) -> User:
    user = db.get(User, int(payload.sub))
    if user is None:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")
    return user


# ---------------------------------------------------------------------------
# 닉네임
# ---------------------------------------------------------------------------
@router.get("/check-nickname")
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


@router.patch("/nickname", response_model=UserResponse)
def update_nickname(
    body: UpdateNicknameRequest,
    payload: TokenPayload = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
) -> UserResponse:
    current_user = _load_current_user(payload, db)
    nick = body.nickname.strip()
    if not nick:
        raise HTTPException(status_code=422, detail="닉네임을 입력해 주세요.")
    exists = db.execute(
        select(User).where(func.lower(User.nickname) == nick.lower(), User.id != current_user.id)
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="이미 사용 중인 닉네임입니다.")
    current_user.nickname = nick
    db.flush()
    return services.user_response(current_user)


# ---------------------------------------------------------------------------
# 내 정보 · 세션
# ---------------------------------------------------------------------------
# owner-check(/auth/owner-check)는 owner_session.py 기반이라 이번 RS256 재작성과
# 무관하다 — main.py(api.whoareryu.cloud)에 그대로 남겨뒀다. www의
# app/portfolio/titanic/(lesson)/layout.tsx가 여전히 백엔드 도메인으로 직접
# 호출하고 있어서, 여기로 옮기면 그 파일까지 고쳐야 했다.


@router.get("/session", response_model=UserResponse)
def get_session(
    payload: TokenPayload = Depends(get_current_user), db: Session = Depends(get_sync_db)
) -> UserResponse:
    return services.user_response(_load_current_user(payload, db))


@router.post("/refresh", response_model=UserResponse)
async def refresh(
    response: Response,
    wr_refresh: str | None = Cookie(default=None),
    db: Session = Depends(get_sync_db),
) -> UserResponse:
    return await services.refresh_session(wr_refresh, response, db)


@router.post("/logout")
async def logout(
    response: Response,
    wr_session: str | None = Cookie(default=None),
) -> dict:
    sub, jti = None, None
    if wr_session:
        try:
            payload = await get_current_user(wr_session=wr_session, authorization=None)
            sub, jti = payload.sub, payload.jti
        except HTTPException:
            pass  # 이미 만료/무효인 토큰이면 그냥 쿠키만 지운다.
    await services.logout(sub, jti, response)
    return {"ok": True}


# ---------------------------------------------------------------------------
# Google
# ---------------------------------------------------------------------------
@router.post("/google")
async def google_login(
    body: GoogleCallbackRequest,
    response: Response,
    db: Session = Depends(get_sync_db),
) -> GoogleLoginResponse | PendingConsentResponse:
    return await services.google_login(body.credential, response, db)


# ---------------------------------------------------------------------------
# Naver
# ---------------------------------------------------------------------------
@router.get("/naver/login")
def naver_login():
    return services.naver_login_redirect()


@router.get("/naver/callback")
async def naver_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    wr_oauth_state_naver: str | None = Cookie(default=None),
    db: Session = Depends(get_sync_db),
):
    return await services.naver_callback(
        code=code, state=state, error=error, state_cookie=wr_oauth_state_naver, db=db
    )


# ---------------------------------------------------------------------------
# Kakao
# ---------------------------------------------------------------------------
@router.get("/kakao/login")
def kakao_login():
    return services.kakao_login_redirect()


@router.get("/kakao/callback")
async def kakao_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    wr_oauth_state_kakao: str | None = Cookie(default=None),
    db: Session = Depends(get_sync_db),
):
    return await services.kakao_callback(
        code=code, state=state, error=error, state_cookie=wr_oauth_state_kakao, db=db
    )


# ---------------------------------------------------------------------------
# 신규가입 약관동의 완료
# ---------------------------------------------------------------------------
@router.post("/consent/complete", response_model=UserResponse)
async def complete_consent(
    body: ConsentCompleteRequest,
    response: Response,
    db: Session = Depends(get_sync_db),
) -> UserResponse:
    return await services.complete_consent(body, response, db)


# ---------------------------------------------------------------------------
# JWKS — 백엔드/외부 검증자가 공개키를 가져가는 곳
# ---------------------------------------------------------------------------
@jwks_router.get("/.well-known/jwks.json")
def jwks() -> dict:
    return {"keys": [public_jwk()]}
