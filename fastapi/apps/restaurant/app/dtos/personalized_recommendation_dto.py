from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PreferenceSnapshot:
    """user 앱 취향 데이터의 값 사본.

    스포크→스포크 직접 import 금지 규칙에 따라 restaurant 앱은 user ORM/DTO를
    import하지 않는다. 조합 지점(라우터/main.py)에서 이 스냅샷으로 변환해 주입한다.
    """

    genre_ranking: list[str] = field(default_factory=list)
    portion: str | None = None
    excluded_restaurant_ids: list[int] = field(default_factory=list)


@dataclass(frozen=True)
class PersonalizedQuery:
    """맥락(시간대·날씨) + 취향 스냅샷 기반 1곳 추천 (기획서 3-2, 4-1)."""

    preference: PreferenceSnapshot
    time_slot: str  # morning / lunch / dinner
    weather: str | None = None
    lat: float | None = None
    lng: float | None = None
    dining_mode: str | None = None  # dine_in / pickup / delivery


@dataclass(frozen=True)
class PersonalizedPick:
    """추천 1곳 — 카드 렌더에 필요한 값 일체."""

    id: int
    name: str
    genre: str
    road_address: str
    latitude: float | None
    longitude: float | None
    reason: str
