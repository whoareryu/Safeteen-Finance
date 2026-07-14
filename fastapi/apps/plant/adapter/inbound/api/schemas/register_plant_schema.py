from __future__ import annotations

from pydantic import BaseModel


class MyPlantResponse(BaseModel):
    id: int
    nickname: str
    species_name: str
    region: str
    growth_stage: str
    points: int
    streak_count: int = 0
