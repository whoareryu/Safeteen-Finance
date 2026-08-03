from __future__ import annotations

from abc import ABC, abstractmethod

from apps.auth.app.dtos.mobile_auth_dto import MobileUserRecord


class MobileUserRepositoryPort(ABC):

    @abstractmethod
    def find_existing(self, *, provider: str, sub: str, email: str) -> MobileUserRecord | None:
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> MobileUserRecord | None:
        pass

    @abstractmethod
    def nickname_exists(self, nickname: str) -> bool:
        pass

    @abstractmethod
    def create(self, *, provider: str, sub: str, email: str, nickname: str) -> MobileUserRecord:
        """policy_agreed_at을 현재 시각으로 채워 생성한다(모바일도 동의 완료 후에만 호출됨)."""
