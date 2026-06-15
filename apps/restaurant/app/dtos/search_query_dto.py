"""search_query internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchQueryQuery:
    id: int
    name: str


@dataclass(frozen=True)
class SearchQueryResponse:
    id: int
    name: str
