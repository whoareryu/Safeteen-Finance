"""topic_restaurants internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TopicRestaurantsQuery:
    id: int
    name: str


@dataclass(frozen=True)
class TopicRestaurantsResponse:
    id: int
    name: str
