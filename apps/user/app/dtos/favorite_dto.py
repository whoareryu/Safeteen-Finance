from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FavoriteToggleCommand:
    store_id: int


@dataclass(frozen=True)
class FavoriteCardQuery:
    user_id: int


@dataclass(frozen=True)
class FavoriteCheckQuery:
    user_id: int
    store_ids: list[int]


@dataclass(frozen=True)
class FavoriteResponse:
    id: int
    name: str
