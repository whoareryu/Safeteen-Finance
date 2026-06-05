from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FavoriteToggleCommand:
    store_id: int


@dataclass
class FavoriteCardQuery:
    user_id: int


@dataclass
class FavoriteCheckQuery:
    user_id: int
    store_ids: list[int]
