"""auth 서비스(auth_main.py) 전용 Pydantic 스키마.

기존 apps/auth/auth_endpoints.py·consent_router.py에 있던 스키마를 그대로
옮겨왔다 — 프론트(www/lib/auth.ts)가 이미 이 응답 형태를 그대로 소비하므로
필드를 바꾸지 않는다. Google/Naver/Kakao 모두 팝업+서버측 리다이렉트 방식으로
통일된 뒤로는 로그인 자체가 JSON 응답이 아니라 리다이렉트라, 로그인 전용
요청/응답 스키마(예전의 GoogleCallbackRequest 등)는 없다.
"""
from __future__ import annotations

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    email: str
    role: str
    region: str | None = None


class UpdateNicknameRequest(BaseModel):
    nickname: str


class ConsentCompleteRequest(BaseModel):
    consent_token: str
    nickname: str
    agree_terms: bool
