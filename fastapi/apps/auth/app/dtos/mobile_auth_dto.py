from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class MobileKakaoLoginCommand:
    id_token: str
    nonce: str
    device_id: str


@dataclass(frozen=True)
class MobileConsentCompleteCommand:
    consent_token: str
    nickname: str
    agree_terms: bool
    device_id: str


@dataclass(frozen=True)
class MobileRefreshCommand:
    refresh_token: str


@dataclass(frozen=True)
class MobileLogoutCommand:
    sub: str
    jti: str
    platform: str


@dataclass(frozen=True)
class MobileAuthTokens:
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


@dataclass(frozen=True)
class MobileLoginResult:
    """카카오 id_token 검증 후 결과 — 기존 유저면 tokens가 채워지고,
    신규 유저면 동의가 필요해 consent_token/suggested_nickname이 채워진다.
    """

    status: Literal["logged_in", "consent_required"]
    tokens: MobileAuthTokens | None = None
    is_new_user: bool | None = None
    consent_token: str | None = None
    suggested_nickname: str | None = None


@dataclass(frozen=True)
class MobileUserRecord:
    id: int
    role: str


@dataclass(frozen=True)
class PendingSignup:
    provider: str
    sub: str
    email: str
    name: str
