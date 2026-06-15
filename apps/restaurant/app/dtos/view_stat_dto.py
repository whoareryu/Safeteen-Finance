"""view_stat internal DTOs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ViewStatQuery:
    id: int
    name: str


@dataclass(frozen=True)
class ViewStatResponse:
    id: int
    name: str
