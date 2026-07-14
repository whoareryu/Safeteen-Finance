from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class PlantCheckinEntity:
    id: int | None
    plant_id: int
    photo_url: str
    checkin_date: date
    health_score: float
    points_earned: int
    streak_day: int
    created_at: datetime | None = None
