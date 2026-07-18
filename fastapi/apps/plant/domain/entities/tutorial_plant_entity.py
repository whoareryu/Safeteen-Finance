from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from plant.domain.value_objects.growth_stage import SPROUT
from plant.domain.value_objects.tutorial_state import LIGHT_PARTIAL


@dataclass
class TutorialPlantEntity:
    id: int | None
    owner_user_id: int
    species_name: str
    region: str
    growth_stage: str = SPROUT
    soil_moisture_pct: float = 70.0
    nutrient_pct: float = 70.0
    light_position: str = LIGHT_PARTIAL
    points: int = 0
    last_watered_at: datetime | None = None
    last_fertilized_at: datetime | None = None
    last_light_moved_at: datetime | None = None
    last_weather_sync_at: datetime | None = None
    created_at: datetime | None = None
