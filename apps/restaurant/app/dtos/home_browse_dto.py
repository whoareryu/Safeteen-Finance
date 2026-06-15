"""home_browse internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HomeBrowseQuery:
    id: int
    name: str


@dataclass(frozen=True)
class HomeBrowseResponse:
    id: int
    name: str
