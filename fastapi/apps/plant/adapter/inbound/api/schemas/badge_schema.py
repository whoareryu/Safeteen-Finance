from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class BadgeItemResponse(BaseModel):
    code: str
    name: str
    description: str
    icon: str
    earned: bool
    earned_at: datetime | None = None


class LeaderboardEntryResponse(BaseModel):
    rank: int
    plant_id: int
    nickname: str
    species_name: str
    points: int
    growth_stage: str
