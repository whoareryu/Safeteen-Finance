"""restaurant_browse internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RestaurantBrowseQuery:
    id: int
    name: str


@dataclass(frozen=True)
class RestaurantBrowseResponse:
    id: int
    name: str
