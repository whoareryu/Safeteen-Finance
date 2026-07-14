from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class PlantBadgeEntity:
    id: int
    code: str
    name: str
    description: str
    icon: str


@dataclass
class EarnedBadgeEntity:
    badge: PlantBadgeEntity
    earned_at: datetime | None = None
