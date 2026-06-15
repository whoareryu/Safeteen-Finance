"""today_picks internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TodayPicksQuery:
    id: int
    name: str


@dataclass(frozen=True)
class TodayPicksResponse:
    id: int
    name: str
