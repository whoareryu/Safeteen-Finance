"""category_browse internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CategoryBrowseQuery:
    id: int
    name: str


@dataclass(frozen=True)
class CategoryBrowseResponse:
    id: int
    name: str
