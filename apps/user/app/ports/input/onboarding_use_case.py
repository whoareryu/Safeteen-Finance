from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from apps.auth.user_model import User
from user.app.dtos.onboarding_dto import OnboardingSubmitCommand, UserPreferenceView


class OnboardingUseCase(ABC):
    """온보딩 입력 저장 / 취향 스냅샷 조회 (기획서 3-1)."""

    @abstractmethod
    def submit(
        self, db: Session, user: User, command: OnboardingSubmitCommand
    ) -> UserPreferenceView:
        ...

    @abstractmethod
    def get_preference(self, db: Session, user_id: int) -> UserPreferenceView | None:
        ...
