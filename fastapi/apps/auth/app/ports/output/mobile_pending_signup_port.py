from __future__ import annotations

from abc import ABC, abstractmethod

from apps.auth.app.dtos.mobile_auth_dto import PendingSignup


class PendingSignupPort(ABC):
    """신규 가입자가 동의를 완료하기 전까지 프로필을 임시 보관한다."""

    @abstractmethod
    async def create(self, *, provider: str, sub: str, email: str, name: str) -> str:
        """consent_token을 반환한다."""

    @abstractmethod
    async def pop(self, consent_token: str) -> PendingSignup | None:
        """1회 소비 — 만료/미존재 시 None."""
