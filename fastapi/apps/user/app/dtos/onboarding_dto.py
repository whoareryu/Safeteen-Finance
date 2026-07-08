from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OnboardingSubmitCommand:
    """온보딩 5단계 입력 (기획서 3-1)."""

    genre_ranking: list[str]  # Step1: 한식/중식/일식/양식/분식/아시안 선호 순위
    dining_mode: str  # Step2: dine_in / delivery / pickup
    portion: str  # Step3: under_one / one / one_half / two_plus
    allergies: list[str] = field(default_factory=list)  # Step4
    avoid_foods: list[str] = field(default_factory=list)  # Step4
    use_budget: bool = False  # Step5 (선택)
    monthly_budget: int | None = None  # Step5: 버짓 사용 시 월 예산(원)


@dataclass(frozen=True)
class UserPreferenceView:
    genre_ranking: list[str]
    dining_mode: str
    portion: str
    allergies: list[str]
    avoid_foods: list[str]
    use_budget: bool
    monthly_budget: int | None = None
