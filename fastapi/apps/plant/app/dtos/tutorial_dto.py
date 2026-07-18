from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TutorialCreateCommand:
    owner_user_id: int
    species_name: str
    region: str


@dataclass(frozen=True)
class TutorialMoveLightCommand:
    tutorial_plant_id: int
    light_position: str


@dataclass(frozen=True)
class TutorialStateResult:
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
