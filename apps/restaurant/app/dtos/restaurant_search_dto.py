"""restaurant_search internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RestaurantSearchQuery:
    id: int
    name: str


@dataclass(frozen=True)
class RestaurantSearchResponse:
    id: int
    name: str
