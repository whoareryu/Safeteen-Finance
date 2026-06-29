from __future__ import annotations

from pydantic import BaseModel, Field


class VisitConfirmRequest(BaseModel):
    """방문 확인 + 별점 (기획서 4-2)."""

    restaurant_id: int
    rating: int | None = Field(None, ge=1, le=5)
    latitude: float | None = None
    longitude: float | None = None


class VisitResponse(BaseModel):
    restaurant_id: int
    rating: int | None
    confirmed: bool
