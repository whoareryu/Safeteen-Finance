from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class PlantEntity:
    id: int | None
    owner_user_id: int | None
    nickname: str
    species_name: str
    region: str
    created_at: datetime | None = None
