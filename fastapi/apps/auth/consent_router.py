"""OAuth 신규 가입자가 닉네임 설정·약관 동의를 완료하면 계정을 확정 생성한다."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.auth.auth_endpoints import UserResponse, _start_session, _user_response
from apps.auth.consent_flow import pop_pending_signup
from apps.auth.session_store import SessionStorePort, get_session_store
from apps.auth.user_model import User
from apps.auth.user_provisioning import create_oauth_user
from apps.database import get_sync_db

consent_router = APIRouter(prefix="/auth/consent", tags=["auth"])


class ConsentCompleteRequest(BaseModel):
    consent_token: str
    nickname: str
    agree_terms: bool


@consent_router.post("/complete", response_model=UserResponse)
async def complete_consent(
    body: ConsentCompleteRequest,
    response: Response,
    db: Session = Depends(get_sync_db),
    session_store: SessionStorePort = Depends(get_session_store),
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
    await _start_session(response, user, session_store)
    return _user_response(user)
