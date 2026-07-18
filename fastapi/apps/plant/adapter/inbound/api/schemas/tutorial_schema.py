from __future__ import annotations

from pydantic import BaseModel


class TutorialCreateRequest(BaseModel):
    species_name: str
    region: str
    owner_user_id: int


class TutorialMoveLightRequest(BaseModel):
    light_position: str


class TutorialStateResponse(BaseModel):
    id: int
    owner_user_id: int
    species_name: str
    region: str
    growth_stage: str
    soil_moisture_pct: float
    nutrient_pct: float
    light_position: str
    points: int
    status: str
    photo_url: str
    feedback: str | None = None
