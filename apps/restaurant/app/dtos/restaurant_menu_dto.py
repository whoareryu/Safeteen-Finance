"""restaurant_menu internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RestaurantMenuQuery:
    id: int
    name: str


@dataclass(frozen=True)
class RestaurantMenuResponse:
    id: int
    name: str
