"""restaurant_domain internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RestaurantDomainQuery:
    id: int
    name: str


@dataclass(frozen=True)
class RestaurantDomainResponse:
    id: int
    name: str
