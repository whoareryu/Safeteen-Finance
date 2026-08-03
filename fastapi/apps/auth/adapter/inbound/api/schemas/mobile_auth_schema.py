"""auth_main.py 기존 스키마(apps/auth/schemas.py)와 동일하게 snake_case 컨벤션을 쓴다."""
from __future__ import annotations

from pydantic import BaseModel


class MobileKakaoLoginRequestSchema(BaseModel):
    id_token: str
    nonce: str
    device_id: str


class MobileConsentCompleteRequestSchema(BaseModel):
    consent_token: str
    nickname: str
    agree_terms: bool
    device_id: str


class MobileRefreshRequestSchema(BaseModel):
    refresh_token: str


class MobileKakaoLoginResponseSchema(BaseModel):
    status: str  # "logged_in" | "consent_required"
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str | None = None
    expires_in: int | None = None
    is_new_user: bool | None = None
    consent_token: str | None = None
    suggested_nickname: str | None = None


class MobileAuthTokensResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
