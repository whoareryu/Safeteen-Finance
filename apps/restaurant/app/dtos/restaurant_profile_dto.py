"""restaurant_profile internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RestaurantProfileQuery:
    id: int
    name: str


@dataclass(frozen=True)
class RestaurantProfileResponse:
    id: int
    name: str
