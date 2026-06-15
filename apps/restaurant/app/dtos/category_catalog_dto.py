"""category_catalog internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CategoryCatalogQuery:
    id: int
    name: str


@dataclass(frozen=True)
class CategoryCatalogResponse:
    id: int
    name: str
