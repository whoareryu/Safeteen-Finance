from functools import lru_cache

from user.adapter.outbound.pg.onboarding_pg_repository import OnboardingPgRepository
from user.app.ports.input.onboarding_use_case import OnboardingUseCase
from user.app.use_cases.onboarding_interactor import OnboardingInteractor


@lru_cache
def get_onboarding_use_case() -> OnboardingUseCase:
    return OnboardingInteractor(repository=OnboardingPgRepository())
