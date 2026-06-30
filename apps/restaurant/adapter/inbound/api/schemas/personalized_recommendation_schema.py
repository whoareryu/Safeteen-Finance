from __future__ import annotations

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """메인 홈 오늘의 추천 요청 (기획서 3-2)."""

    time_slot: str | None = None  # 미지정 시 서버가 KST로 판별
    weather: str | None = None
    excluded_ids: list[int] = Field(default_factory=list)  # "마음에 안 들어" 누적
    genre_ranking: list[str] = Field(default_factory=list)  # 온보딩 취향 (선택)
    lat: float | None = None  # 사용자 위치 (위도)
    lng: float | None = None  # 사용자 위치 (경도)
    dining_mode: str | None = None  # dine_in / pickup / delivery


class RecommendationCardResponse(BaseModel):
    id: int
    name: str
    genre: str
    road_address: str
    latitude: float | None
    longitude: float | None
    reason: str
    time_slot: str
