"""온보딩 API — ``X-User-Id`` 헤더 인증 (기획서 3-1)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.auth.dependencies import get_current_user
from apps.auth.user_model import User
from apps.database import get_sync_db
from user.adapter.inbound.api.schemas.onboarding_schema import (
    OnboardingSubmitRequest,
    UserPreferenceResponse,
)
from user.app.dtos.onboarding_dto import OnboardingSubmitCommand, UserPreferenceView
from user.app.ports.input.onboarding_use_case import OnboardingUseCase
from user.dependencies.onboarding_provider import get_onboarding_use_case

onboarding_router = APIRouter(prefix="/gourmet/onboarding", tags=["gourmet-onboarding"])
router = onboarding_router


def _to_response(view: UserPreferenceView | None) -> UserPreferenceResponse:
    if view is None:
        return UserPreferenceResponse(completed=False)
    return UserPreferenceResponse(
        completed=True,
        genre_ranking=view.genre_ranking,
        dining_mode=view.dining_mode,
        portion=view.portion,
        allergies=view.allergies,
        avoid_foods=view.avoid_foods,
        use_budget=view.use_budget,
        monthly_budget=view.monthly_budget,
    )


@onboarding_router.get("/me", response_model=UserPreferenceResponse)
def read_my_preference(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
    use_case: OnboardingUseCase = Depends(get_onboarding_use_case),
) -> UserPreferenceResponse:
    return _to_response(use_case.get_preference(db, user.id))


@onboarding_router.post("", response_model=UserPreferenceResponse)
def submit_onboarding(
    body: OnboardingSubmitRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
    use_case: OnboardingUseCase = Depends(get_onboarding_use_case),
) -> UserPreferenceResponse:
    view = use_case.submit(
        db,
        user,
        OnboardingSubmitCommand(
            genre_ranking=body.genre_ranking,
            dining_mode=body.dining_mode,
            portion=body.portion,
            allergies=body.allergies,
            avoid_foods=body.avoid_foods,
            use_budget=body.use_budget,
            monthly_budget=body.monthly_budget,
        ),
    )
    return _to_response(view)
