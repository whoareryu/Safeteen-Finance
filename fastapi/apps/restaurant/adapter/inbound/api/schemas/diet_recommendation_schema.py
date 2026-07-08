from __future__ import annotations

from pydantic import BaseModel, Field


class DietRestaurant(BaseModel):
    id: int
    name: str
    genre: str
    road_address: str
    latitude: float | None
    longitude: float | None


class DietResponse(BaseModel):
    diet_type: str
    restaurants: list[DietRestaurant] = Field(default_factory=list)
