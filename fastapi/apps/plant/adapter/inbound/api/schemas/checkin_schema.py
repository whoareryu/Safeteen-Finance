from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class CheckinResponse(BaseModel):
    id: int
    plant_id: int
    checkin_date: date
    health_score: float
    points_earned: int
    streak_day: int
    total_points: int
    growth_stage: str
    new_badges: list[str]


class CheckinHistoryItem(BaseModel):
    id: int
    photo_url: str
    checkin_date: date
    health_score: float
    points_earned: int
    streak_day: int
