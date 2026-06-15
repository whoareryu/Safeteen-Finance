"""meal_plan internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MealPlanQuery:
    pass


@dataclass(frozen=True)
class MealPlanIntroResponse:
    id: int
    name: str
