from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class CheckinCommand:
    plant_id: int
    photo_data: bytes
    photo_filename: str
    photo_content_type: str


@dataclass(frozen=True)
class CheckinResult:
    id: int
    plant_id: int
    checkin_date: date
    health_score: float
    points_earned: int
    streak_day: int
    total_points: int
    growth_stage: str
    new_badges: list[str] = field(default_factory=list)
