"""카카오 id_token 검증 결과 — 프레임워크 의존 없는 순수 도메인 모델."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KakaoIdentity:
    sub: str
    email: str | None
    nickname: str | None
