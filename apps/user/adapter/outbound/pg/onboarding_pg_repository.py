from __future__ import annotations

from sqlalchemy.orm import Session

from user.adapter.outbound.orm.user_preference_orm import UserPreference
from user.app.dtos.onboarding_dto import OnboardingSubmitCommand, UserPreferenceView
from user.app.ports.output.onboarding_repository import OnboardingRepository


class OnboardingPgRepository(OnboardingRepository):
    def upsert(
        self, db: Session, *, user_id: int, command: OnboardingSubmitCommand
    ) -> UserPreferenceView:
        pref = (
            db.query(UserPreference).filter(UserPreference.user_id == user_id).one_or_none()
        )
        if pref is None:
            pref = UserPreference(user_id=user_id)
            db.add(pref)
        pref.genre_ranking = command.genre_ranking
        pref.dining_mode = command.dining_mode
        pref.portion = command.portion
        pref.allergies = command.allergies
        pref.avoid_foods = command.avoid_foods
        pref.use_budget = command.use_budget
        pref.monthly_budget = command.monthly_budget
        db.commit()
        db.refresh(pref)
        return self._to_view(pref)

    def get_by_user(self, db: Session, user_id: int) -> UserPreferenceView | None:
        pref = (
            db.query(UserPreference).filter(UserPreference.user_id == user_id).one_or_none()
        )
        return self._to_view(pref) if pref else None

    @staticmethod
    def _to_view(pref: UserPreference) -> UserPreferenceView:
        return UserPreferenceView(
            genre_ranking=list(pref.genre_ranking or []),
            dining_mode=pref.dining_mode or "",
            portion=pref.portion or "",
            allergies=list(pref.allergies or []),
            avoid_foods=list(pref.avoid_foods or []),
            use_budget=bool(pref.use_budget),
            monthly_budget=pref.monthly_budget,
        )
