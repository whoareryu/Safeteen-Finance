from __future__ import annotations

from sqlalchemy.orm import Session

from apps.auth.user_model import User
from user.app.dtos.onboarding_dto import OnboardingSubmitCommand, UserPreferenceView
from user.app.ports.input.onboarding_use_case import OnboardingUseCase
from user.app.ports.output.onboarding_repository import OnboardingRepository


class OnboardingInteractor(OnboardingUseCase):
    def __init__(self, repository: OnboardingRepository) -> None:
        self._repository = repository

    def submit(
        self, db: Session, user: User, command: OnboardingSubmitCommand
    ) -> UserPreferenceView:
        return self._repository.upsert(db, user_id=user.id, command=command)

    def get_preference(self, db: Session, user_id: int) -> UserPreferenceView | None:
        return self._repository.get_by_user(db, user_id)
