from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VisitConfirmCommand:
    """GPS 방문 감지 후 방문 확인 + 별점 (기획서 4-2)."""

    restaurant_id: int
    rating: int | None = None  # 1~5, 미평가 시 None
    latitude: float | None = None
    longitude: float | None = None


@dataclass(frozen=True)
class VisitView:
    restaurant_id: int
    rating: int | None
    confirmed: bool
