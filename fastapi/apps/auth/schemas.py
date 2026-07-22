"""auth 서비스(auth_main.py) 전용 Pydantic 스키마.

기존 apps/auth/auth_endpoints.py·consent_router.py에 있던 스키마를 그대로
옮겨왔다 — 프론트(www/lib/auth.ts)가 이미 이 응답 형태를 그대로 소비하므로
필드를 바꾸지 않는다.
"""
from __future__ import annotations

from pydantic import BaseModel


class GoogleCallbackRequest(BaseModel):
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


class ConsentCompleteRequest(BaseModel):
    consent_token: str
    nickname: str
    agree_terms: bool
