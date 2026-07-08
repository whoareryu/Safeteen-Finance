"""restaurant_detail internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RestaurantDetailQuery:
    id: int
    name: str


@dataclass(frozen=True)
class RestaurantDetailResponse:
    id: int
    name: str
