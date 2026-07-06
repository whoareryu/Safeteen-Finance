"""소유자(owner) 전용 세션 서명 — 특정 구글 계정으로 로그인했을 때만 통과시키기 위한 최소 HMAC 서명."""
from __future__ import annotations

import hashlib
import hmac
import os

OWNER_EMAIL = os.environ["OWNER_EMAIL"].strip().lower()
_SECRET = os.environ["OWNER_SESSION_SECRET"]


def _sign(email: str) -> str:
    return hmac.new(_SECRET.encode(), email.encode(), hashlib.sha256).hexdigest()


def issue_owner_token(email: str) -> str | None:
    """owner 이메일일 때만 서명된 토큰을 발급한다. 그 외에는 None."""
    email = email.strip().lower()
    if email != OWNER_EMAIL:
        return None
    return f"{email}.{_sign(email)}"


def is_valid_owner_token(token: str | None) -> bool:
    if not token or "." not in token:
        return False
    email, sig = token.rsplit(".", 1)
    return email == OWNER_EMAIL and hmac.compare_digest(sig, _sign(email))
