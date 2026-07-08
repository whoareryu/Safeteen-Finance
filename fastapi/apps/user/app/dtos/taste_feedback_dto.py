from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeedbackCommand:
    """좋아요/싫어요/재방문 신호 + 맥락 (기획서 4-1)."""

    restaurant_id: int
    signal: str  # like / dislike / revisit
    time_slot: str | None = None  # morning / lunch / dinner
    weather: str | None = None  # 맥락 학습용 (기획서 "어떤 날씨에 싫어했는지")


@dataclass(frozen=True)
class DislikePatternView:
    excluded_restaurant_ids: list[int]
