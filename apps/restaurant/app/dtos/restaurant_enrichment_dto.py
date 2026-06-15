"""restaurant_enrichment internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RestaurantEnrichmentQuery:
    id: int
    name: str


@dataclass(frozen=True)
class RestaurantEnrichmentResponse:
    id: int
    name: str
