"""daily_pick internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DailyPickQuery:
    id: int
    name: str


@dataclass(frozen=True)
class DailyPickResponse:
    id: int
    name: str
