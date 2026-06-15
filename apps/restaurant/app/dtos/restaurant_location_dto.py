"""restaurant_location internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RestaurantLocationQuery:
    id: int
    name: str


@dataclass(frozen=True)
class RestaurantLocationResponse:
    id: int
    name: str
