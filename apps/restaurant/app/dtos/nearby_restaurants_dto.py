"""nearby_restaurants internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NearbyRestaurantsQuery:
    id: int
    name: str


@dataclass(frozen=True)
class NearbyRestaurantsResponse:
    id: int
    name: str
