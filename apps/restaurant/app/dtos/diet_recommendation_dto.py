from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DietQuery:
    """헬스 식단 질의 (기획서 3-4)."""

    diet_type: str  # high_protein / low_carb / ...
    district: str | None = None


@dataclass(frozen=True)
class DietView:
    diet_type: str
    restaurants: list[dict] = field(default_factory=list)
