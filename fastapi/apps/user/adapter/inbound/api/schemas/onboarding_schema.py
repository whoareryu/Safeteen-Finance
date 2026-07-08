from __future__ import annotations

from pydantic import BaseModel, Field


class OnboardingSubmitRequest(BaseModel):
    """온보딩 5단계 제출 (기획서 3-1)."""

    genre_ranking: list[str] = Field(default_factory=list)
    dining_mode: str = ""
    portion: str = ""
    allergies: list[str] = Field(default_factory=list)
    avoid_foods: list[str] = Field(default_factory=list)
    use_budget: bool = False
    monthly_budget: int | None = None


class UserPreferenceResponse(BaseModel):
    completed: bool
    genre_ranking: list[str] = Field(default_factory=list)
    dining_mode: str = ""
    portion: str = ""
    allergies: list[str] = Field(default_factory=list)
    avoid_foods: list[str] = Field(default_factory=list)
    use_budget: bool = False
    monthly_budget: int | None = None
