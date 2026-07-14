from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from plant.domain.value_objects.growth_stage import SPROUT


@dataclass
class PlantEntity:
    id: int | None
    owner_user_id: int | None
    nickname: str
    species_name: str
    region: str
    growth_stage: str = SPROUT
    points: int = 0
    streak_count: int = 0
    last_checkin_date: date | None = None
    created_at: datetime | None = None
