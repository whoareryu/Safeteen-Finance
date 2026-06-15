"""search_suggest internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchSuggestQuery:
    id: int
    name: str


@dataclass(frozen=True)
class SearchSuggestResponse:
    id: int
    name: str
