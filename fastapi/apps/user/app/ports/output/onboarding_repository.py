from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from user.app.dtos.onboarding_dto import OnboardingSubmitCommand, UserPreferenceView


class OnboardingRepository(ABC):
    """user_preferences 영속화 포트."""

    @abstractmethod
    def upsert(
        self, db: Session, *, user_id: int, command: OnboardingSubmitCommand
    ) -> UserPreferenceView:
        ...

    @abstractmethod
    def get_by_user(self, db: Session, user_id: int) -> UserPreferenceView | None:
        ...
