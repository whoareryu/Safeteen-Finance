from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CourseQuery:
    """커플/여행 하루 코스 질의 (기획서 3-4)."""

    district: str  # 지역(시군구/동) 검색어
    party_type: str = "couple"  # couple / travel


@dataclass(frozen=True)
class CourseStop:
    slot: str  # brunch / lunch / cafe / dinner / bar
    restaurant_id: int
    name: str


@dataclass(frozen=True)
class CourseView:
    district: str
    stops: list[CourseStop] = field(default_factory=list)
